from slixmpp.jid import JID
from slixmpp.xmlstream import ElementBase, register_stanza_plugin


class Socks5(ElementBase):
    name = 'query'
    namespace = 'http://jabber.org/protocol/bytestreams'
    plugin_attrib = 'socks'
    interfaces = {'sid', 'activate'}
    sub_interfaces = {'activate'}

    def add_streamhost(self, jid, host, port):
        sh = StreamHost(parent=self)
        sh['jid'] = jid
        sh['host'] = host
        sh['port'] = port


class StreamHost(ElementBase):
    name = 'streamhost'
    namespace = 'http://jabber.org/protocol/bytestreams'
    plugin_attrib = 'streamhost'
    plugin_multi_attrib = 'streamhosts'
    interfaces = {'host', 'jid', 'port'}

    def set_jid(self, value):
        return self._set_attr('jid', str(value))

    def get_jid(self):
        return JID(self._get_attr('jid'))


class StreamHostUsed(ElementBase):
    name = 'streamhost-used'
    namespace = 'http://jabber.org/protocol/bytestreams'
    plugin_attrib = 'streamhost_used'
    interfaces = {'jid'}

    def set_jid(self, value):
        return self._set_attr('jid', str(value))

    def get_jid(self):
        return JID(self._get_attr('jid'))


register_stanza_plugin(Socks5, StreamHost, iterable=True)
register_stanza_plugin(Socks5, StreamHostUsed)
