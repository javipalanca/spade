from slixmpp.xmlstream import ElementBase

NAMESPACE = "urn:xmpp:sfs:0"


class StatelessFileSharing(ElementBase):
    name = "file-sharing"
    plugin_attrib = "sfs"
    namespace = NAMESPACE
    interfaces = {"disposition"}


class Sources(ElementBase):
    name = plugin_attrib = "sources"
    namespace = NAMESPACE


class UrlData(ElementBase):
    name = plugin_attrib = "url-data"
    namespace = "http://jabber.org/protocol/url-data"
    interfaces = {"target"}
