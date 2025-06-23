
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from base64 import b64encode, b64decode

from slixmpp.util import bytes
from slixmpp.xmlstream import ET, ElementBase, register_stanza_plugin


class Data(ElementBase):
    name = 'data'
    namespace = 'urn:xmpp:avatar:data'
    plugin_attrib = 'avatar_data'
    interfaces = {'value'}

    def get_value(self):
        if self.xml.text:
            return b64decode(bytes(self.xml.text))
        return b''

    def set_value(self, value):
        if value:
            self.xml.text = b64encode(bytes(value)).decode()
        else:
            self.xml.text = ''

    def del_value(self):
        self.xml.text = ''


class MetaData(ElementBase):
    name = 'metadata'
    namespace = 'urn:xmpp:avatar:metadata'
    plugin_attrib = 'avatar_metadata'
    interfaces = set()

    def add_info(self, id, itype, ibytes, height=None, width=None, url=None):
        info = Info()
        info.values = {'id': id,
                       'type': itype,
                       'bytes': '%s' % ibytes,
                       'height': height,
                       'width': width,
                       'url': url}
        self.append(info)

    def add_pointer(self, xml):
        if not isinstance(xml, Pointer):
            pointer = Pointer()
            pointer.append(xml)
            self.append(pointer)
        else:
            self.append(xml)


class Info(ElementBase):
    name = 'info'
    namespace = 'urn:xmpp:avatar:metadata'
    plugin_attrib = 'info'
    plugin_multi_attrib = 'items'
    interfaces = {'bytes', 'height', 'id', 'type', 'url', 'width'}

    def _get_int(self, name: str) -> int:
        try:
            return int(self._get_attr(name))
        except ValueError:
            return 0

    def _set_int(self, name: str, value: int):
        if value not in ('', None):
            int(value)
        self._set_attr(name, value)

    def get_bytes(self) -> int:
        return self._get_int('bytes')

    def _set_bytes(self, value: int):
        self._set_int('bytes', value)

    def get_height(self) -> int:
        return self._get_int('height')

    def set_height(self, value: int):
        self._set_int('height', value)

    def get_width(self) -> int:
        return self._get_int('width')

    def set_width(self, value: int):
        self._set_int('width', value)


class Pointer(ElementBase):
    name = 'pointer'
    namespace = 'urn:xmpp:avatar:metadata'
    plugin_attrib = 'pointer'
    plugin_multi_attrib = 'pointers'
    interfaces = set()


register_stanza_plugin(MetaData, Info, iterable=True)
register_stanza_plugin(MetaData, Pointer, iterable=True)
