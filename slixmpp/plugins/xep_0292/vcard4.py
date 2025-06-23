import logging
from datetime import date
from typing import Optional

from slixmpp import (
    JID,
    ComponentXMPP,
    register_stanza_plugin,
)
from slixmpp.plugins.base import BasePlugin

from . import stanza


class XEP_0292(BasePlugin):
    """
    vCard4 over XMPP

    Does not implement the IQ semantics that neither movim does gajim implement,
    cf https://xmpp.org/extensions/xep-0292.html#self-iq-retrieval and
    https://xmpp.org/extensions/xep-0292.html#self-iq-publication

    Does not implement the "empty pubsub event item" as a notification mechanism,
    that neither gajim nor movim implement
    https://xmpp.org/extensions/xep-0292.html#sect-idm45744791178720

    Relies on classic pubsub semantics instead.
    """
    xmpp: ComponentXMPP

    name = "xep_0292"
    description = "vCard4 Over XMPP"
    dependencies = {"xep_0163", "xep_0060", "xep_0030"}
    stanza = stanza

    def plugin_init(self):
        pubsub_stanza = self.xmpp["xep_0060"].stanza

        register_stanza_plugin(pubsub_stanza.Item, stanza.VCard4)
        register_stanza_plugin(pubsub_stanza.EventItem, stanza.VCard4)

        self.xmpp['xep_0060'].map_node_event(stanza.NS, 'vcard4')

    def plugin_end(self):
        self.xmpp['xep_0030'].del_feature(feature=stanza.NS)
        self.xmpp['xep_0163'].remove_interest(stanza.NS)

    def session_bind(self, jid):
        self.xmpp['xep_0163'].register_pep('vcard4', stanza.VCard4)

    def publish_vcard(
        self,
        full_name: Optional[str] = None,
        given: Optional[str] = None,
        surname: Optional[str] = None,
        birthday: Optional[date] = None,
        nickname: Optional[str] = None,
        phone: Optional[str] = None,
        note: Optional[str] = None,
        url: Optional[str] = None,
        email: Optional[str] = None,
        country: Optional[str] = None,
        locality: Optional[str] = None,
        impp: Optional[str] = None,
        **pubsubkwargs,
    ):
        """
        Publish a vcard using PEP
        """
        vcard = stanza.VCard4()

        if impp:
            vcard.add_impp(impp)

        if nickname:
            vcard.add_nickname(nickname)
        if full_name:
            vcard["full_name"] = full_name

        if given:
            vcard["given"] = given
        if surname:
            vcard["surname"] = surname
        if birthday:
            vcard["birthday"] = birthday

        if note:
            vcard.add_note(note)
        if url:
            vcard.add_url(url)
        if email:
            vcard.add_email(email)
        if phone:
            vcard.add_tel(phone)
        if country and locality:
            vcard.add_address(country, locality)
        elif country:
            vcard.add_address(country, locality)

        return self.xmpp["xep_0163"].publish(vcard, id="current", **pubsubkwargs)

    def retrieve_vcard(self, jid: JID, **pubsubkwargs):
        """
        Retrieve a vcard using PEP
        """
        return self.xmpp["xep_0060"].get_item(
            jid, stanza.VCard4.namespace, "current", **pubsubkwargs
        )


log = logging.getLogger(__name__)
