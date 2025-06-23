
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2010  Nathanael C. Fritz
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.xmlstream import ElementBase, register_stanza_plugin

class AtomEntry(ElementBase):

    """
    A simple Atom feed entry.

    Stanza Interface:
        title   -- The title of the Atom feed entry.
        summary -- The summary of the Atom feed entry.
    """

    namespace = 'http://www.w3.org/2005/Atom'
    name = 'entry'
    plugin_attrib = 'entry'
    interfaces = {'title', 'summary', 'id', 'published', 'updated'}
    sub_interfaces = {'title', 'summary', 'id', 'published', 'updated'}

class AtomAuthor(ElementBase):

    """
    An Atom author.

    Stanza Interface:
        name -- The printable author name
        uri  -- The bare jid of the author
    """

    name = 'author'
    plugin_attrib = 'author'
    interfaces = {'name', 'uri'}
    sub_interfaces = {'name', 'uri'}

register_stanza_plugin(AtomEntry, AtomAuthor)
