# Slixmpp: The Slick XMPP Library
# Copyright (C) 2021 Mathieu Pasquet
# This file is part of Slixmpp.
# See the file LICENSE for copying permissio
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0441.stanza import Preferences
from slixmpp.plugins.xep_0441.mam_prefs import XEP_0441


register_plugin(XEP_0441)

__all__ = ['XEP_0441', 'Preferences']
