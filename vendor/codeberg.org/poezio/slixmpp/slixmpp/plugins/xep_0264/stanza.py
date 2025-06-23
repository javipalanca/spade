from typing import Optional

from slixmpp import register_stanza_plugin
from slixmpp.plugins.xep_0234.stanza import File
from slixmpp.xmlstream import ElementBase

NS = "urn:xmpp:thumbs:1"


class Thumbnail(ElementBase):
    name = plugin_attrib = "thumbnail"
    namespace = NS
    interfaces = {"uri", "media-type", "width", "height"}

    def get_width(self) -> int:
        return _int_or_none(self._get_attr("width"))

    def get_height(self) -> int:
        return _int_or_none(self._get_attr("height"))

    def set_width(self, v: int) -> None:
        self._set_attr("width", str(v))

    def set_height(self, v: int) -> None:
        self._set_attr("height", str(v))


def _int_or_none(v) -> Optional[int]:
    try:
        return int(v)
    except ValueError:
        return None


def register_plugin():
    register_stanza_plugin(File, Thumbnail)
