
# Slixmpp: The Slick XMPP Library
# Implementation of HTTP over XMPP transport
# http://xmpp.org/extensions/xep-0332.html
# Copyright (C) 2015 Riptide IO, sangeeth@riptideio.com
# This file is part of slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0332 import stanza
from slixmpp.plugins.xep_0332.http import XEP_0332


register_plugin(XEP_0332)
