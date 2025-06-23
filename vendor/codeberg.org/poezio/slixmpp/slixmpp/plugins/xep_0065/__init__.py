from slixmpp.plugins.base import register_plugin

from slixmpp.plugins.xep_0065.socks5 import Socks5Protocol
from slixmpp.plugins.xep_0065.stanza import Socks5
from slixmpp.plugins.xep_0065.proxy import XEP_0065


register_plugin(XEP_0065)
