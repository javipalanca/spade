# Slixmpp: The Slick XMPP Library
# Copyright (C) 2020 Mathieu Pasquet <mathieui@mathieui.net>
# This file is part of Slixmpp.
# See the file LICENSE for copying permissio
from abc import ABC
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from slixmpp.stanza import Message
from slixmpp.xmlstream import (
    ElementBase,
    register_stanza_plugin,
)


NS = "urn:xmpp:fallback:0"


class Fallback(ElementBase):
    namespace = NS
    name = "fallback"
    plugin_attrib = "fallback"
    plugin_multi_attrib = "fallbacks"
    interfaces = {"for"}

    def _find_fallback(self, fallback_for: str) -> "Fallback":
        if self["for"] == fallback_for:
            return self
        for fallback in self.parent()["fallbacks"]:
            if fallback["for"] == fallback_for:
                return fallback
        raise AttributeError("No fallback for this namespace", fallback_for)

    def get_stripped_body(
        self, fallback_for: str, element: Literal["body", "subject"] = "body"
    ) -> str:
        """
        Get the body of a message, with the fallback part stripped

        :param fallback_for: namespace of the fallback to strip
        :param element: set this to "subject" get the stripped subject instead
            of body

        :return: body (or subject) content minus the fallback part
        """
        fallback = self._find_fallback(fallback_for)
        start = fallback[element]["start"]
        end = fallback[element]["end"]
        body = self.parent()[element]
        if start == end == 0:
            return ""
        if start <= end < len(body):
            return body[:start] + body[end:]
        else:
            return body


class FallbackMixin(ABC):
    namespace = NS
    name = NotImplemented
    plugin_attrib = NotImplemented
    interfaces = {"start", "end"}

    def set_start(self, v: int):
        self._set_attr("start", str(v))

    def get_start(self):
        return _int_or_zero(self._get_attr("start"))

    def set_end(self, v: int):
        self._set_attr("end", str(v))

    def get_end(self):
        return _int_or_zero(self._get_attr("end"))


class FallbackBody(FallbackMixin, ElementBase):
    name = plugin_attrib = "body"


class FallbackSubject(FallbackMixin, ElementBase):
    name = plugin_attrib = "subject"


def _int_or_zero(v: str):
    try:
        return int(v)
    except ValueError:
        return 0


def register_plugins():
    register_stanza_plugin(Message, Fallback, iterable=True)
    register_stanza_plugin(Fallback, FallbackBody)
    register_stanza_plugin(Fallback, FallbackSubject)
