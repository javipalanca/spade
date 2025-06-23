# Slixmpp: The Slick XMPP Library
# Copyright (C) 2025 nicoco
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.

from slixmpp.plugins.base import register_plugin

from . import stanza
from .notify import XEP_0492

register_plugin(XEP_0492)

__all__ = ["stanza", "XEP_0492"]
