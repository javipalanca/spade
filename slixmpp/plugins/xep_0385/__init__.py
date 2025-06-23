
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission
from slixmpp.plugins.base import register_plugin

from . import stanza
from .sims import XEP_0385

register_plugin(XEP_0385)
