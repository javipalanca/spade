from asyncio import Future

from slixmpp import Iq
from slixmpp.plugins import BasePlugin
from slixmpp.types import JidStr

from . import stanza
from ..xep_0004 import Form


class XEP_0490(BasePlugin):
    """
    XEP-0490: Message Displayed Synchronization
    """

    name = "xep_0490"
    description = "XEP-0490: Message Displayed Synchronization"
    dependencies = {"xep_0060", "xep_0163", "xep_0223", "xep_0359"}
    stanza = stanza

    def plugin_init(self):
        stanza.register_plugin()
        self.xmpp.plugin["xep_0163"].register_pep(
            "message_displayed_synchronization",
            stanza.Displayed,
        )
        self.xmpp.plugin["xep_0223"].node_profiles[self.stanza.NS] = {
            "pubsub#max_items": "max",
            "pubsub#send_last_published_item": "never",
        }

    def flag_chat(self, chat: JidStr, stanza_id: str, **kwargs) -> Future[Iq]:
        displayed = stanza.Displayed()
        displayed["stanza_id"]["id"] = stanza_id
        return self.xmpp.plugin["xep_0223"].store(
            displayed, node=stanza.NS, id=str(chat), **kwargs
        )

    def catch_up(self, **kwargs):
        return self.xmpp.plugin["xep_0060"].get_items(
            self.xmpp.boundjid.bare, stanza.NS, **kwargs
        )
