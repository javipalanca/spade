
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2010 Nathanael C. Fritz, Erik Reuterborg Larsson
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.xmlstream import ElementBase, ET
from slixmpp.plugins.xep_0030.stanza.items import DiscoItems


class Set(ElementBase):

    """
    XEP-0059 (Result Set Management) can be used to manage the
    results of queries. For example, limiting the number of items
    per response or starting at certain positions.

    Example set stanzas:
    ::

        <iq type="get">
          <query xmlns="http://jabber.org/protocol/disco#items">
            <set xmlns="http://jabber.org/protocol/rsm">
              <max>2</max>
            </set>
          </query>
        </iq>

        <iq type="result">
          <query xmlns="http://jabber.org/protocol/disco#items">
            <item jid="conference.example.com" />
            <item jid="pubsub.example.com" />
            <set xmlns="http://jabber.org/protocol/rsm">
              <first>conference.example.com</first>
              <last>pubsub.example.com</last>
            </set>
          </query>
        </iq>

    Stanza Interface:
    ::

        first_index -- The index attribute of <first>
        after       -- The id defining from which item to start
        before      -- The id defining from which item to
                       start when browsing backwards
        max         -- Max amount per response
        first       -- Id for the first item in the response
        last        -- Id for the last item in the response
        index       -- Used to set an index to start from
        count       -- The number of remote items available


    """
    namespace = 'http://jabber.org/protocol/rsm'
    name = 'set'
    plugin_attrib = 'rsm'
    sub_interfaces = {'first', 'after', 'before', 'count',
                      'index', 'last', 'max'}
    interfaces = {'first_index', 'first', 'after', 'before',
                  'count', 'index', 'last', 'max'}

    def set_first_index(self, val):
        """
        Sets the index attribute for <first> and
        creates the element if it doesn't exist
        """
        fi = self.xml.find("{%s}first" % (self.namespace))
        if fi is not None:
            if val:
                fi.attrib['index'] = val
            elif 'index' in fi.attrib:
                del fi.attrib['index']
        elif val:
            fi = ET.Element("{%s}first" % (self.namespace))
            fi.attrib['index'] = val
            self.xml.append(fi)

    def get_first_index(self):
        """
        Returns the value of the index attribute for <first>
        """
        fi = self.xml.find("{%s}first" % (self.namespace))
        if fi is not None:
            return fi.attrib.get('index', '')

    def del_first_index(self):
        """
        Removes the index attribute for <first> but keeps the element
        """
        fi = self.xml.find("{%s}first" % (self.namespace))
        if fi is not None:
            del fi.attrib['index']

    def set_before(self, val):
        """
        Sets the value of <before>, if the value is True
        then the element will be created without a value
        """
        b = self.xml.find("{%s}before" % (self.namespace))
        if b is None and val is True:
            self._set_sub_text('{%s}before' % self.namespace, '', True)
        else:
            self._set_sub_text('{%s}before' % self.namespace, val)

    def get_before(self):
        """
        Returns the value of <before>, if it is
        empty it will return True
        """
        b = self.xml.find("{%s}before" % (self.namespace))
        if b is not None and not b.text:
            return True
        elif b is not None:
            return b.text
        else:
            return None
