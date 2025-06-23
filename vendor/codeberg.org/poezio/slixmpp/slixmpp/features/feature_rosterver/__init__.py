
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012  Nathanael C. Fritz
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.features.feature_rosterver.rosterver import FeatureRosterVer
from slixmpp.features.feature_rosterver.stanza import RosterVer


register_plugin(FeatureRosterVer)
