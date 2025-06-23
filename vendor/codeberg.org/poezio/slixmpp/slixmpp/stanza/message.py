
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2010  Nathanael C. Fritz
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.stanza.rootstanza import RootStanza
from slixmpp.xmlstream import StanzaBase, ET


ORIGIN_NAME = '{urn:xmpp:sid:0}origin-id'


class Message(RootStanza):

    """
    XMPP's <message> stanzas are a "push" mechanism to send information
    to other XMPP entities without requiring a response.

    Chat clients will typically use <message> stanzas that have a type
    of either "chat" or "groupchat".

    When handling a message event, be sure to check if the message is
    an error response.

    Example <message> stanzas:

    .. code-block:: xml

        <message to="user1@example.com" from="user2@example.com">
          <body>Hi!</body>
        </message>

        <message type="groupchat" to="room@conference.example.com">
          <body>Hi everyone!</body>
        </message>

    Stanza Interface:
        - **body**: The main contents of the message.
        - **subject**: An optional description of the message's contents.
        - **mucroom**: (Read-only) The name of the MUC room that sent the message.
        - **mucnick**: (Read-only) The MUC nickname of message's sender.

    Attributes:
        - **types**: May be one of: normal, chat, headline, groupchat, or error.
    """

    name = 'message'
    namespace = 'jabber:client'
    plugin_attrib = name
    interfaces = {'type', 'to', 'from', 'id', 'body', 'subject', 'thread',
                  'parent_thread', 'mucroom', 'mucnick'}
    sub_interfaces = {'body', 'subject', 'thread'}
    lang_interfaces = sub_interfaces
    types = {'normal', 'chat', 'headline', 'error', 'groupchat'}

    def __init__(self, *args, recv=False, **kwargs):
        """
        Initialize a new <message /> stanza with an optional 'id' value.

        Overrides StanzaBase.__init__.
        """
        StanzaBase.__init__(self, *args, **kwargs)
        if not recv and self['id'] == '':
            if self.stream:
                use_ids = getattr(self.stream, 'use_message_ids', None)
                if use_ids:
                    self.set_id(self.stream.new_id())
            else:
                self.del_origin_id()

    def get_type(self):
        """
        Return the message type.

        Overrides default stanza interface behavior.

        Returns 'normal' if no type attribute is present.

        :rtype: str
        """
        return self._get_attr('type', 'normal')

    def get_id(self):
        return self._get_attr('id') or ''

    def get_origin_id(self):
        sub = self.xml.find(ORIGIN_NAME)
        if sub is not None:
            return sub.attrib.get('id') or ''
        return ''

    def _set_ids(self, value) -> None:
        if value is None or value == '':
            return None

        self.xml.attrib['id'] = value

        if self.stream:
            if not getattr(self.stream, 'use_origin_id', False):
                self.del_origin_id()
                return None

        sub = self.xml.find(ORIGIN_NAME)
        if sub is not None:
            sub.attrib['id'] = value
        else:
            sub = ET.Element(ORIGIN_NAME)
            sub.attrib['id'] = value
            self.xml.append(sub)

    def set_id(self, value):
        return self._set_ids(value)

    def set_origin_id(self, value: str):
        return self._set_ids(value)

    def del_origin_id(self):
        sub = self.xml.find(ORIGIN_NAME)
        if sub is not None:
            self.xml.remove(sub)

    def get_parent_thread(self):
        """Return the message thread's parent thread.

        :rtype: str
        """
        thread = self.xml.find('{%s}thread' % self.namespace)
        if thread is not None:
            return thread.attrib.get('parent', '')
        return ''

    def set_parent_thread(self, value):
        """Add or change the message thread's parent thread.

        :param str value: identifier of the thread"""
        thread = self.xml.find('{%s}thread' % self.namespace)
        if value:
            if thread is None:
                thread = ET.Element('{%s}thread' % self.namespace)
                self.xml.append(thread)
            thread.attrib['parent'] = value
        else:
            if thread is not None and 'parent' in thread.attrib:
                del thread.attrib['parent']

    def del_parent_thread(self):
        """Delete the message thread's parent reference."""
        thread = self.xml.find('{%s}thread' % self.namespace)
        if thread is not None and 'parent' in thread.attrib:
            del thread.attrib['parent']

    def chat(self):
        """Set the message type to 'chat'."""
        self['type'] = 'chat'
        return self

    def normal(self):
        """Set the message type to 'normal'."""
        self['type'] = 'normal'
        return self

    def reply(self, body=None, clear=True):
        """
        Create a message reply.

        Overrides StanzaBase.reply.

        Sets proper 'to' attribute if the message is from a MUC, and
        adds a message body if one is given.

        :param str body:  Optional text content for the message.
        :param bool clear: Indicates if existing content should be removed
                           before replying. Defaults to True.

        :rtype: :class:`~.Message`
        """
        new_message = StanzaBase.reply(self, clear)

        if not getattr(self.stream, "is_component", False) and self['type'] == 'groupchat':
            new_message['to'] = new_message['to'].bare

        new_message['thread'] = self['thread']
        new_message['parent_thread'] = self['parent_thread']

        del new_message['id']
        if self.stream is not None and self.stream.use_message_ids:
            new_message['id'] = self.stream.new_id()

        if body is not None:
            new_message['body'] = body
        return new_message

    def get_mucroom(self):
        """
        Return the name of the MUC room where the message originated.

        Read-only stanza interface.

        :rtype: str
        """
        if self['type'] == 'groupchat':
            return self['from'].bare
        else:
            return ''

    def get_mucnick(self):
        """
        Return the nickname of the MUC user that sent the message.

        Read-only stanza interface.

        :rtype: str
        """
        if self['type'] == 'groupchat':
            return self['from'].resource
        else:
            return ''

    def set_mucroom(self, value):
        """Dummy method to prevent modification."""
        pass

    def del_mucroom(self):
        """Dummy method to prevent deletion."""
        pass

    def set_mucnick(self, value):
        """Dummy method to prevent modification."""
        pass

    def del_mucnick(self):
        """Dummy method to prevent deletion."""
        pass
