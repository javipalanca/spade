import asyncio
import logging
from functools import partial
import typing

from slixmpp import Message, Iq, Presence, JID
from slixmpp.xmlstream.handler import Callback
from slixmpp.xmlstream.matcher import StanzaPath
from slixmpp.plugins import BasePlugin


class XEP_0100(BasePlugin):

    """
    XEP-0100: Gateway interaction

    Does not cover the deprecated Agent Information and 'jabber:iq:gateway' protocols

    Events registered by this plugin:

    - legacy_login: Jabber user got online or just registered
    - legacy_logout: Jabber user got offline or just unregistered
    - legacy_presence_unavailable: Jabber user sent an unavailable presence to a legacy contact
    - gateway_message: Jabber user sent a direct message to the gateway component
    - legacy_message: Jabber user sent a message to the legacy network


    Plugin Parameters:

    - `component_name`: (str) Name of the entity
    - `type`: (str) Type of the gateway identity. Should be the name of the legacy service
    - `needs_registration`: (bool) If set to True, messages received from unregistered users will
      not be transmitted to the legacy service

    API:

    - legacy_contact_add(jid, node, ifrom: JID, args: JID): Add contact on the legacy service.
      Should raise LegacyError if anything goes wrong in the process.
      `ifrom` is the gateway user's JID and `args` is the legacy contact's JID.
    - legacy_contact_remove(jid, node, ifrom: JID, args: JID): Remove a contact.

    """

    name = "xep_0100"
    description = "XEP-0100: Gateway interaction"
    dependencies = {
        "xep_0030",  # Service discovery
        "xep_0077",  # In band registration
    }

    default_config = {
        "component_name": "SliXMPP gateway",
        "type": "xmpp",
        "needs_registration": True,
    }

    def plugin_init(self):
        if not self.xmpp.is_component:
            log.error("Only components can be gateways, aborting plugin load")
            return

        self.xmpp["xep_0030"].add_identity(
            name=self.component_name, category="gateway", itype=self.type
        )

        self.api.register(self._legacy_contact_remove, "legacy_contact_remove")
        self.api.register(self._legacy_contact_add, "legacy_contact_add")

        # Without that BaseXMPP sends unsub/unavailable on sub requests and we don't want that
        self.xmpp.client_roster.auto_authorize = True
        self.xmpp.client_roster.auto_subscribe = False

        self.xmpp.add_event_handler("user_register", self.on_user_register)
        self.xmpp.add_event_handler("user_unregister", self.on_user_unregister)
        self.xmpp.add_event_handler("presence_available", self.on_presence_available)
        self.xmpp.add_event_handler(
            "presence_unavailable", self.on_presence_unavailable
        )
        self.xmpp.add_event_handler("presence_subscribe", self.on_presence_subscribe)
        self.xmpp.add_event_handler(
            "presence_unsubscribe", self.on_presence_unsubscribe
        )
        self.xmpp.add_event_handler("message", self.on_message)

    def plugin_end(self):
        if not self.xmpp.is_component:
            return

        self.xmpp.del_event_handler("user_register", self.on_user_register)
        self.xmpp.del_event_handler("user_unregister", self.on_user_unregister)
        self.xmpp.del_event_handler("presence_available", self.on_presence_available)
        self.xmpp.del_event_handler(
            "presence_unavailable", self.on_presence_unavailable
        )
        self.xmpp.del_event_handler("presence_subscribe", self.on_presence_subscribe)
        self.xmpp.del_event_handler("message", self.on_message)
        self.xmpp.del_event_handler(
            "presence_unsubscribe", self.on_presence_unsubscribe
        )

    async def get_user(self, stanza):
        return await self.xmpp["xep_0077"].api["user_get"](None, None, None, stanza)

    def send_presence(self, pto, ptype=None, pstatus=None, pfrom=None):
        self.xmpp.send_presence(
            pfrom=self.xmpp.boundjid.bare,
            ptype=ptype,
            pto=pto,
            pstatus=pstatus,
        )

    async def on_user_register(self, iq: Iq):
        user_jid = iq["from"]
        user = await self.get_user(iq)
        if user is None:  # This should not happen
            log.warning(f"{user_jid} has registered but cannot find them in user store")
        else:
            log.debug(f"Sending subscription request to {user_jid}")
            self.xmpp.client_roster.subscribe(user_jid)

    def on_user_unregister(self, iq: Iq):
        user_jid = iq["from"]
        log.debug(f"Sending subscription request to {user_jid}")
        self.xmpp.event("legacy_logout", iq)
        self.xmpp.client_roster.unsubscribe(iq["from"])
        self.xmpp.client_roster.remove(iq["from"])
        log.debug(f"roster: {self.xmpp.client_roster}")

    async def on_presence_available(self, presence: Presence):
        user_jid = presence["from"]
        user = await self.get_user(presence)
        if user is None:
            log.warning(
                f"{user_jid} has gotten online but cannot find them in user store"
            )
        else:
            self.xmpp.event("legacy_login", presence)
            log.debug(f"roster: {self.xmpp.client_roster}")
            self.send_presence(pto=user_jid.bare, ptype="available")

    async def on_presence_unavailable(self, presence: Presence):
        user_jid = presence["from"]
        user = await self.get_user(presence)
        if user is None:  # This should not happen
            log.warning(
                f"{user_jid} has gotten offline but but cannot find them in user store"
            )
            return

        if presence["to"] == self.xmpp.boundjid.bare:
            self.xmpp.event("legacy_logout", presence)
            self.send_presence(pto=user_jid, ptype="unavailable")
        else:
            self.xmpp.event("legacy_presence_unavailable", presence)

    async def _legacy_contact_add(self, jid, node, ifrom, contact_jid: JID):
        pass

    async def on_presence_subscribe(self, presence: Presence):
        user_jid = presence["from"]
        user = await self.get_user(presence)
        if user is None and self.needs_registration:
            return

        if presence["to"] == self.xmpp.boundjid.bare:
            return

        try:
            await self.api["legacy_contact_add"](
                ifrom=user_jid,
                args=presence["to"],
            )
        except LegacyError:
            self.xmpp.send_presence(
                pfrom=presence["to"],
                ptype="unsubscribed",
                pto=user_jid,
            )
            return
        self.xmpp.send_presence(
            pfrom=presence["to"],
            ptype="subscribed",
            pto=user_jid,
        )
        self.xmpp.send_presence(
            pfrom=presence["to"],
            pto=user_jid,
        )
        self.xmpp.send_presence(
            pfrom=presence["to"],
            ptype="subscribe",
            pto=user_jid,
        )  # TODO: handle resulting subscribed presences

    async def on_presence_unsubscribe(self, presence: Presence):
        if presence["to"] == self.xmpp.boundjid.bare:
            # should we trigger unregistering here?
            return

        user_jid = presence["from"]
        user = await self.get_user(presence)
        if user is None:
            log.debug("Received remove subscription from unregistered user")
            if self.needs_registration:
                return

        await self.api["legacy_contact_remove"](ifrom=user_jid, args=presence["to"])

        for ptype in "unsubscribe", "unsubscribed", "unavailable":
            self.xmpp.send_presence(
                pfrom=presence["to"],
                ptype=ptype,
                pto=user_jid,
            )

    async def _legacy_contact_remove(self, jid, node, ifrom, contact_jid: JID):
        pass

    async def on_message(self, msg: Message):
        if msg["type"] == "groupchat":
            return  # groupchat messages are out of scope of XEP-0100

        if msg["to"] == self.xmpp.boundjid.bare:
            # It may be useful to exchange direct messages with the component
            self.xmpp.event("gateway_message", msg)
            return

        if self.needs_registration and await self.get_user(msg) is None:
            return

        self.xmpp.event("legacy_message", msg)

    def transform_legacy_message(
        self,
        jabber_user_jid: typing.Union[JID, str],
        legacy_contact_id: str,
        body: str,
        mtype: typing.Optional[str] = None,
    ):
        """
        Transform a legacy message to an XMPP message
        """
        # Should escaping legacy IDs to valid JID local parts be handled here?
        # Maybe by internal API stuff?
        self.xmpp.send_message(
            mfrom=JID(f"{legacy_contact_id}@{self.xmpp.boundjid.bare}"),
            mto=JID(jabber_user_jid).bare,
            mbody=body,
            mtype=mtype,
        )


class LegacyError(Exception):
    pass


log = logging.getLogger(__name__)
