from slixmpp.xmlstream import ElementBase

NAMESPACE = "urn:xmpp:reference:0"


class Reference(ElementBase):
    name = plugin_attrib = "reference"
    namespace = NAMESPACE
    interfaces = {"type", "uri", "id", "begin", "end"}
