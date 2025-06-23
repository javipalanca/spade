# Slixmpp: The Slick XMPP Library
# Copyright (C) 2021 Mathieu Pasquet
# This file is part of Slixmpp.
# See the file LICENSE for copying permissio
from typing import (
    Iterable,
    Set,
)

from slixmpp.jid import JID
from slixmpp.xmlstream import ElementBase, ET


class Preferences(ElementBase):
    """MAM Preferences payload.

    .. code-block:: xml

        <iq type='set' id='juliet3'>
          <prefs xmlns='urn:xmpp:mam:2' default='roster'>
            <always>
              <jid>romeo@montague.lit</jid>
            </always>
            <never>
              <jid>montague@montague.lit</jid>
            </never>
          </prefs>
        </iq>

    """
    name = 'prefs'
    namespace = 'urn:xmpp:mam:2'
    plugin_attrib = 'mam_prefs'
    #: Available interfaces:
    #:
    #: - ``default``: Default MAM policy (must be one of 'roster', 'always',
    #:   'never'
    #: - ``always``  (``List[JID]``): list of JIDs to always store
    #:   conversations with.
    #: - ``never``  (``List[JID]``): list of JIDs to never store
    #:   conversations with.
    interfaces = {'default', 'always', 'never'}
    sub_interfaces = {'always', 'never'}

    def get_always(self) -> Set[JID]:
        results = set()

        jids = self.xml.findall('{%s}always/{%s}jid' % (
            self.namespace, self.namespace))

        for jid in jids:
            results.add(JID(jid.text))

        return results

    def set_always(self, value: Iterable[JID]):
        self._set_sub_text('always', '', keep=True)
        always = self.xml.find('{%s}always' % self.namespace)
        always.clear()

        if not isinstance(value, (list, set)):
            value = [value]

        for jid in value:
            jid_xml = ET.Element('{%s}jid' % self.namespace)
            jid_xml.text = str(jid)
            always.append(jid_xml)

    def get_never(self) -> Set[JID]:
        results = set()

        jids = self.xml.findall('{%s}never/{%s}jid' % (
            self.namespace, self.namespace))

        for jid in jids:
            results.add(JID(jid.text))

        return results

    def set_never(self, value: Iterable[JID]):
        self._set_sub_text('never', '', keep=True)
        never = self.xml.find('{%s}never' % self.namespace)
        never.clear()

        if not isinstance(value, (list, set)):
            value = [value]

        for jid in value:
            jid_xml = ET.Element('{%s}jid' % self.namespace)
            jid_xml.text = str(jid)
            never.append(jid_xml)
