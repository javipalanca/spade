# Slixmpp: The Slick XMPP Library
# Copyright (C) 2025 nicoco
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.

from typing import Literal, Optional, cast

from slixmpp import register_stanza_plugin
from slixmpp.plugins.xep_0402.stanza import Extensions
from slixmpp.types import ClientTypes
from slixmpp.xmlstream import ElementBase

NS = "urn:xmpp:notification-settings:0"

WhenLiteral = Literal["never", "always", "on-mention"]


class Notify(ElementBase):
    """
    Chat notification settings element


    To enable it on a Conference element, use configure() like this:

    .. code-block::python

        # C being a Conference element
        C['extensions']["notify"].configure("always", client_type="pc")

    Which will add the <notify> element to the <extensions> element.
    """

    namespace = NS
    name = "notify"
    plugin_attrib = "notify"
    interfaces = {"notify"}

    def configure(self, when: WhenLiteral, client_type: Optional[ClientTypes] = None) -> None:
        """
        Configure the chat notification settings for this bookmark.

        This method ensures that there are no conflicting settings, e.g.,
        both a <never /> and a <always /> element.
        """
        cls = _CLASS_MAP[when]
        element = cls()
        if client_type is not None:
            element["client-type"] = client_type

        match = client_type if client_type is not None else ""
        for child in self:
            if isinstance(child, _Base) and child["client-type"] == match:
                self.xml.remove(child.xml)

        self.append(element)

    def get_config(
        self, client_type: Optional[ClientTypes] = None
    ) -> Optional[WhenLiteral]:
        """
        Get the chat notification settings for this bookmark.

        :param client_type: Optionally, get the notification for a specific client type.
            If unset, returns the global notification setting.

        :return: The chat notification setting as a string, or None if unset.
        """
        match = client_type if client_type is not None else ""
        for child in self:
            if isinstance(child, _Base) and child["client-type"] == match:
                return cast(WhenLiteral, child.name)
        return None


class _Base(ElementBase):
    namespace = NS
    interfaces = {"client-type"}


class Never(_Base):
    name = "never"
    plugin_attrib = name


class Always(_Base):
    name = "always"
    plugin_attrib = name


class OnMention(_Base):
    name = "on-mention"
    plugin_attrib = name


class Advanced(ElementBase):
    namespace = NS
    name = plugin_attrib = "advanced"


_CLASS_MAP = {
    "never": Never,
    "always": Always,
    "on-mention": OnMention,
}


def register_plugin():
    register_stanza_plugin(Extensions, Notify)
    register_stanza_plugin(Notify, Advanced)
    register_stanza_plugin(Notify, Never, iterable=True)
    register_stanza_plugin(Notify, Always, iterable=True)
    register_stanza_plugin(Notify, OnMention, iterable=True)
