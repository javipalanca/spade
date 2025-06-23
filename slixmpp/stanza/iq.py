
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2010  Nathanael C. Fritz
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import asyncio
from slixmpp.stanza.rootstanza import RootStanza
from slixmpp.xmlstream import StanzaBase, ET
from slixmpp.xmlstream.handler import Callback, CoroutineCallback
from slixmpp.xmlstream.matcher import MatchIDSender, MatcherId
from slixmpp.exceptions import IqTimeout, IqError


class Iq(RootStanza):

    """
    XMPP <iq> stanzas, or info/query stanzas, are XMPP's method of
    requesting and modifying information, similar to HTTP's GET and
    POST methods.

    Each <iq> stanza must have an 'id' value which associates the
    stanza with the response stanza. XMPP entities must always
    be given a response <iq> stanza with a type of 'result' after
    sending a stanza of type 'get' or 'set'.

    Most uses cases for <iq> stanzas will involve adding a <query>
    element whose namespace indicates the type of information
    desired. However, some custom XMPP applications use <iq> stanzas
    as a carrier stanza for an application-specific protocol instead.

    Example <iq> Stanzas:

    .. code-block:: xml

        <iq to="user@example.com" type="get" id="314">
          <query xmlns="http://jabber.org/protocol/disco#items" />
        </iq>

        <iq to="user@localhost" type="result" id="17">
          <query xmlns='jabber:iq:roster'>
            <item jid='otheruser@example.net'
                  name='John Doe'
                  subscription='both'>
              <group>Friends</group>
            </item>
          </query>
        </iq>

    Stanza Interface:
        - **query**: The namespace of the <query> element if one exists.
    Attributes:
        - **types**: May be one of: get, set, result, or error.
    """

    namespace = 'jabber:client'
    name = 'iq'
    interfaces = {'type', 'to', 'from', 'id', 'query'}
    types = {'get', 'result', 'set', 'error'}
    plugin_attrib = name

    def __init__(self, *args, recv=False, **kwargs):
        """
        Initialize a new <iq> stanza with an 'id' value.

        Overrides StanzaBase.__init__.
        """
        StanzaBase.__init__(self, *args, **kwargs)
        if not recv and self['id'] == '':
            if self.stream is not None:
                self['id'] = self.stream.new_id()
            else:
                self['id'] = '0'

    def unhandled(self):
        """
        Send a feature-not-implemented error if the stanza is not handled.

        Overrides StanzaBase.unhandled.
        """
        if self['type'] in ('get', 'set'):
            reply = self.reply()
            reply['error']['condition'] = 'feature-not-implemented'
            reply['error']['text'] = 'No handlers registered for this request.'
            reply.send()

    def set_payload(self, value):
        """
        Set the XML contents of the <iq> stanza.

        :param value: An XML object or a list of XML objects to use as the <iq>
                      stanza's contents
        :type value: list or XML object
        """
        self.clear()
        StanzaBase.set_payload(self, value)
        return self

    def set_query(self, value):
        """
        Add or modify a <query> element.

        Query elements are differentiated by their namespace.

        :param str value: The namespace of the <query> element.
        """
        query = self.xml.find("{%s}query" % value)
        if query is None and value:
            plugin = self.plugin_tag_map.get('{%s}query' % value, None)
            if plugin:
                self.enable(plugin.plugin_attrib)
            else:
                self.clear()
                query = ET.Element("{%s}query" % value)
                self.xml.append(query)
        return self

    def get_query(self):
        """Return the namespace of the <query> element.

        :rtype: str"""
        for child in self.xml:
            if child.tag.endswith('query'):
                ns = child.tag.split('}')[0]
                if '{' in ns:
                    ns = ns[1:]
                return ns
        return ''

    def del_query(self):
        """Remove the <query> element."""
        for child in self.xml:
            if child.tag.endswith('query'):
                self.xml.remove(child)
        return self

    def reply(self, clear=True):
        """
        Create a new <iq> stanza replying to ``self``.

        Overrides StanzaBase.reply

        Sets the 'type' to 'result' in addition to the default
        StanzaBase.reply behavior.

        :param bool clear: Indicates if existing content should be
                           removed before replying. Defaults to True.
        """
        new_iq = StanzaBase.reply(self, clear=clear)
        new_iq['type'] = 'result'
        return new_iq

    def send(self, callback=None, timeout=None):
        """Send an <iq> stanza over the XML stream.

        A callback handler can be provided that will be executed when the Iq
        stanza's result reply is received.

        Returns a future which result will be set to the result Iq if it is of type 'get' or 'set'
        (when it is received), or a future with the result set to None if it has another type.

        Overrides StanzaBase.send

        :param function callback: Optional reference to a stream handler
                                  function. Will be executed when a reply
                                  stanza is received.
        :param int timeout: The length of time (in seconds) to wait for a
                            response before raising an IqTimeout
        :rtype: asyncio.Future
        """
        if self.stream.session_bind_event.is_set():
            matcher = MatchIDSender({
                'id': self['id'],
                'self': self.stream.boundjid,
                'peer': self['to']
            })
        else:
            matcher = MatcherId(self['id'])

        future = asyncio.Future()

        # Prevents handlers from existing forever.
        if timeout is None:
            timeout = 120

        def callback_success(result):
            type_ = result['type']
            if type_ == 'result':
                if not future.done():
                    future.set_result(result)
            elif type_ == 'error':
                if not future.done():
                    future.set_exception(IqError(result))
            else:
                # Most likely an iq addressed to ourself, rearm the callback.
                handler = constr(handler_name,
                                 matcher,
                                 callback_success,
                                 once=True)
                self.stream.register_handler(handler)
                return

            if timeout is not None:
                self.stream.cancel_schedule('IqTimeout_%s' % self['id'])
            if callback is not None:
                callback(result)

        def callback_timeout():
            if not future.done():
                future.set_exception(IqTimeout(self))
            self.stream.remove_handler('IqCallback_%s' % self['id'])

        if self['type'] in ('get', 'set'):
            handler_name = 'IqCallback_%s' % self['id']
            if asyncio.iscoroutinefunction(callback):
                constr = CoroutineCallback
            else:
                constr = Callback
            if timeout is not None:
                self.stream.schedule('IqTimeout_%s' % self['id'],
                                     timeout,
                                     callback_timeout,
                                     repeat=False)
            handler = constr(handler_name,
                             matcher,
                             callback_success,
                             once=True)
            self.stream.register_handler(handler)
        else:
            future.set_result(None)
        StanzaBase.send(self)
        return future

    def _set_stanza_values(self, values):
        """
        Set multiple stanza interface values using a dictionary.

        Stanza plugin values may be set usind nested dictionaries.

        If the interface 'query' is given, then it will be set
        last to avoid duplication of the <query /> element.

        Overrides ElementBase._set_stanza_values.

        Arguments:
            values -- A dictionary mapping stanza interface with values.
                      Plugin interfaces may accept a nested dictionary that
                      will be used recursively.
        """
        query = values.get('query', '')
        if query:
            del values['query']
            StanzaBase._set_stanza_values(self, values)
            self['query'] = query
        else:
            StanzaBase._set_stanza_values(self, values)
        return self
