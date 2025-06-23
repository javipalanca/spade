
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2011 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import logging
import hashlib
import base64

from asyncio import Future, Lock
from collections import defaultdict
from typing import Optional

from slixmpp import __version__
from slixmpp.stanza import StreamFeatures, Presence, Iq
from slixmpp.xmlstream import register_stanza_plugin, JID
from slixmpp.xmlstream.handler import Callback
from slixmpp.xmlstream.matcher import StanzaPath
from slixmpp.util import MemoryCache
from slixmpp.exceptions import XMPPError
from slixmpp.plugins import BasePlugin
from slixmpp.plugins.xep_0115 import stanza, StaticCaps
from slixmpp.types import OptJidStr


log = logging.getLogger(__name__)


class XEP_0115(BasePlugin):

    """
    XEP-0115: Entity Capabilities
    """

    name = 'xep_0115'
    description = 'XEP-0115: Entity Capabilities'
    dependencies = {'xep_0030', 'xep_0128', 'xep_0004'}
    stanza = stanza
    default_config = {
        'hash': 'sha-1',
        'caps_node': None,
        'broadcast': True,
        'cache': None,
    }

    def plugin_init(self):
        self.hashes = {'sha-1': hashlib.sha1,
                       'sha1': hashlib.sha1,
                       'md5': hashlib.md5}

        if self.caps_node is None:
            self.caps_node = 'http://slixmpp.com/ver/%s' % __version__

        if self.cache is None:
            self.cache = MemoryCache()

        register_stanza_plugin(Presence, stanza.Capabilities)
        register_stanza_plugin(StreamFeatures, stanza.Capabilities)

        self._disco_ops = ['cache_caps',
                           'get_caps',
                           'assign_verstring',
                           'get_verstring',
                           'supports',
                           'has_identity']

        self.xmpp.register_handler(
                Callback('Entity Capabilites',
                         StanzaPath('presence/caps'),
                         self._handle_caps))

        self.xmpp.add_filter('out', self._filter_add_caps)

        self.xmpp.add_event_handler('entity_caps', self._process_caps)

        if not self.xmpp.is_component:
            self.xmpp.register_feature('caps',
                    self._handle_caps_feature,
                    restart=False,
                    order=10010)

        disco = self.xmpp['xep_0030']
        self.static = StaticCaps(self.xmpp, disco.static)

        for op in self._disco_ops:
            self.api.register(getattr(self.static, op), op, default=True)

        for op in ('supports', 'has_identity'):
            self.xmpp['xep_0030'].api.register(getattr(self.static, op), op)

        self._run_node_handler = disco._run_node_handler

        disco.cache_caps = self.cache_caps
        disco.update_caps = self.update_caps
        disco.assign_verstring = self.assign_verstring
        disco.get_verstring = self.get_verstring

        # prevent concurrent fetches for the same hash
        self._locks = defaultdict(Lock)

    def plugin_end(self):
        self.xmpp['xep_0030'].del_feature(feature=stanza.Capabilities.namespace)
        self.xmpp.del_filter('out', self._filter_add_caps)
        self.xmpp.del_event_handler('entity_caps', self._process_caps)
        self.xmpp.remove_handler('Entity Capabilities')
        if not self.xmpp.is_component:
            self.xmpp.unregister_feature('caps', 10010)
        for op in ('supports', 'has_identity'):
            self.xmpp['xep_0030'].restore_defaults(op)

    def session_bind(self, jid):
        self.xmpp['xep_0030'].add_feature(stanza.Capabilities.namespace)

    async def _filter_add_caps(self, stanza):
        if not isinstance(stanza, Presence) or not self.broadcast:
            return stanza

        if stanza['type'] not in ('available', 'chat', 'away', 'dnd', 'xa'):
            return stanza

        ver = await self.get_verstring(stanza['from'])
        if ver:
            stanza['caps']['node'] = self.caps_node
            stanza['caps']['hash'] = self.hash
            stanza['caps']['ver'] = ver
        return stanza

    def _handle_caps(self, presence):
        if not self.xmpp.is_component:
            if presence['from'] == self.xmpp.boundjid:
                return
        self.xmpp.event('entity_caps', presence)

    def _handle_caps_feature(self, features):
        # We already have a method to process presence with
        # caps, so wrap things up and use that.
        p = Presence()
        p['from'] = self.xmpp.boundjid.domain
        p.append(features['caps'])
        self.xmpp.features.add('caps')

        self.xmpp.event('entity_caps', p)

    async def _process_caps(self, pres: Presence):
        if not pres['caps']['hash']:
            log.debug("Received unsupported legacy caps: %s, %s, %s",
                    pres['caps']['node'],
                    pres['caps']['ver'],
                    pres['caps']['ext'])
            self.xmpp.event('entity_caps_legacy', pres)
            return

        ver = pres['caps']['ver']
        async with self._locks[ver]:
            await self._process_caps_wrapped(pres, ver)
        self._locks.pop(ver, None)

    async def _process_caps_wrapped(self, pres: Presence, ver: str):
        existing_verstring = await self.get_verstring(pres['from'].full)
        if str(existing_verstring) == str(ver):
            return

        existing_caps = await self.get_caps(verstring=ver)
        if existing_caps is not None:
            await self.assign_verstring(pres['from'], ver)
            return

        ifrom = pres['to'] if self.xmpp.is_component else None

        if pres['caps']['hash'] not in self.hashes:
            try:
                log.debug("Unknown caps hash: %s", pres['caps']['hash'])
                await self.xmpp['xep_0030'].get_info(jid=pres['from'], ifrom=ifrom)
                return
            except XMPPError:
                return

        log.debug("New caps verification string: %s", ver)
        try:
            node = '%s#%s' % (pres['caps']['node'], ver)
            caps = await self.xmpp['xep_0030'].get_info(pres['from'], node,
                                                             ifrom=ifrom)

            if isinstance(caps, Iq):
                caps = caps['disco_info']

            if await self._validate_caps(caps, pres['caps']['hash'],
                                               pres['caps']['ver']):
                await self.assign_verstring(pres['from'], pres['caps']['ver'])
        except XMPPError:
            log.debug("Could not retrieve disco#info results for caps for %s", node)

    async def _validate_caps(self, caps, hash, check_verstring):
        # Check Identities
        full_ids = caps.get_identities(dedupe=False)
        deduped_ids = caps.get_identities()
        if len(full_ids) != len(deduped_ids):
            log.debug("Duplicate disco identities found, invalid for caps")
            return False

        # Check Features
        full_features = caps.get_features(dedupe=False)
        deduped_features = caps.get_features()
        if len(full_features) != len(deduped_features):
            log.debug("Duplicate disco features found, invalid for caps")
            return False

        # Check Forms
        form_types = []
        deduped_form_types = set()
        for stanza in caps['substanzas']:
            if not isinstance(stanza, self.xmpp['xep_0004'].stanza.Form):
                log.debug("Non form extension found, ignoring for caps")
                caps.xml.remove(stanza.xml)
                continue
            if 'FORM_TYPE' in stanza.get_fields():
                f_type = tuple(stanza.get_fields()['FORM_TYPE']['value'])
                form_types.append(f_type)
                deduped_form_types.add(f_type)
                if len(form_types) != len(deduped_form_types):
                    log.debug("Duplicated FORM_TYPE values, " + \
                              "invalid for caps")
                    return False

                if len(f_type) > 1:
                    deduped_type = set(f_type)
                    if len(f_type) != len(deduped_type):
                        log.debug("Extra FORM_TYPE data, invalid for caps")
                        return False

                if stanza.get_fields()['FORM_TYPE']['type'] != 'hidden':
                    log.debug("Field FORM_TYPE type not 'hidden', " + \
                              "ignoring form for caps")
                    caps.xml.remove(stanza.xml)
            else:
                log.debug("No FORM_TYPE found, ignoring form for caps")
                caps.xml.remove(stanza.xml)

        verstring = self.generate_verstring(caps, hash)
        if verstring != check_verstring:
            log.debug("Verification strings do not match: %s, %s" % (
                verstring, check_verstring))
            return False

        await self.cache_caps(verstring, caps)
        return True

    def generate_verstring(self, info, hash):
        hash = self.hashes.get(hash, None)
        if hash is None:
            return None

        S = ''

        # Convert None to '' in the identities
        def clean_identity(id):
            return map(lambda i: i or '', id)
        identities = map(clean_identity, info['identities'])

        identities = sorted(('/'.join(i) for i in identities))
        features = sorted(info['features'])

        S += '<'.join(identities) + '<'
        S += '<'.join(features) + '<'

        form_types = {}

        for stanza in info['substanzas']:
            if isinstance(stanza, self.xmpp['xep_0004'].stanza.Form):
                if 'FORM_TYPE' in stanza.get_fields():
                    f_type = stanza['values']['FORM_TYPE']
                    if len(f_type):
                        f_type = f_type[0]
                    if f_type not in form_types:
                        form_types[f_type] = []
                    form_types[f_type].append(stanza)

        sorted_forms = sorted(form_types.keys())
        for f_type in sorted_forms:
            for form in form_types[f_type]:
                S += '%s<' % f_type
                fields = sorted(form.get_fields().keys())
                fields.remove('FORM_TYPE')
                for field in fields:
                    S += '%s<' % field
                    vals = form.get_fields()[field].get_value(convert=False)
                    if vals is None:
                        S += '<'
                    else:
                        if not isinstance(vals, list):
                            vals = [vals]
                        S += '<'.join(sorted(vals)) + '<'

        binary = hash(S.encode('utf8')).digest()
        return base64.b64encode(binary).decode('utf-8')

    async def update_caps(self, jid: OptJidStr = None,
                          node: Optional[str] = None,
                          preserve: bool = False,
                          broadcast: bool = True):
        """Update caps for a local JID based on current data.

        :param jid: JID whose info to update
        :param node: Node to fetch info from
        :param broadcast: Send a presence after updating.
        :param preserve: Send presence only to contacts found in the roster.
        """
        try:
            info = await self.xmpp['xep_0030'].get_info(jid, node, local=True)
            if isinstance(info, Iq):
                info = info['disco_info']
            ver = self.generate_verstring(info, self.hash)
            await self.xmpp['xep_0030'].set_info(
                jid=jid,
                node='%s#%s' % (self.caps_node, ver),
                info=info
            )
            await self.cache_caps(ver, info)
            await self.assign_verstring(jid, ver)

            if broadcast and self.xmpp.sessionstarted and self.broadcast:
                if self.xmpp.is_component or preserve:
                    for contact in self.xmpp.roster[jid]:
                        self.xmpp.roster[jid][contact].send_last_presence()
                else:
                    self.xmpp.roster[jid].send_last_presence()
        except XMPPError:
            return

    def get_verstring(self, jid=None) -> Future:
        """Get the stored verstring for a JID.

        .. versionchanged:: 1.8.0
            This function now returns a Future.
        """
        if jid in ('', None):
            jid = self.xmpp.boundjid.full
        if isinstance(jid, JID):
            jid = jid.full
        return self.api['get_verstring'](jid)

    def assign_verstring(self, jid=None, verstring=None) -> Future:
        """Assign a vertification string to a jid.

        .. versionchanged:: 1.8.0
            This function now returns a Future.
        """
        if jid in (None, ''):
            jid = self.xmpp.boundjid.full
        if isinstance(jid, JID):
            jid = jid.full
        return self.api['assign_verstring'](jid, args={
            'verstring': verstring
        })

    def cache_caps(self, verstring=None, info=None) -> Future:
        """Add caps to the cache.

        .. versionchanged:: 1.8.0
            This function now returns a Future.
        """
        data = {'verstring': verstring, 'info': info}
        return self.api['cache_caps'](args=data)

    async def get_caps(self, jid=None, verstring=None):
        """Get caps for a JID.

        .. versionchanged:: 1.8.0
            This function is now a coroutine.
        """
        if verstring is None:
            if jid is not None:
                verstring = await self.get_verstring(jid)
            else:
                return None
        if isinstance(jid, JID):
            jid = jid.full
        data = {'verstring': verstring}
        return await self.api['get_caps'](jid, args=data)
