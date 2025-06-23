from slixmpp import register_stanza_plugin
from slixmpp.plugins.xep_0060.stanza import Item
from slixmpp.xmlstream import ElementBase

NS = "urn:xmpp:bookmarks:1"


class Conference(ElementBase):
    namespace = NS
    name = "conference"
    plugin_attrib = "conference"
    interfaces = {"name", "autojoin", "nick", "password"}
    sub_interfaces = {"nick", "password"}

    def set_autojoin(self, v: bool):
        self._set_attr("autojoin", "true" if v else "false")

    def get_autojoin(self):
        v = self._get_attr("autojoin", "")
        if not v:
            return False
        return v == "1" or v.lower() == "true"


class Extensions(ElementBase):
    namespace = NS
    name = "extensions"
    plugin_attrib = "extensions"


def register_plugin():
    register_stanza_plugin(Conference, Extensions)
    register_stanza_plugin(Item, Conference)
