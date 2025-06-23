
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2011 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.xmlstream import ElementBase


class OOBTransfer(ElementBase):

    """
    """

    name = 'query'
    namespace = 'jabber:iq:oob'
    plugin_attrib = 'oob_transfer'
    interfaces = {'url', 'desc', 'sid'}
    sub_interfaces = {'url', 'desc'}


class OOB(ElementBase):

    """
    """

    name = 'x'
    namespace = 'jabber:x:oob'
    plugin_attrib = 'oob'
    interfaces = {'url', 'desc'}
    sub_interfaces = interfaces
