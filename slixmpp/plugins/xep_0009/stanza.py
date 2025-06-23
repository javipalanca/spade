
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2011 Nathanael C. Fritz, Dann Martens (TOMOTON).
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.xmlstream.stanzabase import ElementBase
from xml.etree import ElementTree as ET


class RPCQuery(ElementBase):
    name = 'query'
    namespace = 'jabber:iq:rpc'
    plugin_attrib = 'rpc_query'


class MethodCall(ElementBase):
    name = 'methodCall'
    namespace = 'jabber:iq:rpc'
    plugin_attrib = 'method_call'
    interfaces = {'method_name', 'params'}

    def get_method_name(self):
        return self._get_sub_text('methodName')

    def set_method_name(self, value):
        return self._set_sub_text('methodName', value)

    def get_params(self):
        return self.xml.find('{%s}params' % self.namespace)

    def set_params(self, params):
        self.append(params)


class MethodResponse(ElementBase):
    name = 'methodResponse'
    namespace = 'jabber:iq:rpc'
    plugin_attrib = 'method_response'
    interfaces = {'params', 'fault'}

    def get_params(self):
        return self.xml.find('{%s}params' % self.namespace)

    def set_params(self, params):
        self.append(params)

    def get_fault(self) -> ET:
        return self.xml.find('{%s}fault' % self.namespace)

    def set_fault(self, fault: ET) -> None:
        self.append(fault)
