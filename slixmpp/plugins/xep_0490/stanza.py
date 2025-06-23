from slixmpp import register_stanza_plugin
from slixmpp.plugins.xep_0060.stanza import Item
from slixmpp.xmlstream import ElementBase
from slixmpp.plugins.xep_0359.stanza import StanzaID

NS = "urn:xmpp:mds:displayed:0"


class Displayed(ElementBase):
    namespace = NS
    name = "displayed"
    plugin_attrib = "displayed"


def register_plugin():
    register_stanza_plugin(Displayed, StanzaID)
    register_stanza_plugin(Item, Displayed)
