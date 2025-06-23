
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2012 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import logging
from typing import Optional

from slixmpp import JID
from slixmpp.stanza import Iq
from slixmpp.exceptions import XMPPError
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.xmlstream.handler import CoroutineCallback
from slixmpp.xmlstream.matcher import StanzaPath
from slixmpp.plugins import BasePlugin
from slixmpp.plugins.xep_0054 import VCardTemp, stanza


log = logging.getLogger(__name__)


class XEP_0054(BasePlugin):

    """
    XEP-0054: vcard-temp
    """

    name = 'xep_0054'
    description = 'XEP-0054: vcard-temp'
    dependencies = {'xep_0030', 'xep_0082'}
    stanza = stanza

    def plugin_init(self):
        """
        Start the XEP-0054 plugin.
        """
        register_stanza_plugin(Iq, VCardTemp)


        self.api.register(self._set_vcard, 'set_vcard', default=True)
        self.api.register(self._get_vcard, 'get_vcard', default=True)
        self.api.register(self._del_vcard, 'del_vcard', default=True)

        self._vcard_cache = {}

        self.xmpp.register_handler(
                CoroutineCallback('VCardTemp',
                    StanzaPath('iq/vcard_temp'),
                    self._handle_get_vcard))

    def plugin_end(self):
        self.xmpp.remove_handler('VCardTemp')
        self.xmpp['xep_0030'].del_feature(feature='vcard-temp')

    def session_bind(self, jid):
        self.xmpp['xep_0030'].add_feature('vcard-temp')

    def make_vcard(self) -> VCardTemp:
        """Return an empty vcard element."""
        return VCardTemp()

    async def get_vcard(self, jid: Optional[JID] = None, *,
                        local: Optional[bool] = None, cached: bool = False,
                        ifrom: Optional[JID] = None,
                        **iqkwargs) -> Iq:
        """Retrieve a VCard.

        .. versionchanged:: 1.8.0
            This function is now a coroutine.

        :param jid: JID of the entity to fetch the VCard from.
        :param local: Only check internally for a vcard.
        :param cached: Whether to check in the local cache before
                       sending a query.
        """
        if local is None:
            if jid is not None and not isinstance(jid, JID):
                jid = JID(jid)
                if self.xmpp.is_component:
                    if jid.domain == self.xmpp.boundjid.domain:
                        local = True
                else:
                    if str(jid) == str(self.xmpp.boundjid):
                        local = True
                jid = jid.full
            elif jid in (None, ''):
                local = True

        if local:
            vcard = await self.api['get_vcard'](jid, None, ifrom)
            if not isinstance(vcard, Iq):
                iq = self.xmpp.Iq()
                if vcard is None:
                    vcard = VCardTemp()
                iq.append(vcard)
                return iq
            return vcard

        if cached:
            vcard = await self.api['get_vcard'](jid, None, ifrom)
            if vcard is not None:
                if not isinstance(vcard, Iq):
                    iq = self.xmpp.Iq()
                    iq.append(vcard)
                    return iq
                return vcard

        iq = self.xmpp.make_iq_get(ito=jid, ifrom=ifrom)
        iq.enable('vcard_temp')
        return await iq.send(**iqkwargs)

    async def publish_vcard(self, vcard: Optional[VCardTemp] = None,
                            jid: Optional[JID] = None,
                            ifrom: Optional[JID] = None, **iqkwargs):
        """Publish a vcard.

        .. versionchanged:: 1.8.0
            This function is now a coroutine.

        :param vcard: The VCard to publish.
        :param jid: The JID to publish the VCard to.
        """
        await self.api['set_vcard'](jid, None, ifrom, vcard)
        if self.xmpp.is_component:
            return

        iq = self.xmpp.make_iq_set(ito=jid, ifrom=ifrom)
        iq.append(vcard)
        await iq.send(**iqkwargs)

    async def _handle_get_vcard(self, iq: Iq):
        if iq['type'] == 'result':
            await self.api['set_vcard'](jid=iq['from'], args=iq['vcard_temp'])
            return
        elif iq['type'] == 'get' and self.xmpp.is_component:
            vcard = await self.api['get_vcard'](iq['to'].bare, ifrom=iq['from'])
            if vcard is None:
                raise XMPPError("item-not-found")
            elif isinstance(vcard, Iq):
                await vcard.send()
            else:
                iq = iq.reply()
                iq.append(vcard)
                iq.send()
        elif iq['type'] == 'set':
            raise XMPPError('service-unavailable')

    # =================================================================

    def _set_vcard(self, jid, node, ifrom, vcard):
        self._vcard_cache[jid.bare] = vcard

    def _get_vcard(self, jid, node, ifrom, vcard):
        return self._vcard_cache.get(jid.bare, None)

    def _del_vcard(self, jid, node, ifrom, vcard):
        if jid.bare in self._vcard_cache:
            del self._vcard_cache[jid.bare]
