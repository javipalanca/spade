
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import hashlib
import logging
from asyncio import Future
from typing import (
    Dict,
    Optional,
)

from slixmpp import JID
from slixmpp.stanza import Presence
from slixmpp.exceptions import XMPPError, IqTimeout, IqError
from slixmpp.xmlstream import register_stanza_plugin, ElementBase
from slixmpp.plugins.base import BasePlugin
from slixmpp.plugins.xep_0153 import stanza, VCardTempUpdate


log = logging.getLogger(__name__)


class XEP_0153(BasePlugin):

    name = 'xep_0153'
    description = 'XEP-0153: vCard-Based Avatars'
    dependencies = {'xep_0054'}
    stanza = stanza

    def plugin_init(self):
        self._hashes = {}

        register_stanza_plugin(Presence, VCardTempUpdate)

        self.xmpp.add_filter('out', self._update_presence)

        self.xmpp.add_event_handler('session_start', self._start)

        self.xmpp.add_event_handler('presence_available', self._recv_presence)
        self.xmpp.add_event_handler('presence_dnd', self._recv_presence)
        self.xmpp.add_event_handler('presence_xa', self._recv_presence)
        self.xmpp.add_event_handler('presence_chat', self._recv_presence)
        self.xmpp.add_event_handler('presence_away', self._recv_presence)

        self.api.register(self._set_hash, 'set_hash', default=True)
        self.api.register(self._get_hash, 'get_hash', default=True)
        self.api.register(self._reset_hash, 'reset_hash', default=True)

    def plugin_end(self):
        self.xmpp.del_filter('out', self._update_presence)
        self.xmpp.del_event_handler('session_start', self._start)
        self.xmpp.del_event_handler('session_end', self._end)
        self.xmpp.del_event_handler('presence_available', self._recv_presence)
        self.xmpp.del_event_handler('presence_dnd', self._recv_presence)
        self.xmpp.del_event_handler('presence_xa', self._recv_presence)
        self.xmpp.del_event_handler('presence_chat', self._recv_presence)
        self.xmpp.del_event_handler('presence_away', self._recv_presence)

    def set_avatar(self, jid: Optional[JID] = None,
                   avatar: Optional[bytes] = None,
                   mtype: Optional[str] = None, **iqkwargs) -> Future:
        """Set a VCard avatar.

        :param jid: The JID to set the avatar for.
        :param avatar: Avatar content.
        :param mtype: Avatar file type (e.g. image/jpeg).
        """
        if jid is None:
            jid = self.xmpp.boundjid.bare

        async def get_and_set_avatar():
            timeout = iqkwargs.get('timeout', None)
            try:
                result = await self.xmpp['xep_0054'].get_vcard(
                    jid,
                    cached=False,
                    timeout=timeout
                )
            except IqTimeout:
                raise
            vcard = result['vcard_temp']
            vcard['PHOTO']['TYPE'] = mtype
            vcard['PHOTO']['BINVAL'] = avatar

            try:
                result = await self.xmpp['xep_0054'].publish_vcard(
                    jid=jid,
                    vcard=vcard,
                    **iqkwargs
                )
            except IqTimeout:
                raise
            await self.api['reset_hash'](jid)
            self.xmpp.roster[jid].send_last_presence()

        return self.xmpp.wrap(get_and_set_avatar())

    async def _start(self, event):
        try:
            vcard = await self.xmpp['xep_0054'].get_vcard(self.xmpp.boundjid.bare)
            data = vcard['vcard_temp']['PHOTO']['BINVAL']
            if not data:
                new_hash = ''
            else:
                new_hash = hashlib.sha1(data).hexdigest()
            await self.api['set_hash'](self.xmpp.boundjid, args=new_hash)
        except XMPPError:
            log.debug('Could not retrieve vCard for %s', self.xmpp.boundjid.bare)

    async def _update_presence(self, stanza: ElementBase) -> ElementBase:
        if not isinstance(stanza, Presence):
            return stanza

        if stanza['type'] not in ('available', 'dnd', 'chat', 'away', 'xa'):
            return stanza

        current_hash = await self.api['get_hash'](stanza['from'])
        stanza['vcard_temp_update']['photo'] = current_hash
        return stanza

    async def _recv_presence(self, pres: Presence):
        try:
            if pres.get_plugin('muc', check=True):
                # Don't process vCard avatars for MUC occupants
                # since they all share the same bare JID.
                return
        except:
            pass

        if not pres.match('presence/vcard_temp_update'):
            await self.api['set_hash'](pres['from'], args=None)
            return

        data = pres['vcard_temp_update']['photo']
        if data is None:
            return
        self.xmpp.event('vcard_avatar_update', pres)

    # =================================================================

    async def _reset_hash(self, jid: JID, node: str, ifrom: JID, args: Dict):
        own_jid = (jid.bare == self.xmpp.boundjid.bare)
        if self.xmpp.is_component:
            own_jid = (jid.domain == self.xmpp.boundjid.domain)

        await self.api['set_hash'](jid, args=None)
        if own_jid:
            self.xmpp.roster[jid].send_last_presence()

        try:
            iq = await self.xmpp['xep_0054'].get_vcard(jid=jid.bare, ifrom=ifrom)
        except (IqError, IqTimeout):
            log.debug('Could not retrieve vCard for %s', jid)
            return
        try:
            data = iq['vcard_temp']['PHOTO']['BINVAL']
        except ValueError:
            log.debug('Invalid BINVAL in vCard’s PHOTO for %s:', jid, exc_info=True)
            data = None
        if not data:
            new_hash = ''
        else:
            new_hash = hashlib.sha1(data).hexdigest()

        await self.api['set_hash'](jid, args=new_hash)

    def _get_hash(self, jid: JID, node: str, ifrom: JID, args: Dict):
        return self._hashes.get(jid.bare, None)

    def _set_hash(self, jid: JID, node: str, ifrom: JID, args: Dict):
        self._hashes[jid.bare] = args
