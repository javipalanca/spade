
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2011  Nathanael C. Fritz
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.features.feature_starttls.starttls import FeatureSTARTTLS
from slixmpp.features.feature_starttls.stanza import *


register_plugin(FeatureSTARTTLS)
