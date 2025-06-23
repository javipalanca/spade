from slixmpp.xmlstream import ElementBase

NAMESPACE = "urn:xmpp:sims:1"


class Sims(ElementBase):
    name = "media-sharing"
    plugin_attrib = "sims"
    namespace = NAMESPACE


class Sources(ElementBase):
    name = plugin_attrib = "sources"
    namespace = NAMESPACE
