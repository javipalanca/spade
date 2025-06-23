# Slixmpp: The Slick XMPP Library
# This file is part of Slixmpp
# See the file LICENSE for copying permission
import re
import base64

from slixmpp.util import bytes
from slixmpp.exceptions import XMPPError
from slixmpp.xmlstream import ElementBase


VALID_B64 = re.compile(r'[A-Za-z0-9\+\/]*=*')


def to_b64(data):
    return bytes(base64.b64encode(bytes(data))).decode('utf-8')


def from_b64(data):
    return bytes(base64.b64decode(bytes(data)))


class Open(ElementBase):
    name = 'open'
    namespace = 'http://jabber.org/protocol/ibb'
    plugin_attrib = 'ibb_open'
    interfaces = {'block_size', 'sid', 'stanza'}

    def get_block_size(self):
        return int(self._get_attr('block-size', '0'))

    def set_block_size(self, value):
        self._set_attr('block-size', str(value))

    def del_block_size(self):
        self._del_attr('block-size')


class Data(ElementBase):
    name = 'data'
    namespace = 'http://jabber.org/protocol/ibb'
    plugin_attrib = 'ibb_data'
    interfaces = {'seq', 'sid', 'data'}
    sub_interfaces = {'data'}

    def get_seq(self):
        return int(self._get_attr('seq', '0'))

    def set_seq(self, value):
        self._set_attr('seq', str(value))

    def get_data(self):
        text = self.xml.text
        if not text:
            raise XMPPError('not-acceptable', 'IBB data element is empty.')
        b64_data = text.strip()
        if VALID_B64.match(b64_data).group() == b64_data:
            return from_b64(b64_data)
        else:
            raise XMPPError('not-acceptable')

    def set_data(self, value):
        self.xml.text = to_b64(value)

    def del_data(self):
        self.xml.text = ''


class Close(ElementBase):
    name = 'close'
    namespace = 'http://jabber.org/protocol/ibb'
    plugin_attrib = 'ibb_close'
    interfaces = {'sid'}
