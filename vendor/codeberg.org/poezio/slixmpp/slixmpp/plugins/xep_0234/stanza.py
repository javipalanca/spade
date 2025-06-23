from datetime import datetime

from slixmpp.plugins.xep_0082 import format_datetime, parse
from slixmpp.xmlstream import ElementBase

NS = "urn:xmpp:jingle:apps:file-transfer:5"


class File(ElementBase):
    name = "file"
    namespace = NS
    plugin_attrib = "file"
    interfaces = sub_interfaces = {"media-type", "name", "date", "size", "hash", "desc"}

    def set_size(self, size: int):
        self._set_sub_text("size", str(size))

    def get_size(self):
        return _int_or_none(self._get_sub_text("size"))

    def get_date(self):
        try:
            return parse(self._get_sub_text("date"))
        except ValueError:
            return

    def set_date(self, stamp: datetime):
        try:
            self._set_sub_text("date", format_datetime(stamp))
        except ValueError:
            pass


def _int_or_none(v):
    try:
        return int(v)
    except ValueError:
        return None
