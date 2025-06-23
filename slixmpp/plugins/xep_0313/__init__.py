
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permissio
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0313.stanza import Result, MAM, Metadata
from slixmpp.plugins.xep_0313.mam import XEP_0313


register_plugin(XEP_0313)

__all__ = ['XEP_0313', 'Result', 'MAM', 'Metadata']
