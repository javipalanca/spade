# Slixmpp: The Slick XMPP Library
# Copyright (C) 2020 Mathieu Pasquet <mathieui@mathieui.net>
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from typing import (
    Iterable,
    Optional,
    Tuple,
)

from slixmpp import JID, Message
from slixmpp.plugins import BasePlugin
from slixmpp.plugins.xep_0439 import stanza
from slixmpp.xmlstream.matcher import StanzaPath
from slixmpp.xmlstream.handler import Callback



class XEP_0439(BasePlugin):
    '''XEP-0439: Quick Response'''

    name = 'xep_0439'
    description = 'XEP-0439: Quick Response'
    dependencies = set()
    stanza = stanza
    namespace = stanza.NS

    def plugin_init(self) -> None:
        stanza.register_plugins()
        self.xmpp.register_handler(Callback(
            'Action received',
            StanzaPath('message/action'),
            self._handle_action,
        ))
        self.xmpp.register_handler(Callback(
            'Response received',
            StanzaPath('message/response'),
            self._handle_response,
        ))
        self.xmpp.register_handler(Callback(
            'ActionSelected received',
            StanzaPath('message/action_selected'),
            self._handle_action_selected,
        ))

    def plugin_send(self):
        self.xmpp.remove_handler('Action received')
        self.xmpp.remove_handler('Response received')
        self.xmpp.remove_handler('ActionSelected received')

    def _handle_response(self, msg: Message):
        self.xmpp.event('responses_received', msg)

    def _handle_action(self, msg: Message):
        self.xmpp.event('action_received', msg)

    def _handle_action_selected(self, msg: Message):
        self.xmpp.event('action_selected', msg)

    def ask_for_response(self, mto: JID, body: str,
                         responses: Iterable[Tuple[str, str]],
                         mtype: str = 'chat', lang: Optional[str] = None, *,
                         mfrom: Optional[JID] = None):
        """
        Send a message with a set of responses.

        :param JID mto: The JID of the entity which will receive the message
        :param str body: The message body of the question
        :param Iterable[Tuple[str, str]] responses: A set of tuples containing
            (value, label) for each response
        :param str mtype: The message type
        :param str lang: The lang of the message (if not use, the default
            for this session will be used.
        """
        if lang is None:
            lang = self.xmpp.default_lang
        msg = self.xmpp.make_message(mto=mto, mfrom=mfrom, mtype=mtype)
        msg['body|%s' % lang] = body
        values = set()
        for value, label in responses:
            if value in values:
                raise ValueError("Duplicate values")
            values.add(value)
            elem = stanza.Response()
            elem['lang'] = lang
            elem['value'] = value
            elem['label'] = label
            msg.append(elem)
        msg.send()

    def ask_for_actions(self, mto: JID, body: str,
                        actions: Iterable[Tuple[str, str]],
                        mtype: str = 'chat', lang: Optional[str] = None, *,
                        mfrom: Optional[JID] = None):
        """
        Send a message with a set of actions.

        :param JID mto: The JID of the entity which will receive the message
        :param str body: The message body of the question
        :param Iterable[Tuple[str, str]] actions: A set of tuples containing
            (action, label) for each action
        :param str mtype: The message type
        :param str lang: The lang of the message (if not use, the default
            for this session will be used.
        """
        if lang is None:
            lang = self.xmpp.default_lang
        msg = self.xmpp.make_message(mto=mto, mfrom=mfrom, mtype=mtype)
        msg['body|%s' % lang] = body
        ids = set()
        for id, label in actions:
            if id in ids:
                raise ValueError("Duplicate ids")
            ids.add(id)
            elem = stanza.Action()
            elem['lang'] = lang
            elem['id'] = id
            elem['label'] = label
            msg.append(elem)
        msg.send()
