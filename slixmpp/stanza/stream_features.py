
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2010  Nathanael C. Fritz
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from slixmpp.xmlstream import StanzaBase, ElementBase
from typing import ClassVar, Dict, Type, List


class StreamFeatures(StanzaBase):
    """Stream feature element"""

    name = 'features'
    namespace = 'http://etherx.jabber.org/streams'
    interfaces = {'features', 'required', 'optional'}
    sub_interfaces = interfaces
    plugin_attrib_map: ClassVar[Dict[str, Type[ElementBase]]] = {}
    plugin_tag_map: ClassVar[Dict[str, Type[ElementBase]]] = {}

    def setup(self, xml):
        StanzaBase.setup(self, xml)
        self.values = self.values

    def get_features(self) -> Dict[str, ElementBase]:
        features = {}
        for (name, lang), plugin in self.plugins.items():
            features[name] = plugin
        return features

    def set_features(self, value):
        pass

    def del_features(self):
        pass

    def get_required(self) -> List[ElementBase]:
        features = self.get_features()
        return [f for n, f in features.items() if f['required']]

    def get_optional(self) -> List[ElementBase]:
        features = self.get_features()
        return [f for n, f in features.items() if not f['required']]
