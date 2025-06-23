from datetime import datetime
from typing import Optional

from slixmpp.plugins.xep_0082 import format_datetime, parse
from slixmpp.plugins.xep_0300 import Hash
from slixmpp.plugins.xep_0264.stanza import Thumbnail
from slixmpp.xmlstream import ElementBase, register_stanza_plugin

NS = "urn:xmpp:file:metadata:0"


class File(ElementBase):
    name = "file"
    namespace = NS
    plugin_attrib = "file"
    interfaces = sub_interfaces = {
        "media-type",
        "name",
        "date",
        "size",
        "desc",
        "width",
        "height",
        "length"
    }

    def set_width(self, width: int):
        self.__set_if_positive("width", width)

    def get_width(self) -> Optional[int]:
        return _positive_int_or_none(self._get_sub_text("width"))

    def set_height(self, height: int):
        self.__set_if_positive("height", height)

    def get_height(self) -> Optional[int]:
        return _positive_int_or_none(self._get_sub_text("height"))

    def set_length(self, length: int):
        self.__set_if_positive("length", length)

    def get_length(self) -> Optional[int]:
        return _positive_int_or_none(self._get_sub_text("length"))

    def set_size(self, size: int):
        self.__set_if_positive("size", size)

    def get_size(self) -> Optional[int]:
        return _positive_int_or_none(self._get_sub_text("size"))

    def get_date(self) -> Optional[datetime]:
        try:
            return parse(self._get_sub_text("date"))
        except ValueError:
            return

    def set_date(self, stamp: datetime):
        try:
            self._set_sub_text("date", format_datetime(stamp))
        except ValueError:
            pass

    def __set_if_positive(self, key: str, value: int):
        if value <= 0:
            raise ValueError(f"Invalid value for element {key}: {value}")
        self._set_sub_text(key, str(value))


def _positive_int_or_none(v: str) -> Optional[int]:
    try:
        return int(v)
    except ValueError:
        return None

def register_plugins():
    register_stanza_plugin(File, Hash)
    register_stanza_plugin(File, Thumbnail)
