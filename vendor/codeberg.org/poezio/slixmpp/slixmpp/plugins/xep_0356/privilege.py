import logging
import typing
import uuid
from collections import defaultdict

from slixmpp import JID, Iq, Message
from slixmpp.plugins.base import BasePlugin
from slixmpp.xmlstream import StanzaBase
from slixmpp.xmlstream.handler import Callback
from slixmpp.xmlstream.matcher import StanzaPath

from . import stanza
from .permissions import IqPermission, MessagePermission, Permissions, RosterAccess

log = logging.getLogger(__name__)


class XEP_0356(BasePlugin):
    """
    XEP-0356: Privileged Entity

    Events:

    ::

        privileges_advertised  -- Received message/privilege from the server
    """

    name = "xep_0356"
    description = "XEP-0356: Privileged Entity"
    dependencies = {"xep_0297"}
    stanza = stanza

    granted_privileges = defaultdict(Permissions)

    def plugin_init(self):
        if not self.xmpp.is_component:
            log.error("XEP 0356 is only available for components")
            return

        stanza.register()

        self.xmpp.register_handler(
            Callback(
                "Privileges",
                StanzaPath("message/privilege"),
                self._handle_privilege,
            )
        )

    def plugin_end(self):
        self.xmpp.remove_handler("Privileges")

    def _handle_privilege(self, msg: StanzaBase):
        """
        Called when the XMPP server advertise the component's privileges.

        Stores the privileges in this instance's granted_privileges attribute (a dict)
        and raises the privileges_advertised event
        """
        permissions = self.granted_privileges[msg.get_from()]
        for perm in msg["privilege"]["perms"]:
            access = perm["access"]
            if access == "iq":
                for ns in perm["namespaces"]:
                    permissions.iq[ns["ns"]] = ns["type"]
            elif access in _VALID_ACCESSES:
                setattr(permissions, access, perm["type"])
            else:
                log.warning("Received an invalid privileged access: %s", access)
        log.debug(f"Privileges: {self.granted_privileges}")
        self.xmpp.event("privileges_advertised")

    def send_privileged_message(self, msg: Message):
        if (
            self.granted_privileges[msg.get_from().domain].message
            != MessagePermission.OUTGOING
        ):
            raise PermissionError(
                "The server hasn't authorized us to send messages on behalf of other users"
            )
        else:
            self._make_privileged_message(msg).send()

    def _make_privileged_message(self, msg: Message):
        server = msg.get_from().domain
        wrapped = self.xmpp.make_message(mto=server, mfrom=self.xmpp.boundjid.bare)
        wrapped["privilege"]["forwarded"].append(msg)
        return wrapped

    def _make_get_roster(self, jid: typing.Union[JID, str], **iq_kwargs):
        return self.xmpp.make_iq_get(
            queryxmlns="jabber:iq:roster",
            ifrom=self.xmpp.boundjid.bare,
            ito=jid,
            **iq_kwargs,
        )

    def _make_set_roster(
        self,
        jid: typing.Union[JID, str],
        roster_items: dict,
        **iq_kwargs,
    ):
        iq = self.xmpp.make_iq_set(
            ifrom=self.xmpp.boundjid.bare,
            ito=jid,
            **iq_kwargs,
        )
        iq["roster"]["items"] = roster_items
        return iq

    async def get_roster(self, jid: typing.Union[JID, str], **send_kwargs) -> Iq:
        """
        Return the roster of user on the server the component has privileged access to.

        Raises ValueError if the server did not advertise the corresponding privileges

        :param jid: user we want to fetch the roster from
        """
        if isinstance(jid, str):
            jid = JID(jid)
        if self.granted_privileges[jid.domain].roster not in (
            RosterAccess.GET,
            RosterAccess.BOTH,
        ):
            raise PermissionError(
                "The server did not grant us privileges to get rosters"
            )
        else:
            return await self._make_get_roster(jid).send(**send_kwargs)

    async def set_roster(
        self, jid: typing.Union[JID, str], roster_items: dict, **send_kwargs
    ) -> Iq:
        """
        Return the roster of user on the server the component has privileged access to.

        Raises ValueError if the server did not advertise the corresponding privileges

        Here is an example of a roster_items value:

        .. code-block:: json

            {
                "friend1@example.com": {
                    "name": "Friend 1",
                    "subscription": "both",
                    "groups": ["group1", "group2"],
                },
                "friend2@example.com": {
                    "name": "Friend 2",
                    "subscription": "from",
                    "groups": ["group3"],
                },
            }

        :param jid: user we want to add or modify roster items
        :param roster_items: a dict containing the roster items' JIDs as keys and
                             nested dicts containing names, subscriptions and groups.

        """
        if isinstance(jid, str):
            jid = JID(jid)
        if self.granted_privileges[jid.domain].roster not in (
            RosterAccess.GET,
            RosterAccess.BOTH,
        ):
            raise PermissionError(
                "The server did not grant us privileges to set rosters"
            )
        else:
            return await self._make_set_roster(jid, roster_items).send(**send_kwargs)

    async def send_privileged_iq(
        self, encapsulated_iq: Iq, iq_id: typing.Optional[str] = None
    ):
        """
        Send an IQ on behalf of a user

        Caution: the IQ *must* have the jabber:client namespace
        """
        iq_id = iq_id or str(uuid.uuid4())
        encapsulated_iq["id"] = iq_id
        server = encapsulated_iq.get_to().domain
        perms = self.granted_privileges.get(server)
        if not perms:
            raise PermissionError(f"{server} has not granted us any privilege")
        itype = encapsulated_iq["type"]
        for ns in encapsulated_iq.plugins.values():
            type_ = perms.iq[ns.namespace]
            if type_ == IqPermission.NONE:
                raise PermissionError(
                    f"{server} has not granted any IQ privilege for namespace {ns.namespace}"
                )
            elif type_ == IqPermission.BOTH:
                pass
            elif type_ != itype:
                raise PermissionError(
                    f"{server} has not granted IQ {itype} privilege for namespace {ns.namespace}"
                )
        iq = self.xmpp.make_iq(
            itype=itype,
            ifrom=self.xmpp.boundjid.bare,
            ito=encapsulated_iq.get_from(),
            id=iq_id,
        )
        iq["privileged_iq"].append(encapsulated_iq)

        resp = await iq.send()
        return resp["privilege"]["forwarded"]["iq"]


# does not include iq access that is handled differently
_VALID_ACCESSES = {"message", "roster", "presence"}
