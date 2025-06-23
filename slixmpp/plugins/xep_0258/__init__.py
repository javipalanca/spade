
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2010 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0258 import stanza
from slixmpp.plugins.xep_0258.stanza import SecurityLabel, Label
from slixmpp.plugins.xep_0258.stanza import DisplayMarking, EquivalentLabel
from slixmpp.plugins.xep_0258.stanza import ESSLabel, Catalog, CatalogItem
from slixmpp.plugins.xep_0258.security_labels import XEP_0258


register_plugin(XEP_0258)
