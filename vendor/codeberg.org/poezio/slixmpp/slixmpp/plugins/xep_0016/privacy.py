
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2011 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from asyncio import Future
from typing import Optional, Callable, Iterable

from slixmpp import Iq
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.plugins import BasePlugin
from slixmpp.plugins.xep_0016 import stanza
from slixmpp.plugins.xep_0016.stanza import Privacy, Item


class XEP_0016(BasePlugin):

    name = 'xep_0016'
    description = 'XEP-0016: Privacy Lists'
    dependencies = {'xep_0030'}
    stanza = stanza

    def plugin_init(self):
        register_stanza_plugin(Iq, Privacy)

    def plugin_end(self):
        self.xmpp['xep_0030'].del_feature(feature=Privacy.namespace)

    def session_bind(self, jid):
        self.xmpp['xep_0030'].add_feature(Privacy.namespace)

    def get_privacy_lists(self, timeout: Optional[int] = None,
                          callback: Optional[Callable] = None) -> Future:
        iq = self.xmpp.Iq()
        iq['type'] = 'get'
        iq.enable('privacy')
        return iq.send(timeout=timeout, callback=callback)

    def get_list(self, name: str, timeout: Optional[int] = None,
                 callback: Optional[Callable] = None) -> Future:
        iq = self.xmpp.Iq()
        iq['type'] = 'get'
        iq['privacy']['list']['name'] = name
        return iq.send(timeout=timeout, callback=callback)

    def get_active(self, timeout: Optional[int] = None,
                   callback: Optional[Callable] = None) -> Future:
        iq = self.xmpp.Iq()
        iq['type'] = 'get'
        iq['privacy'].enable('active')
        return iq.send(timeout=timeout, callback=callback)

    def get_default(self, timeout: Optional[int] = None,
                    callback: Optional[Callable] = None) -> Future:
        iq = self.xmpp.Iq()
        iq['type'] = 'get'
        iq['privacy'].enable('default')
        return iq.send(timeout=timeout, callback=callback)

    def activate(self, name: str, timeout: Optional[int] = None,
                 callback: Optional[Callable] = None) -> Future:
        iq = self.xmpp.Iq()
        iq['type'] = 'set'
        iq['privacy']['active']['name'] = name
        return iq.send(timeout=timeout, callback=callback)

    def deactivate(self, timeout: Optional[int] = None,
                   callback: Optional[Callable] = None) -> Future:
        iq = self.xmpp.Iq()
        iq['type'] = 'set'
        iq['privacy'].enable('active')
        return iq.send(timeout=timeout, callback=callback)

    def make_default(self, name, timeout: Optional[int] = None,
                     callback: Optional[Callable] = None) -> Future:
        iq = self.xmpp.Iq()
        iq['type'] = 'set'
        iq['privacy']['default']['name'] = name
        return iq.send(timeout=timeout, callback=callback)

    def remove_default(self, timeout: Optional[int] = None,
                       callback: Optional[Callable] = None) -> Future:
        iq = self.xmpp.Iq()
        iq['type'] = 'set'
        iq['privacy'].enable('default')
        return iq.send(timeout=timeout, callback=callback)

    def edit_list(self, name: str, rules: Iterable[Item],
                  timeout: Optional[int] = None,
                  callback: Optional[Callable] = None) -> Future:
        iq = self.xmpp.Iq()
        iq['type'] = 'set'
        iq['privacy']['list']['name'] = name
        priv_list = iq['privacy']['list']

        if not rules:
            rules = []

        for rule in rules:
            if isinstance(rule, Item):
                priv_list.append(rule)
                continue

            priv_list.add_item(
                rule['value'],
                rule['action'],
                rule['order'],
                itype=rule.get('type', None),
                iq=rule.get('iq', None),
                message=rule.get('message', None),
                presence_in=rule.get(
                    'presence_in',
                    rule.get('presence-in', None)
                ),
                presence_out=rule.get(
                    'presence_out',
                    rule.get('presence-out', None)
                )
            )
        return iq.send(timeout=timeout, callback=callback)

    def remove_list(self, name: str, timeout: Optional[int] = None,
                    callback: Optional[Callable] = None) -> Future:
        iq = self.xmpp.Iq()
        iq['type'] = 'set'
        iq['privacy']['list']['name'] = name
        return iq.send(timeout=timeout, callback=callback)
