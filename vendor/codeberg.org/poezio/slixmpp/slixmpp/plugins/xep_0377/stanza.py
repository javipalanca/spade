
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2020 Mathieu Pasquet
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.xmlstream import ET, ElementBase


class Report(ElementBase):
    """
    A spam/abuse report.

    Example sub stanza:
    ::

        <report xmlns="urn:xmpp:reporting:1" reason="urn:xmpp:reporting:abuse">
          <text xml:lang="en">
            Never came trouble to my house like this.
          </text>
        </report>

    The reason attribute is mandatory.

    """
    name = "report"
    namespace = "urn:xmpp:reporting:1"
    plugin_attrib = "report"
    interfaces = ("text", "reason")
    sub_interfaces = {'text'}


class Text(ElementBase):
    name = "text"
    plugin_attrib = "text"
    namespace = "urn:xmpp:reporting:1"
