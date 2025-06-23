# Slixmpp: The Slick XMPP Library
# Copyright (C) 2010 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from typing import (
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
    Union,
    Dict,
)
from slixmpp.xmlstream import ElementBase, ET

IdentityType = Tuple[str, str, Optional[str], Optional[str]]


class DiscoInfo(ElementBase):

    """
    XMPP allows for users and agents to find the identities and features
    supported by other entities in the XMPP network through service discovery,
    or "disco". In particular, the "disco#info" query type for <iq> stanzas is
    used to request the list of identities and features offered by a JID.

    An identity is a combination of a category and type, such as the 'client'
    category with a type of 'pc' to indicate the agent is a human operated
    client with a GUI, or a category of 'gateway' with a type of 'aim' to
    identify the agent as a gateway for the legacy AIM protocol. See
    `XMPP Registrar Disco Categories`_ for a full list of
    accepted category and type combinations.

    .. _XMPP Registrar Disco Categories: <http://xmpp.org/registrar/disco-categories.html>

    Features are simply a set of the namespaces that identify the supported
    features. For example, a client that supports service discovery will
    include the feature ``http://jabber.org/protocol/disco#info``.

    Since clients and components may operate in several roles at once, identity
    and feature information may be grouped into "nodes". If one were to write
    all of the identities and features used by a client, then node names would
    be like section headings.

    Example disco#info stanza:

    .. code-block:: xml

        <iq type="get">
          <query xmlns="http://jabber.org/protocol/disco#info" />
        </iq>

        <iq type="result">
          <query xmlns="http://jabber.org/protocol/disco#info">
            <identity category="client" type="bot" name="Slixmpp Bot" />
            <feature var="http://jabber.org/protocol/disco#info" />
            <feature var="jabber:x:data" />
            <feature var="urn:xmpp:ping" />
          </query>
        </iq>
    """

    name = 'query'
    namespace = 'http://jabber.org/protocol/disco#info'
    plugin_attrib = 'disco_info'
    #: Stanza interfaces:
    #:
    #: - ``node``: The name of the node to either query or return the info from
    #: - ``identities``: A set of 4-tuples, where each tuple contains the
    #:   category, type, xml:lang and name of an identity
    #: - ``features``: A set of namespaces for features
    #:
    interfaces = {'node', 'features', 'identities'}
    lang_interfaces = {'identities'}

    # Cache identities and features
    _identities: Set[Tuple[str, str, Optional[str]]]
    _features: Set[str]

    def setup(self, xml: Optional[ET.ElementTree] = None):
        """
        Populate the stanza object using an optional XML object.

        Overrides ElementBase.setup

        Caches identity and feature information.

        :param xml: Use an existing XML object for the stanza's values.
        """
        ElementBase.setup(self, xml)

        self._identities = {id[0:3] for id in self['identities']}
        self._features = self['features']

    def add_identity(self, category: str, itype: str,
                     name: Optional[str] = None, lang: Optional[str] = None
                     ) -> bool:
        """
        Add a new identity element. Each identity must be unique
        in terms of all four identity components.

        Multiple, identical category/type pairs are allowed only
        if the xml:lang values are different. Likewise, multiple
        category/type/xml:lang pairs are allowed so long as the names
        are different. In any case, a category and type are required.

        :param category: The general category to which the agent belongs.
        :param itype: A more specific designation with the category.
        :param name: Optional human readable name for this identity.
        :param lang: Optional standard xml:lang value.
        """
        identity = (category, itype, lang)
        if identity not in self._identities:
            self._identities.add(identity)
            id_xml = ET.Element('{%s}identity' % self.namespace)
            id_xml.attrib['category'] = category
            id_xml.attrib['type'] = itype
            if lang:
                id_xml.attrib['{%s}lang' % self.xml_ns] = lang
            if name:
                id_xml.attrib['name'] = name
            self.xml.insert(0, id_xml)
            return True
        return False

    def del_identity(self, category: str, itype: str, name=None,
                     lang: Optional[str] = None) -> bool:
        """
        Remove a given identity.

        :param category: The general category to which the agent belonged.
        :param itype: A more specific designation with the category.
        :param name: Optional human readable name for this identity.
        :param lang: Optional, standard xml:lang value.
        """
        identity = (category, itype, lang)
        if identity in self._identities:
            self._identities.remove(identity)
            for id_xml in self.xml.findall('{%s}identity' % self.namespace):
                id = (id_xml.attrib['category'],
                      id_xml.attrib['type'],
                      id_xml.attrib.get('{%s}lang' % self.xml_ns, None))
                if id == identity:
                    self.xml.remove(id_xml)
                    return True
        return False

    def dict_identities(self, lang: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Return the list of all identities, each one as a dict with
        category, type, xml_lang, and name keys.

        :param lang: If there is a need to filter identities by lang.
        """
        ids = self.get_identities(lang=lang, dedupe=True)
        dict_ids = []
        for identity in ids:
            dict_ids.append({
                'category': identity[0],
                'type': identity[1],
                'xml_lang': identity[2],
                'name': identity[3],
            })
        return dict_ids

    def get_identities(self, lang: Optional[str] = None, dedupe: bool = True
                       ) -> Iterable[IdentityType]:
        """
        Return a set of all identities in tuple form as so:

            (category, type, lang, name)

        If a language was specified, only return identities using
        that language.

        :param lang: Optional, standard xml:lang value.
        :param dedupe: If True, de-duplicate identities, otherwise
                       return a list of all identities.
        """
        identities: Union[List[IdentityType], Set[IdentityType]]
        if dedupe:
            identities = set()
        else:
            identities = []
        for id_xml in self.xml.findall('{%s}identity' % self.namespace):
            xml_lang = id_xml.attrib.get('{%s}lang' % self.xml_ns, None)
            category = id_xml.attrib.get('category', None)
            type_ = id_xml.attrib.get('type', None)
            name = id_xml.attrib.get('name', None)
            if lang is None or xml_lang == lang:
                id = (category, type_, xml_lang, name)
                if isinstance(identities, set):
                    identities.add(id)
                else:
                    identities.append(id)
        return identities

    def set_identities(self, identities: Iterable[IdentityType],
                       lang: Optional[str] = None):
        """
        Add or replace all identities. The identities must be a in set
        where each identity is a tuple of the form:

            (category, type, lang, name)

        If a language is specifified, any identities using that language
        will be removed to be replaced with the given identities.

        .. note::

            An identity's language will not be changed regardless of
            the value of lang.

        :param identities: A set of identities in tuple form.
        :param lang: Optional, standard xml:lang value.
        """
        self.del_identities(lang)
        for identity in identities:
            category, itype, lang, name = identity
            self.add_identity(category, itype, name, lang)

    def del_identities(self, lang: Optional[str] = None):
        """
        Remove all identities. If a language was specified, only
        remove identities using that language.

        :param lang: Optional, standard xml:lang value.
        """
        for id_xml in self.xml.findall('{%s}identity' % self.namespace):
            if lang is None:
                self.xml.remove(id_xml)
            elif id_xml.attrib.get('{%s}lang' % self.xml_ns, None) == lang:
                self._identities.remove((
                    id_xml.attrib['category'],
                    id_xml.attrib['type'],
                    id_xml.attrib.get('{%s}lang' % self.xml_ns, None)))
                self.xml.remove(id_xml)

    def add_feature(self, feature: str) -> bool:
        """
        Add a single, new feature.

        :param feature: The namespace of the supported feature.
        """
        if feature not in self._features:
            self._features.add(feature)
            feature_xml = ET.Element('{%s}feature' % self.namespace)
            feature_xml.attrib['var'] = feature
            self.xml.append(feature_xml)
            return True
        return False

    def del_feature(self, feature: str) -> bool:
        """
        Remove a single feature.

        :param feature: The namespace of the removed feature.
        """
        if feature in self._features:
            self._features.remove(feature)
            for feature_xml in self.xml.findall('{%s}feature' % self.namespace):
                if feature_xml.attrib['var'] == feature:
                    self.xml.remove(feature_xml)
                    return True
        return False

    def get_features(self, dedupe: bool = True) -> Iterable[str]:
        """Return the set of all supported features."""
        features: Union[List[str], Set[str]]
        if dedupe:
            features = set()
        else:
            features = []
        for feature_xml in self.xml.findall('{%s}feature' % self.namespace):
            feature = feature_xml.attrib.get('var', None)
            if feature:
                if isinstance(features, set):
                    features.add(feature)
                else:
                    features.append(feature)
        return features

    def set_features(self, features: Iterable[str]):
        """
        Add or replace the set of supported features.

        :param features: The new set of supported features.
        """
        self.del_features()
        for feature in features:
            self.add_feature(feature)

    def del_features(self):
        """Remove all features."""
        self._features = set()
        for feature_xml in self.xml.findall('{%s}feature' % self.namespace):
            self.xml.remove(feature_xml)
