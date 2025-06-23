
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2010  Nathanael C. Fritz
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import logging
from os import getenv

# Use defusedxml if wanted
# Since enabling it can have adverse consequences for the programs using
# slixmpp, do not enable it by default.
if  getenv('SLIXMPP_ENABLE_DEFUSEDXML', default='false').lower() == 'true':
    try:
        import defusedxml
        defusedxml.defuse_stdlib()
    except ImportError:
        pass

from slixmpp.stanza import Message, Presence, Iq
from slixmpp.jid import JID, InvalidJID
from slixmpp.xmlstream.stanzabase import ET, ElementBase, register_stanza_plugin
from slixmpp.xmlstream.handler import *
from slixmpp.xmlstream import XMLStream
from slixmpp.xmlstream.matcher import *
from slixmpp.basexmpp import BaseXMPP
from slixmpp.clientxmpp import ClientXMPP
from slixmpp.componentxmpp import ComponentXMPP

from slixmpp.version import __version__, __version_info__

__all__ = [
    'Message', 'Presence', 'Iq', 'JID', 'InvalidJID', 'ET', 'ElementBase',
    'register_stanza_plugin', 'XMLStream', 'BaseXMPP', 'ClientXMPP', 'ComponentXMPP',
    '__version__', '__version_info__'
]
