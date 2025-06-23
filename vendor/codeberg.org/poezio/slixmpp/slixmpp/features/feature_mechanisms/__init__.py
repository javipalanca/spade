
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2011  Nathanael C. Fritz
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.features.feature_mechanisms.mechanisms import FeatureMechanisms
from slixmpp.features.feature_mechanisms.stanza import Mechanisms
from slixmpp.features.feature_mechanisms.stanza import Auth
from slixmpp.features.feature_mechanisms.stanza import Success
from slixmpp.features.feature_mechanisms.stanza import Failure


register_plugin(FeatureMechanisms)
