
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2013 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import datetime as dt

from slixmpp.xmlstream import ElementBase, register_stanza_plugin
from slixmpp.plugins import xep_0082


class File(ElementBase):
    name = 'file'
    namespace = 'http://jabber.org/protocol/si/profile/file-transfer'
    plugin_attrib = 'file'
    interfaces = {'name', 'size', 'date', 'hash', 'desc'}
    sub_interfaces = {'desc'}

    def set_size(self, value):
        self._set_attr('size', str(value))

    def get_date(self):
        timestamp = self._get_attr('date')
        return xep_0082.parse(timestamp)

    def set_date(self, value):
        if isinstance(value, dt.datetime):
            value = xep_0082.format_datetime(value)
        self._set_attr('date', value)


class Range(ElementBase):
    name = 'range'
    namespace = 'http://jabber.org/protocol/si/profile/file-transfer'
    plugin_attrib = 'range'
    interfaces = {'length', 'offset'}

    def set_length(self, value):
        self._set_attr('length', str(value))

    def set_offset(self, value):
        self._set_attr('offset', str(value))


register_stanza_plugin(File, Range)
