
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2011 Nathanael C. Fritz, Dalek
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import logging
from typing import Optional

import slixmpp
from slixmpp import Message, JID
from slixmpp.plugins import BasePlugin
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.xmlstream.handler import Callback
from slixmpp.xmlstream.matcher import StanzaPath
from slixmpp.plugins.xep_0249 import Invite, stanza


log = logging.getLogger(__name__)


class XEP_0249(BasePlugin):

    """
    XEP-0249: Direct MUC Invitations
    """

    name = 'xep_0249'
    description = 'XEP-0249: Direct MUC Invitations'
    dependencies = {'xep_0030'}
    stanza = stanza

    def plugin_init(self):
        self.xmpp.register_handler(
                Callback('Direct MUC Invitations',
                         StanzaPath('message/groupchat_invite'),
                         self._handle_invite))

        register_stanza_plugin(Message, Invite)

    def plugin_end(self):
        self.xmpp['xep_0030'].del_feature(feature=Invite.namespace)
        self.xmpp.remove_handler('Direct MUC Invitations')

    def session_bind(self, jid):
        self.xmpp['xep_0030'].add_feature(Invite.namespace)

    def _handle_invite(self, msg: Message):
        """
        Raise an event for all invitations received.
        """
        log.debug("Received direct muc invitation from %s to room %s",
                  msg['from'], msg['groupchat_invite']['jid'])

        self.xmpp.event('groupchat_direct_invite', msg)

    def send_invitation(self, jid: JID, roomjid: JID,
                        password: Optional[str] = None,
                        reason: Optional[str] = None, *,
                        mfrom: Optional[JID] = None):
        """
        Send a direct MUC invitation to an XMPP entity.

        :param JID jid: The JID of the entity that will receive
                        the invitation
        :param JID roomjid: the address of the groupchat room to be joined
        :param str password: a password needed for entry into a
                             password-protected room (OPTIONAL).
        :param str reason: a human-readable purpose for the invitation
                            (OPTIONAL).
        """

        msg = self.xmpp.Message()
        msg['to'] = jid
        if mfrom is not None:
            msg['from'] = mfrom
        msg['groupchat_invite']['jid'] = roomjid
        if password is not None:
            msg['groupchat_invite']['password'] = password
        if reason is not None:
            msg['groupchat_invite']['reason'] = reason

        return msg.send()
