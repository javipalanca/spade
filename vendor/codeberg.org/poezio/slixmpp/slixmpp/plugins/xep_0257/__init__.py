
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0257 import stanza
from slixmpp.plugins.xep_0257.stanza import Certs, AppendCert
from slixmpp.plugins.xep_0257.stanza import DisableCert, RevokeCert
from slixmpp.plugins.xep_0257.client_cert_management import XEP_0257


register_plugin(XEP_0257)
