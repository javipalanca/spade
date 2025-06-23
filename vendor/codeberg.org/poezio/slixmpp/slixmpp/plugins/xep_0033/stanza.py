
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.xmlstream import JID, ElementBase, ET, register_stanza_plugin


class Addresses(ElementBase):

    name = 'addresses'
    namespace = 'http://jabber.org/protocol/address'
    plugin_attrib = 'addresses'
    interfaces = set()

    def add_address(self, atype='to', jid='', node='', uri='',
                          desc='', delivered=False):
        addr = Address(parent=self)
        addr['type'] = atype
        addr['jid'] = jid
        addr['node'] = node
        addr['uri'] = uri
        addr['desc'] = desc
        addr['delivered'] = delivered

        return addr

    # Additional methods for manipulating sets of addresses
    # based on type are generated below.


class Address(ElementBase):

    name = 'address'
    namespace = 'http://jabber.org/protocol/address'
    plugin_attrib = 'address'
    interfaces = {'type', 'jid', 'node', 'uri', 'desc', 'delivered'}

    address_types = {'bcc', 'cc', 'noreply', 'replyroom', 'replyto', 'to'}

    def get_jid(self):
        return JID(self._get_attr('jid'))

    def set_jid(self, value):
        self._set_attr('jid', str(value))

    def get_delivered(self):
        value = self._get_attr('delivered', False)
        return value and value.lower() in ('true', '1')

    def set_delivered(self, delivered):
        if delivered:
            self._set_attr('delivered', 'true')
        else:
            del self['delivered']

    def set_uri(self, uri):
        if uri:
            del self['jid']
            del self['node']
            self._set_attr('uri', uri)
        else:
            self._del_attr('uri')


# =====================================================================
# Auto-generate address type filters for the Addresses class.

def _addr_filter(atype):
    def _type_filter(addr):
        if isinstance(addr, Address):
            if atype == 'all' or addr['type'] == atype:
                return True
        return False
    return _type_filter


def _build_methods(atype):

    def get_multi(self):
        return list(filter(_addr_filter(atype), self))

    def set_multi(self, value):
        del self[atype]
        for addr in value:

            # Support assigning dictionary versions of addresses
            # instead of full Address objects.
            if not isinstance(addr, Address):
                if atype != 'all':
                    addr['type'] = atype
                elif 'atype' in addr and 'type' not in addr:
                    addr['type'] = addr['atype']
                addrObj = Address()
                addrObj.values = addr
                addr = addrObj

            self.append(addr)

    def del_multi(self):
        res = list(filter(_addr_filter(atype), self))
        for addr in res:
            self.iterables.remove(addr)
            self.xml.remove(addr.xml)

    return get_multi, set_multi, del_multi


for atype in ('all', 'bcc', 'cc', 'noreply', 'replyroom', 'replyto', 'to'):
    get_multi, set_multi, del_multi = _build_methods(atype)

    Addresses.interfaces.add(atype)
    setattr(Addresses, "get_%s" % atype, get_multi)
    setattr(Addresses, "set_%s" % atype, set_multi)
    setattr(Addresses, "del_%s" % atype, del_multi)

    if atype == 'all':
        Addresses.interfaces.add('addresses')
        setattr(Addresses, "get_addresses", get_multi)
        setattr(Addresses, "set_addresses", set_multi)
        setattr(Addresses, "del_addresses", del_multi)



register_stanza_plugin(Addresses, Address, iterable=True)
