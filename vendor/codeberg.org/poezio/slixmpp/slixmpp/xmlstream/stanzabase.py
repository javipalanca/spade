# slixmpp.xmlstream.stanzabase
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# module implements a wrapper layer for XML objects
# that allows them to be treated like dictionaries.
# Part of Slixmpp: The Slick XMPP Library
# :copyright: (c) 2011 Nathanael C. Fritz
# :license: MIT, see LICENSE for more details
from __future__ import annotations

import copy
import logging
import weakref
from typing import (
    cast,
    Any,
    Callable,
    ClassVar,
    Coroutine,
    Dict,
    List,
    Iterable,
    Optional,
    Set,
    Tuple,
    Type,
    TYPE_CHECKING,
    Union,
)
from weakref import ReferenceType
from xml.etree import ElementTree as ET

from slixmpp.types import JidStr
from slixmpp.xmlstream import JID
from slixmpp.xmlstream.tostring import tostring


if TYPE_CHECKING:
    from slixmpp.xmlstream import XMLStream


log = logging.getLogger(__name__)


# Used to check if an argument is an XML object.
XML_TYPE = type(ET.Element('xml'))


XML_NS = 'http://www.w3.org/XML/1998/namespace'


STRICT_INTERFACE = False


def register_stanza_plugin(stanza: Type[ElementBase], plugin: Type[ElementBase],
                           iterable: bool = False, overrides: bool = False) -> None:
    """
    Associate a stanza object as a plugin for another stanza.

    >>> from slixmpp.xmlstream import register_stanza_plugin
    >>> register_stanza_plugin(Iq, CustomStanza)

    Plugin stanzas marked as iterable will be included in the list of
    substanzas for the parent, using ``parent['substanzas']``. If the
    attribute ``plugin_multi_attrib`` was defined for the plugin, then
    the substanza set can be filtered to only instances of the plugin
    class. For example, given a plugin class ``Foo`` with
    ``plugin_multi_attrib = 'foos'`` then::

        parent['foos']

    would return a collection of all ``Foo`` substanzas.

    :param class stanza: The class of the parent stanza.
    :param class plugin: The class of the plugin stanza.
    :param bool iterable: Indicates if the plugin stanza should be
                          included in the parent stanza's iterable
                          ``'substanzas'`` interface results.
    :param bool overrides: Indicates if the plugin should be allowed
                           to override the interface handlers for
                           the parent stanza, based on the plugin's
                           ``overrides`` field.

    .. versionadded:: 1.0-Beta1
        Made ``register_stanza_plugin`` the default name. The prior
        ``registerStanzaPlugin`` function name remains as an alias.
    """
    tag = "{%s}%s" % (plugin.namespace, plugin.name)

    # Prevent weird memory reference gotchas by ensuring
    # that the parent stanza class has its own set of
    # plugin info maps and is not using the mappings from
    # an ancestor class (like ElementBase).
    plugin_info = ('plugin_attrib_map', 'plugin_tag_map',
                   'plugin_iterables', 'plugin_overrides')
    for attr in plugin_info:
        info = getattr(stanza, attr)
        setattr(stanza, attr, info.copy())

    stanza.plugin_attrib_map[plugin.plugin_attrib] = plugin
    stanza.plugin_tag_map[tag] = plugin

    if iterable:
        stanza.plugin_iterables.add(plugin)
        if plugin.plugin_multi_attrib:
            multiplugin = multifactory(plugin, plugin.plugin_multi_attrib)
            register_stanza_plugin(stanza, multiplugin)
    if overrides:
        for interface in plugin.overrides:
            stanza.plugin_overrides[interface] = plugin.plugin_attrib


def multifactory(stanza: Type[ElementBase], plugin_attrib: str) -> Type[ElementBase]:
    """
    Returns a ElementBase class for handling reoccuring child stanzas
    """

    def plugin_filter(self: Multi) -> Callable[..., bool]:
        return lambda x: isinstance(x, self._multistanza)

    def plugin_lang_filter(self: Multi, lang: Optional[str]) -> Callable[..., bool]:
        return lambda x: isinstance(x, self._multistanza) and \
                         x['lang'] == lang

    class Multi(ElementBase):
        """
        Template class for multifactory
        """
        _multistanza: Type[ElementBase]

        def setup(self, xml: Optional[ET.Element] = None) -> bool:
            self.xml = ET.Element('')
            return False

    def get_multi(self: Multi, lang: Optional[str] = None) -> List[ElementBase]:
        parent = fail_without_parent(self)
        if not lang or lang == '*':
            res = filter(plugin_filter(self), parent)
        else:
            res = filter(plugin_lang_filter(self, lang), parent)
        return list(res)

    def set_multi(self: Multi, val: Iterable[ElementBase], lang: Optional[str] = None) -> None:
        parent = fail_without_parent(self)
        del_multi = getattr(self, 'del_%s' % plugin_attrib)
        del_multi(lang)
        for sub in val:
            parent.append(sub)

    def fail_without_parent(self: Multi) -> ElementBase:
        parent = None
        if self.parent:
            parent = self.parent()
        if not parent:
            raise ValueError('No stanza parent for multifactory')
        return parent

    def del_multi(self: Multi, lang: Optional[str] = None) -> None:
        parent = fail_without_parent(self)
        if not lang or lang == '*':
            res = list(filter(plugin_filter(self), parent))
        else:
            res = list(filter(plugin_lang_filter(self, lang), parent))
        if not res:
            del parent.plugins[(plugin_attrib, None)]
            parent.loaded_plugins.remove(plugin_attrib)
            try:
                parent.xml.remove(self.xml)
            except ValueError:
                pass
        else:
            for stanza in list(res):
                parent.iterables.remove(stanza)
                parent.xml.remove(stanza.xml)

    Multi.is_extension = True
    Multi.plugin_attrib = plugin_attrib
    Multi._multistanza = stanza
    Multi.interfaces = {plugin_attrib}
    Multi.lang_interfaces = {plugin_attrib}
    setattr(Multi, "get_%s" % plugin_attrib, get_multi)
    setattr(Multi, "set_%s" % plugin_attrib, set_multi)
    setattr(Multi, "del_%s" % plugin_attrib, del_multi)
    return Multi


def fix_ns(xpath: str, split: bool = False, propagate_ns: bool = True,
           default_ns: str = '') -> Union[str, List[str]]:
    """Apply the stanza's namespace to elements in an XPath expression.

    :param string xpath: The XPath expression to fix with namespaces.
    :param bool split: Indicates if the fixed XPath should be left as a
                       list of element names with namespaces. Defaults to
                       False, which returns a flat string path.
    :param bool propagate_ns: Overrides propagating parent element
                              namespaces to child elements. Useful if
                              you wish to simply split an XPath that has
                              non-specified namespaces, and child and
                              parent namespaces are known not to always
                              match. Defaults to True.
    """
    fixed = []
    # Split the XPath into a series of blocks, where a block
    # is started by an element with a namespace.
    ns_blocks = xpath.split('{')
    for ns_block in ns_blocks:
        if '}' in ns_block:
            # Apply the found namespace to following elements
            # that do not have namespaces.
            ns_block_split = ns_block.split('}')
            namespace = ns_block_split[0]
            elements = ns_block_split[1].split('/')
        else:
            # Apply the stanza's namespace to the following
            # elements since no namespace was provided.
            namespace = default_ns
            elements = ns_block.split('/')

        for element in elements:
            if element:
                # Skip empty entry artifacts from splitting.
                if propagate_ns and element[0] != '*':
                    tag = '{%s}%s' % (namespace, element)
                else:
                    tag = element
                fixed.append(tag)
    if split:
        return fixed
    return '/'.join(fixed)


class ElementBase(object):

    """
    The core of Slixmpp's stanza XML manipulation and handling is provided
    by ElementBase. ElementBase wraps XML ElementTree objects and enables
    access to the XML contents through dictionary syntax, similar in style
    to the Ruby XMPP library Blather's stanza implementation.

    Stanzas are defined by their name, namespace, and interfaces. For
    example, a simplistic Message stanza could be defined as::

        >>> class Message(ElementBase):
        ...     name = "message"
        ...     namespace = "jabber:client"
        ...     interfaces = {'to', 'from', 'type', 'body'}
        ...     sub_interfaces = {'body'}

    The resulting Message stanza's contents may be accessed as so::

        >>> message['to'] = "user@example.com"
        >>> message['body'] = "Hi!"
        >>> message['body']
        "Hi!"
        >>> del message['body']
        >>> message['body']
        ""

    The interface values map to either custom access methods, stanza
    XML attributes, or (if the interface is also in sub_interfaces) the
    text contents of a stanza's subelement.

    Custom access methods may be created by adding methods of the
    form "getInterface", "setInterface", or "delInterface", where
    "Interface" is the titlecase version of the interface name.

    Stanzas may be extended through the use of plugins. A plugin
    is simply a stanza that has a plugin_attrib value. For example::

        >>> class MessagePlugin(ElementBase):
        ...     name = "custom_plugin"
        ...     namespace = "custom"
        ...     interfaces = {'useful_thing', 'custom'}
        ...     plugin_attrib = "custom"

    The plugin stanza class must be associated with its intended
    container stanza by using register_stanza_plugin as so::

        >>> register_stanza_plugin(Message, MessagePlugin)

    The plugin may then be accessed as if it were built-in to the parent
    stanza::

        >>> message['custom']['useful_thing'] = 'foo'

    If a plugin provides an interface that is the same as the plugin's
    plugin_attrib value, then the plugin's interface may be assigned
    directly from the parent stanza, as shown below, but retrieving
    information will require all interfaces to be used, as so::

        >>> # Same as using message['custom']['custom']
        >>> message['custom'] = 'bar'
        >>> # Must use all interfaces
        >>> message['custom']['custom']
        'bar'

    If the plugin sets :attr:`is_extension` to ``True``, then both setting
    and getting an interface value that is the same as the plugin's
    plugin_attrib value will work, as so::

        >>> message['custom'] = 'bar'  # Using is_extension=True
        >>> message['custom']
        'bar'


    :param xml: Initialize the stanza object with an existing XML object.
    :param parent: Optionally specify a parent stanza object will
                   contain this substanza.
    """

    #: The XML tag name of the element, not including any namespace
    #: prefixes. For example, an :class:`ElementBase` object for
    #: ``<message />`` would use ``name = 'message'``.
    name: ClassVar[str] = 'stanza'

    #: The XML namespace for the element. Given ``<foo xmlns="bar" />``,
    #: then ``namespace = "bar"`` should be used. The default namespace
    #: is ``jabber:client`` since this is being used in an XMPP library.
    namespace: str = 'jabber:client'

    #: For :class:`ElementBase` subclasses which are intended to be used
    #: as plugins, the ``plugin_attrib`` value defines the plugin name.
    #: Plugins may be accessed by using the ``plugin_attrib`` value as
    #: the interface. An example using ``plugin_attrib = 'foo'``::
    #:
    #:     register_stanza_plugin(Message, FooPlugin)
    #:     msg = Message()
    #:     msg['foo']['an_interface_from_the_foo_plugin']
    plugin_attrib: ClassVar[str] = 'plugin'

    #: For :class:`ElementBase` subclasses that are intended to be an
    #: iterable group of items, the ``plugin_multi_attrib`` value defines
    #: an interface for the parent stanza which returns the entire group
    #: of matching substanzas. So the following are equivalent::
    #:
    #:     # Given stanza class Foo, with plugin_multi_attrib = 'foos'
    #:     parent['foos']
    #:     filter(isinstance(item, Foo), parent['substanzas'])
    plugin_multi_attrib: ClassVar[str] = ''

    #: The set of keys that the stanza provides for accessing and
    #: manipulating the underlying XML object. This set may be augmented
    #: with the :attr:`plugin_attrib` value of any registered
    #: stanza plugins.
    interfaces: ClassVar[Set[str]] = {'type', 'to', 'from', 'id', 'payload'}

    #: A subset of :attr:`interfaces` which maps interfaces to direct
    #: subelements of the underlying XML object. Using this set, the text
    #: of these subelements may be set, retrieved, or removed without
    #: needing to define custom methods.
    sub_interfaces: ClassVar[Set[str]] = set()

    #: A subset of :attr:`interfaces` which maps the presence of
    #: subelements to boolean values. Using this set allows for quickly
    #: checking for the existence of empty subelements like ``<required />``.
    #:
    #: .. versionadded:: 1.1
    bool_interfaces: ClassVar[Set[str]] = set()

    #: .. versionadded:: 1.1.2
    lang_interfaces: ClassVar[Set[str]] = set()

    #: In some cases you may wish to override the behaviour of one of the
    #: parent stanza's interfaces. The ``overrides`` list specifies the
    #: interface name and access method to be overridden. For example,
    #: to override setting the parent's ``'condition'`` interface you
    #: would use::
    #:
    #:     overrides = ['set_condition']
    #:
    #: Getting and deleting the ``'condition'`` interface would not
    #: be affected.
    #:
    #: .. versionadded:: 1.0-Beta5
    overrides: ClassVar[List[str]] = []

    #: If you need to add a new interface to an existing stanza, you
    #: can create a plugin and set ``is_extension = True``. Be sure
    #: to set the :attr:`plugin_attrib` value to the desired interface
    #: name, and that it is the only interface listed in
    #: :attr:`interfaces`. Requests for the new interface from the
    #: parent stanza will be passed to the plugin directly.
    #:
    #: .. versionadded:: 1.0-Beta5
    is_extension: ClassVar[bool] = False

    #: A map of interface operations to the overriding functions.
    #: For example, after overriding the ``set`` operation for
    #: the interface ``body``, :attr:`plugin_overrides` would be::
    #:
    #:     {'set_body': <some function>}
    #:
    #: .. versionadded: 1.0-Beta5
    plugin_overrides: ClassVar[Dict[str, str]] = {}

    #: A mapping of the :attr:`plugin_attrib` values of registered
    #: plugins to their respective classes.
    plugin_attrib_map: ClassVar[Dict[str, Type[ElementBase]]] = {}

    #: A mapping of root element tag names (in ``'{namespace}elementname'``
    #: format) to the plugin classes responsible for them.
    plugin_tag_map: ClassVar[Dict[str, Type[ElementBase]]] = {}

    #: The set of stanza classes that can be iterated over using
    #: the 'substanzas' interface. Classes are added to this set
    #: when registering a plugin with ``iterable=True``::
    #:
    #:     register_stanza_plugin(DiscoInfo, DiscoItem, iterable=True)
    #:
    #: .. versionadded:: 1.0-Beta5
    plugin_iterables: ClassVar[Set[Type[ElementBase]]] = set()

    #: The default XML namespace: ``http://www.w3.org/XML/1998/namespace``.
    xml_ns: ClassVar[str] = XML_NS

    plugins: Dict[Tuple[str, Optional[str]], ElementBase]
    #: The underlying XML object for the stanza. It is a standard
    #: :class:`xml.etree.ElementTree` object.
    xml: ET.Element
    _index: int
    loaded_plugins: Set[str]
    iterables: List[ElementBase]
    tag: str
    parent: Optional[ReferenceType[ElementBase]]

    def __init__(self, xml: Optional[ET.Element] = None, parent: Union[Optional[ElementBase], ReferenceType[ElementBase]] = None):
        self._index = 0

        if xml is not None:
            self.xml = xml

        #: An ordered dictionary of plugin stanzas, mapped by their
        #: :attr:`plugin_attrib` value.
        self.plugins = {}
        self.loaded_plugins = set()

        #: A list of child stanzas whose class is included in
        #: :attr:`plugin_iterables`.
        self.iterables = []

        #: The name of the tag for the stanza's root element. It is the
        #: same as calling :meth:`tag_name()` and is formatted as
        #: ``'{namespace}elementname'``.
        self.tag = self.tag_name()

        #: A :class:`weakref.weakref` to the parent stanza, if there is one.
        #: If not, then :attr:`parent` is ``None``.
        self.parent = None
        if parent is not None:
            if not isinstance(parent, weakref.ReferenceType):
                self.parent = weakref.ref(parent)
            else:
                self.parent = parent

        if self.setup(xml):
            # If we generated our own XML, then everything is ready.
            return

        # Initialize values using provided XML
        for child in self.xml:
            if child.tag in self.plugin_tag_map:
                plugin_class = self.plugin_tag_map[child.tag]
                self.init_plugin(plugin_class.plugin_attrib,
                                 existing_xml=child,
                                 reuse=False)

    def setup(self, xml: Optional[ET.Element] = None) -> bool:
        """Initialize the stanza's XML contents.

        Will return ``True`` if XML was generated according to the stanza's
        definition instead of building a stanza object from an existing
        XML object.

        :param xml: An existing XML object to use for the stanza's content
                    instead of generating new XML.
        """
        if hasattr(self, 'xml'):
            return False
        if not hasattr(self, 'xml') and xml is not None:
            self.xml = xml
            return False


        # Generate XML from the stanza definition
        last_xml = ET.Element('')
        for ename in self.name.split('/'):
            new = ET.Element("{%s}%s" % (self.namespace, ename))
            if not hasattr(self, 'xml'):
                self.xml = new
            else:
                last_xml.append(new)
            last_xml = new
        if self.parent is not None:
            parent = self.parent()
            if parent:
                parent.xml.append(self.xml)

        # We had to generate XML
        return True

    def enable(self, attrib: str, lang: Optional[str] = None) -> ElementBase:
        """Enable and initialize a stanza plugin.

        Alias for :meth:`init_plugin`.

        :param string attrib: The :attr:`plugin_attrib` value of the
                              plugin to enable.
        """
        return self.init_plugin(attrib, lang)

    def __contains__(self, name: str) -> bool:
        """
        Check if the stanza contains a specific plugin.
        """
        lang = None
        if '|' in name:
            name, lang, *_ = name.split('|')
        return self.get_plugin(name, lang=lang, check=True) is not None

    def get_plugin(self, name: str, lang: Optional[str] = None, check: bool = False) -> Optional[ElementBase]:
        """Retrieve a stanza plugin.

        :param check: Return None instead of creating the object if True.
        :param name: Stanza plugin attribute name.
        :param lang: xml:lang of the element to retrieve.
        """
        if lang is None:
            lang = self.get_lang()

        if name not in self.plugin_attrib_map:
            return None

        plugin_class = self.plugin_attrib_map[name]

        if plugin_class.is_extension:
            if (name, None) in self.plugins:
                return self.plugins[(name, None)]
            else:
                return None if check else self.init_plugin(name, lang)
        else:
            if (name, lang) in self.plugins:
                return self.plugins[(name, lang)]
            else:
                return None if check else self.init_plugin(name, lang)

    def init_plugin(self, attrib: str, lang: Optional[str] = None,
                    existing_xml: Optional[ET.Element] = None,
                    reuse: bool = True,
                    element: Optional[ElementBase] = None) -> ElementBase:
        """Enable and initialize a stanza plugin.

        :param string attrib: The :attr:`plugin_attrib` value of the
                              plugin to enable.
        """
        default_lang = self.get_lang()
        if not lang:
            lang = default_lang

        plugin_class = self.plugin_attrib_map[attrib]

        if plugin_class.is_extension and (attrib, None) in self.plugins:
            return self.plugins[(attrib, None)]
        if reuse and (attrib, lang) in self.plugins:
            return self.plugins[(attrib, lang)]

        if element is not None:
            plugin = element
        else:
            plugin = plugin_class(parent=self, xml=existing_xml)

        if plugin.is_extension:
            self.plugins[(attrib, None)] = plugin
        else:
            if lang != default_lang:
                plugin['lang'] = lang
            self.plugins[(attrib, lang)] = plugin

        if plugin_class in self.plugin_iterables:
            self.iterables.append(plugin)
            if plugin_class.plugin_multi_attrib:
                self.init_plugin(plugin_class.plugin_multi_attrib)

        self.loaded_plugins.add(attrib)

        return plugin

    def _get_stanza_values(self) -> Dict[str, Any]:
        """Return A JSON/dictionary version of the XML content
        exposed through the stanza's interfaces::

            >>> msg = Message()
            >>> msg.values
            {'body': '', 'from': , 'mucnick': '', 'mucroom': '',
            'to': , 'type': 'normal', 'id': '', 'subject': ''}

        Likewise, assigning to :attr:`values` will change the XML
        content::

            >>> msg = Message()
            >>> msg.values = {'body': 'Hi!', 'to': 'user@example.com'}
            >>> msg
            '<message to="user@example.com"><body>Hi!</body></message>'

        .. versionadded:: 1.0-Beta1
        """
        values = {}
        values['lang'] = self['lang']
        for interface in self.interfaces:
            if isinstance(self[interface], JID):
                values[interface] = self[interface].jid
            else:
                values[interface] = self[interface]
            if interface in self.lang_interfaces:
                values['%s|*' % interface] = self['%s|*' % interface]
        for plugin, stanza in self.plugins.items():
            lang = stanza['lang']
            if lang:
                values['%s|%s' % (plugin[0], lang)] = stanza.values
            else:
                values[plugin[0]] = stanza.values
        if self.iterables:
            iterables = []
            for stanza in self.iterables:
                iterables.append(stanza.values)
                iterables[-1]['__childtag__'] = stanza.tag
            values['substanzas'] = iterables
        return values

    def _set_stanza_values(self, values: Dict[str, Any]) -> ElementBase:
        """Set multiple stanza interface values using a dictionary.

        Stanza plugin values may be set using nested dictionaries.

        :param values: A dictionary mapping stanza interface with values.
                       Plugin interfaces may accept a nested dictionary that
                       will be used recursively.

        .. versionadded:: 1.0-Beta1
        """
        iterable_interfaces = [p.plugin_attrib for \
                                    p in self.plugin_iterables]

        if 'lang' in values:
            self['lang'] = values['lang']

        if 'substanzas' in values:
            # Remove existing substanzas
            for stanza in self.iterables:
                try:
                    self.xml.remove(stanza.xml)
                except ValueError:
                    pass
            self.iterables = []

            # Add new substanzas
            for subdict in values['substanzas']:
                if '__childtag__' in subdict:
                    for subclass in self.plugin_iterables:
                        child_tag = "{%s}%s" % (subclass.namespace,
                                                subclass.name)
                        if subdict['__childtag__'] == child_tag:
                            sub = subclass(parent=self)
                            sub.values = subdict
                            self.iterables.append(sub)

        for interface, value in values.items():
            full_interface = interface
            interface_lang = ('%s|' % interface).split('|')
            interface = interface_lang[0]
            lang = interface_lang[1] or self.get_lang()

            if interface == 'lang':
                continue
            elif interface == 'substanzas':
                continue
            elif interface in self.interfaces:
                self[full_interface] = value
            elif interface in self.plugin_attrib_map:
                if interface not in iterable_interfaces:
                    plugin = self.get_plugin(interface, lang)
                    if plugin:
                        plugin.values = value
        return self

    def __getitem__(self, full_attrib: str) -> Any:
        """Return the value of a stanza interface using dict-like syntax.

        Example::

            >>> msg['body']
            'Message contents'

        Stanza interfaces are typically mapped directly to the underlying XML
        object, but can be overridden by the presence of a ``get_attrib``
        method (or ``get_foo`` where the interface is named ``'foo'``, etc).

        The search order for interface value retrieval for an interface
        named ``'foo'`` is:

            1. The list of substanzas (``'substanzas'``)
            2. The result of calling the ``get_foo`` override handler.
            3. The result of calling ``get_foo``.
            4. The result of calling ``getFoo``.
            5. The contents of the ``foo`` subelement, if ``foo`` is listed
               in :attr:`sub_interfaces`.
            6. True or False depending on the existence of a ``foo``
               subelement and ``foo`` is in :attr:`bool_interfaces`.
            7. The value of the ``foo`` attribute of the XML object.
            8. The plugin named ``'foo'``
            9. An empty string.

        :param string full_attrib: The name of the requested stanza interface.
        """
        attrib, lang, *_ = ('%s|' % full_attrib).split('|')

        kwargs = {'lang': lang} if lang and attrib in self.lang_interfaces else {}

        if attrib == 'substanzas':
            return self.iterables
        elif attrib in self.interfaces or attrib == 'lang':
            get_method = "get_%s" % attrib.lower()

            if self.plugin_overrides:
                name = self.plugin_overrides.get(get_method, None)
                if name:
                    plugin = self.get_plugin(name, lang)
                    if plugin:
                        handler = getattr(plugin, get_method, None)
                        if handler:
                            return handler(**kwargs)

            if hasattr(self, get_method):
                return getattr(self, get_method)(**kwargs)
            else:
                if attrib in self.sub_interfaces:
                    return self._get_sub_text(attrib, lang=lang)
                elif attrib in self.bool_interfaces:
                    elem = self.xml.find('{%s}%s' % (self.namespace, attrib))
                    return elem is not None
                else:
                    return self._get_attr(attrib)
        elif attrib in self.plugin_attrib_map:
            plugin = self.get_plugin(attrib, lang)
            if plugin and plugin.is_extension:
                return plugin[full_attrib]
            return plugin
        else:
            # XXX: This is legacy from SleekXMPP
            #      We've probably missed the opportunity to fix it
            logging.warning("Unknown stanza interface: %s" % full_attrib)
            if STRICT_INTERFACE:
                raise ValueError(f'Unknown stanza interface: {full_attrib}')
            return ''

    def __setitem__(self, attrib: str, value: Any) -> Any:
        """Set the value of a stanza interface using dictionary-like syntax.

        Example::

            >>> msg['body'] = "Hi!"
            >>> msg['body']
            'Hi!'

        Stanza interfaces are typically mapped directly to the underlying XML
        object, but can be overridden by the presence of a ``set_attrib``
        method (or ``set_foo`` where the interface is named ``'foo'``, etc).

        The effect of interface value assignment for an interface
        named ``'foo'`` will be one of:

            1. Delete the interface's contents if the value is None.
            2. Call the ``set_foo`` override handler, if it exists.
            3. Call ``set_foo``, if it exists.
            4. Call ``setFoo``, if it exists.
            5. Set the text of a ``foo`` element, if ``'foo'`` is
               in :attr:`sub_interfaces`.
            6. Add or remove an empty subelement ``foo``
               if ``foo`` is in :attr:`bool_interfaces`.
            7. Set the value of a top level XML attribute named ``foo``.
            8. Attempt to pass the value to a plugin named ``'foo'`` using
               the plugin's ``'foo'`` interface.
            9. Do nothing.

        :param string attrib: The name of the stanza interface to modify.
        :param value: The new value of the stanza interface.
        """
        full_attrib = attrib
        attrib_lang = ('%s|' % attrib).split('|')
        attrib = attrib_lang[0]
        lang = attrib_lang[1] or None

        kwargs = {}
        if lang and attrib in self.lang_interfaces:
            kwargs['lang'] = lang

        if attrib in self.interfaces or attrib == 'lang':
            if value is not None:
                set_method = "set_%s" % attrib.lower()

                if self.plugin_overrides:
                    name = self.plugin_overrides.get(set_method, None)
                    if name:
                        plugin = self.get_plugin(name, lang)
                        if plugin:
                            handler = getattr(plugin, set_method, None)
                            if handler:
                                return handler(value, **kwargs)

                if hasattr(self, set_method):
                    getattr(self, set_method)(value, **kwargs)
                else:
                    if attrib in self.sub_interfaces:
                        if isinstance(value, JID):
                            value = str(value)
                        if lang == '*':
                            return self._set_all_sub_text(attrib,
                                                          value,
                                                          lang='*')
                        return self._set_sub_text(attrib, text=value,
                                                          lang=lang)
                    elif attrib in self.bool_interfaces:
                        if value:
                            return self._set_sub_text(attrib, '',
                                    keep=True,
                                    lang=lang)
                        else:
                            return self._set_sub_text(attrib, '',
                                    keep=False,
                                    lang=lang)
                    else:
                        self._set_attr(attrib, value)
            else:
                self.__delitem__(attrib)
        elif attrib in self.plugin_attrib_map:
            plugin = self.get_plugin(attrib, lang)
            if plugin:
                plugin[full_attrib] = value
        return self

    def __delitem__(self, attrib: str) -> Any:
        """Delete the value of a stanza interface using dict-like syntax.

        Example::

            >>> msg['body'] = "Hi!"
            >>> msg['body']
            'Hi!'
            >>> del msg['body']
            >>> msg['body']
            ''

        Stanza interfaces are typically mapped directly to the underlyig XML
        object, but can be overridden by the presence of a ``del_attrib``
        method (or ``del_foo`` where the interface is named ``'foo'``, etc).

        The effect of deleting a stanza interface value named ``foo`` will be
        one of:

            1. Call ``del_foo`` override handler, if it exists.
            2. Call ``del_foo``, if it exists.
            3. Call ``delFoo``, if it exists.
            4. Delete ``foo`` element, if ``'foo'`` is in
               :attr:`sub_interfaces`.
            5. Remove ``foo`` element if ``'foo'`` is in
               :attr:`bool_interfaces`.
            6. Delete top level XML attribute named ``foo``.
            7. Remove the ``foo`` plugin, if it was loaded.
            8. Do nothing.

        :param attrib: The name of the affected stanza interface.
        """
        full_attrib = attrib
        attrib_lang = ('%s|' % attrib).split('|')
        attrib = attrib_lang[0]
        lang = attrib_lang[1] or None

        kwargs = {}
        if lang and attrib in self.lang_interfaces:
            kwargs['lang'] = lang

        if attrib in self.interfaces or attrib == 'lang':
            del_method = "del_%s" % attrib.lower()

            if self.plugin_overrides:
                name = self.plugin_overrides.get(del_method, None)
                if name:
                    plugin = self.get_plugin(attrib, lang)
                    if plugin:
                        handler = getattr(plugin, del_method, None)
                        if handler:
                            return handler(**kwargs)

            if hasattr(self, del_method):
                getattr(self, del_method)(**kwargs)
            else:
                if attrib in self.sub_interfaces:
                    return self._del_sub(attrib, lang=lang)
                elif attrib in self.bool_interfaces:
                    return self._del_sub(attrib, lang=lang)
                else:
                    self._del_attr(attrib)
        elif attrib in self.plugin_attrib_map:
            plugin = self.get_plugin(attrib, lang, check=True)
            if not plugin:
                return self
            if plugin.is_extension:
                del plugin[full_attrib]
                del self.plugins[(attrib, None)]
            else:
                del self.plugins[(attrib, plugin['lang'])]
            self.loaded_plugins.remove(attrib)
            try:
                self.xml.remove(plugin.xml)
            except ValueError:
                pass
        return self

    def _set_attr(self, name: str, value: Optional[JidStr]) -> None:
        """Set the value of a top level attribute of the XML object.

        If the new value is None or an empty string, then the attribute will
        be removed.

        :param name: The name of the attribute.
        :param value: The new value of the attribute, or None or '' to
                      remove it.
        """
        if value is None or value == '':
            self.__delitem__(name)
        else:
            if isinstance(value, JID):
                value = str(value)
            self.xml.attrib[name] = value

    def _del_attr(self, name: str) -> None:
        """Remove a top level attribute of the XML object.

        :param name: The name of the attribute.
        """
        if name in self.xml.attrib:
            del self.xml.attrib[name]

    def _get_attr(self, name: str, default: str = '') -> str:
        """Return the value of a top level attribute of the XML object.

        In case the attribute has not been set, a default value can be
        returned instead. An empty string is returned if no other default
        is supplied.

        :param name: The name of the attribute.
        :param default: Optional value to return if the attribute has not
                        been set. An empty string is returned otherwise.
        """
        return self.xml.attrib.get(name, default)

    def _get_sub_text(self, name: str, default: str = '',
                      lang: Optional[str] = None) -> Union[str, Dict[str, str]]:
        """Return the text contents of a sub element.

        In case the element does not exist, or it has no textual content,
        a default value can be returned instead. An empty string is returned
        if no other default is supplied.

        :param name: The name or XPath expression of the element.
        :param default: Optional default to return if the element does
                        not exists. An empty string is returned otherwise.
        """
        name = cast(str, self._fix_ns(name))
        if lang == '*':
            return self._get_all_sub_text(name, default, None)

        default_lang = self.get_lang()
        if not lang:
            lang = default_lang

        stanzas = self.xml.findall(name)
        if not stanzas:
            return default
        result = None
        for stanza in stanzas:
            if stanza.attrib.get('{%s}lang' % XML_NS, default_lang) == lang:
                if stanza.text is None:
                    return default
                result = stanza.text
                break
            if stanza.text:
                result = stanza.text
        if result is not None:
            return result
        return default

    def _get_all_sub_text(self, name: str, default: str = '',
                          lang: Optional[str] = None) -> Dict[str, str]:
        name = cast(str, self._fix_ns(name))

        default_lang = self.get_lang()
        results = {}
        stanzas = self.xml.findall(name)
        if stanzas:
            for stanza in stanzas:
                stanza_lang = stanza.attrib.get('{%s}lang' % XML_NS,
                                                default_lang)
                if not lang or lang == '*' or stanza_lang == lang:
                    if stanza.text is None:
                        text = default
                    else:
                        text = stanza.text
                    results[stanza_lang] = text
        return results

    def _set_sub_text(self, name: str, text: Optional[str] = None,
                      keep: bool = False,
                      lang: Optional[str] = None) -> Optional[ET.Element]:
        """Set the text contents of a sub element.

        In case the element does not exist, a element will be created,
        and its text contents will be set.

        If the text is set to an empty string, or None, then the
        element will be removed, unless keep is set to True.

        :param name: The name or XPath expression of the element.
        :param text: The new textual content of the element. If the text
                     is an empty string or None, the element will be removed
                     unless the parameter keep is True.
        :param keep: Indicates if the element should be kept if its text is
                     removed. Defaults to False.
        """
        default_lang = self.get_lang()
        if lang is None:
            lang = default_lang

        if not text and not keep:
            self._del_sub(name, lang=lang)
            return None

        path = cast(List[str], self._fix_ns(name, split=True))
        name = path[-1]
        parent: Optional[ET.Element] = self.xml

        # The first goal is to find the parent of the subelement, or, if
        # we can't find that, the closest grandparent element.
        missing_path: List[str] = []
        search_order = path[:-1]
        while search_order:
            parent = self.xml.find('/'.join(search_order))
            ename = search_order.pop()
            if parent is not None:
                break
            else:
                missing_path.append(ename)
        missing_path.reverse()

        # Find all existing elements that match the desired
        # element path (there may be multiples due to different
        # languages values).
        if parent is not None:
            elements = self.xml.findall('/'.join(path))
        else:
            parent = self.xml
            elements = []

        # Insert the remaining grandparent elements that don't exist yet.
        for ename in missing_path:
            element = ET.Element(ename)
            parent.append(element)
            parent = element

        # Re-use an existing element with the proper language, if one exists.
        for element in elements:
            elang = element.attrib.get('{%s}lang' % XML_NS, default_lang)
            if not lang and elang == default_lang or lang and lang == elang:
                element.text = text
                return element

        # No useable element exists, so create a new one.
        element = ET.Element(name)
        element.text = text
        if lang and lang != default_lang:
            element.attrib['{%s}lang' % XML_NS] = lang
        parent.append(element)
        return element

    def _set_all_sub_text(self, name: str, values: Dict[str, str],
                          keep: bool = False,
                          lang: Optional[str] = None) -> None:
        self._del_sub(name, lang=lang)
        for value_lang, value in values.items():
            if not lang or lang == '*' or value_lang == lang:
                self._set_sub_text(name, text=value,
                                         keep=keep,
                                         lang=value_lang)

    def _del_sub(self, name: str, all: bool = False, lang: Optional[str] = None) -> None:
        """Remove sub elements that match the given name or XPath.

        If the element is in a path, then any parent elements that become
        empty after deleting the element may also be deleted if requested
        by setting all=True.

        :param name: The name or XPath expression for the element(s) to remove.
        :param bool all: If True, remove all empty elements in the path to the
                         deleted element. Defaults to False.
        """
        path = self._fix_ns(name, split=True)
        original_target = path[-1]

        default_lang = self.get_lang()
        if not lang:
            lang = default_lang

        parent: Optional[ET.Element] = self.xml
        for level, _ in enumerate(path):
            # Generate the paths to the target elements and their parent.
            element_path = "/".join(path[:len(path) - level])
            parent_path: Optional[str] = "/".join(path[:len(path) - level - 1])

            elements = self.xml.findall(element_path)
            if parent_path == '':
                parent_path = None
            if parent_path is not None:
                parent = self.xml.find(parent_path)
            if elements:
                if parent is None:
                    parent = self.xml
                for element in elements:
                    if element.tag == original_target or not list(element):
                        # Only delete the originally requested elements, and
                        # any parent elements that have become empty.
                        elem_lang = element.attrib.get('{%s}lang' % XML_NS,
                                                       default_lang)
                        if lang == '*' or elem_lang == lang:
                            parent.remove(element)
            if not all:
                # If we don't want to delete elements up the tree, stop
                # after deleting the first level of elements.
                return

    def match(self, xpath: Union[str, List[str]]) -> bool:
        """Compare a stanza object with an XPath-like expression.

        If the XPath matches the contents of the stanza object, the match
        is successful.

        The XPath expression may include checks for stanza attributes.
        For example::

            'presence@show=xa@priority=2/status'

        Would match a presence stanza whose show value is set to ``'xa'``,
        has a priority value of ``'2'``, and has a status element.

        :param string xpath: The XPath expression to check against. It
                             may be either a string or a list of element
                             names with attribute checks.
        """
        if not isinstance(xpath, list):
            xpath = self._fix_ns(xpath, split=True, propagate_ns=False)

        # Extract the tag name and attribute checks for the first XPath node.
        components = xpath[0].split('@')
        tag = components[0]
        attributes = components[1:]

        if tag not in (self.name, "{%s}%s" % (self.namespace, self.name)) and \
            tag not in self.loaded_plugins and tag not in self.plugin_attrib:
            # The requested tag is not in this stanza, so no match.
            return False

        # Check the rest of the XPath against any substanzas.
        matched_substanzas = False
        for substanza in self.iterables:
            if xpath[1:] == []:
                break
            matched_substanzas = substanza.match(xpath[1:])
            if matched_substanzas:
                break

        # Check attribute values.
        for attribute in attributes:
            name, value = attribute.split('=')
            if self[name] != value:
                return False

        # Check sub interfaces.
        if len(xpath) > 1:
            next_tag = xpath[1]
            if next_tag in self.sub_interfaces and self[next_tag]:
                return True

        # Attempt to continue matching the XPath using the stanza's plugins.
        if not matched_substanzas and len(xpath) > 1:
            # Convert {namespace}tag@attribs to just tag
            next_tag = xpath[1].split('@')[0].split('}')[-1]
            langs = [name[1] for name in self.plugins if name[0] == next_tag]
            for lang in langs:
                plugin = self.get_plugin(next_tag, lang)
                if plugin and plugin.match(xpath[1:]):
                    return True
            return False

        # Everything matched.
        return True

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Return the value of a stanza interface.

        If the found value is None or an empty string, return the supplied
        default value.

        Allows stanza objects to be used like dictionaries.

        :param string key: The name of the stanza interface to check.
        :param default: Value to return if the stanza interface has a value
                        of ``None`` or ``""``. Will default to returning None.
        """
        value = self[key]
        if value is None or value == '':
            return default
        return value

    def keys(self) -> List[str]:
        """Return the names of all stanza interfaces provided by the
        stanza object.

        Allows stanza objects to be used like dictionaries.
        """
        out = []
        out += [x for x in self.interfaces]
        out += [x for x in self.loaded_plugins]
        out.append('lang')
        if self.iterables:
            out.append('substanzas')
        return out

    def append(self, item: Union[ET.Element, ElementBase]) -> ElementBase:
        """Append either an XML object or a substanza to this stanza object.

        If a substanza object is appended, it will be added to the list
        of iterable stanzas.

        Allows stanza objects to be used like lists.

        :param item: Either an XML object or a stanza object to add to
                     this stanza's contents.
        """
        if not isinstance(item, ElementBase):
            if type(item) == XML_TYPE:
                return self.appendxml(item)
            else:
                raise TypeError(f"Cannot append {item!r} to a stanza")
        self.xml.append(item.xml)
        if item.__class__ == self.plugin_tag_map.get(item.tag_name(), None):
            self.init_plugin(item.plugin_attrib,
                             existing_xml=item.xml,
                             element=item,
                             reuse=False)
        elif item.__class__ in self.plugin_iterables:
            self.iterables.append(item)
            if item.__class__.plugin_multi_attrib:
                self.init_plugin(item.__class__.plugin_multi_attrib)
        else:
            self.iterables.append(item)
        item.parent = weakref.ref(self)
        return self

    def appendxml(self, xml: ET.Element) -> ElementBase:
        """Append an XML object to the stanza's XML.

        The added XML will not be included in the list of
        iterable substanzas.

        :param XML xml: The XML object to add to the stanza.
        """
        self.xml.append(xml)
        return self

    def pop(self, index: int = 0) -> ElementBase:
        """Remove and return the last substanza in the list of
        iterable substanzas.

        Allows stanza objects to be used like lists.

        :param int index: The index of the substanza to remove.
        """
        substanza = self.iterables.pop(index)
        self.xml.remove(substanza.xml)
        return substanza

    def next(self) -> ElementBase:
        """Return the next iterable substanza."""
        return self.__next__()

    def clear(self) -> ElementBase:
        """Remove all XML element contents and plugins.

        Any attribute values will be preserved.
        """
        for child in list(self.xml):
            self.xml.remove(child)

        for plugin in list(self.plugins.keys()):
            del self.plugins[plugin]
        return self

    @classmethod
    def tag_name(cls) -> str:
        """Return the namespaced name of the stanza's root element.

        The format for the tag name is::

            '{namespace}elementname'

        For example, for the stanza ``<foo xmlns="bar" />``,
        ``stanza.tag_name()`` would return ``"{bar}foo"``.
        """
        return "{%s}%s" % (cls.namespace, cls.name)

    def get_lang(self, lang: Optional[str] = None) -> str:
        result = self.xml.attrib.get('{%s}lang' % XML_NS, '')
        if not result and self.parent:
            parent = self.parent()
            if parent:
                return cast(str, parent['lang'])
        return result

    def set_lang(self, lang: Optional[str]) -> None:
        self.del_lang()
        attr = '{%s}lang' % XML_NS
        if lang:
            self.xml.attrib[attr] = lang

    def del_lang(self) -> None:
        attr = '{%s}lang' % XML_NS
        if attr in self.xml.attrib:
            del self.xml.attrib[attr]

    def _fix_ns(self, xpath: str, split: bool = False,
                propagate_ns: bool = True) -> Union[str, List[str]]:
        return fix_ns(xpath, split=split,
                             propagate_ns=propagate_ns,
                             default_ns=self.namespace)

    def __eq__(self, other: Any) -> bool:
        """Compare the stanza object with another to test for equality.

        Stanzas are equal if their interfaces return the same values,
        and if they are both instances of ElementBase.

        :param ElementBase other: The stanza object to compare against.
        """
        if not isinstance(other, ElementBase):
            return False

        # Check that this stanza is a superset of the other stanza.
        values = self.values
        other_values = other.values
        for key in other.keys():
            if key not in values or values.get(key) != other_values.get(key):
                return False

        # Check that the other stanza is a superset of this stanza.
        for key in self.keys():
            if key not in values or other_values.get(key) != values.get(key):
                return False

        # Both stanzas are supersets of each other, therefore they
        # must be equal.
        return True

    def __ne__(self, other: Any) -> bool:
        """Compare the stanza object with another to test for inequality.

        Stanzas are not equal if their interfaces return different values,
        or if they are not both instances of ElementBase.

        :param ElementBase other: The stanza object to compare against.
        """
        return not self.__eq__(other)

    def __bool__(self) -> bool:
        """Stanza objects should be treated as True in boolean contexts.
        """
        return True

    def __len__(self) -> int:
        """Return the number of iterable substanzas in this stanza."""
        return len(self.iterables)

    def __iter__(self) -> ElementBase:
        """Return an iterator object for the stanza's substanzas.

        The iterator is the stanza object itself. Attempting to use two
        iterators on the same stanza at the same time is discouraged.
        """
        self._index = 0
        return self

    def __next__(self) -> ElementBase:
        """Return the next iterable substanza."""
        self._index += 1
        if self._index > len(self.iterables):
            self._index = 0
            raise StopIteration
        return self.iterables[self._index - 1]

    def __copy__(self) -> ElementBase:
        """Return a copy of the stanza object that does not share the same
        underlying XML object.
        """
        return self.__class__(
            xml=copy.deepcopy(self.xml),
            parent=self.parent,
        )

    def __str__(self, top_level_ns: bool = True) -> str:
        """Return a string serialization of the underlying XML object.

        .. seealso:: :ref:`tostring`

        :param bool top_level_ns: Display the top-most namespace.
                                  Defaults to True.
        """
        return tostring(self.xml, xmlns='',
                        top_level=True)

    def __repr__(self) -> str:
        """Use the stanza's serialized XML as its representation."""
        return self.__str__()

    # Compatibility.
    _get_plugin = get_plugin
    get_stanza_values = _get_stanza_values
    set_stanza_values = _set_stanza_values

    #: A JSON/dictionary version of the XML content exposed through
    #: the stanza interfaces::
    #:
    #:     >>> msg = Message()
    #:     >>> msg.values
    #:    {'body': '', 'from': , 'mucnick': '', 'mucroom': '',
    #:     'to': , 'type': 'normal', 'id': '', 'subject': ''}
    #:
    #: Likewise, assigning to the :attr:`values` will change the XML
    #: content::
    #:
    #:     >>> msg = Message()
    #:     >>> msg.values = {'body': 'Hi!', 'to': 'user@example.com'}
    #:     >>> msg
    #:     '<message to="user@example.com"><body>Hi!</body></message>'
    #:
    #: Child stanzas are exposed as nested dictionaries.
    values = property(_get_stanza_values, _set_stanza_values)  # type: ignore


class StanzaBase(ElementBase):

    """
    StanzaBase provides the foundation for all other stanza objects used
    by Slixmpp, and defines a basic set of interfaces common to nearly
    all stanzas. These interfaces are the ``'id'``, ``'type'``, ``'to'``,
    and ``'from'`` attributes. An additional interface, ``'payload'``, is
    available to access the XML contents of the stanza. Most stanza objects
    will provided more specific interfaces, however.

    **Stanza Interfaces:**

        :id: An optional id value that can be used to associate stanzas
        :to: A JID object representing the recipient's JID.
        :from: A JID object representing the sender's JID.
               with their replies.
        :type: The type of stanza, typically will be ``'normal'``,
               ``'error'``, ``'get'``, or ``'set'``, etc.
        :payload: The XML contents of the stanza.

    :param XMLStream stream: Optional :class:`slixmpp.xmlstream.XMLStream`
                             object responsible for sending this stanza.
    :param XML xml: Optional XML contents to initialize stanza values.
    :param string stype: Optional stanza type value.
    :param sto: Optional string or :class:`slixmpp.xmlstream.JID`
                object of the recipient's JID.
    :param sfrom: Optional string or :class:`slixmpp.xmlstream.JID`
                  object of the sender's JID.
    :param string sid: Optional ID value for the stanza.
    :param parent: Optionally specify a parent stanza object will
                   contain this substanza.
    """

    #: The default XMPP client namespace
    namespace = 'jabber:client'
    types: ClassVar[Set[str]] = set()

    def __init__(self, stream: Optional[XMLStream] = None,
                 xml: Optional[ET.Element] = None,
                 stype: Optional[str] = None,
                 sto: Optional[JidStr] = None, sfrom: Optional[JidStr] = None,
                 sid: Optional[str] = None,
                 parent: Optional[ElementBase] = None, recv: bool = False):
        self.stream = stream
        if stream is not None:
            self.namespace = stream.default_ns
        ElementBase.__init__(self, xml, parent)
        if stype is not None:
            self['type'] = stype
        if sto is not None:
            self['to'] = sto
        if sfrom is not None:
            self['from'] = sfrom
        if sid is not None:
            self['id'] = sid
        self.tag = "{%s}%s" % (self.namespace, self.name)

    def set_type(self, value: str) -> StanzaBase:
        """Set the stanza's ``'type'`` attribute.

        Only type values contained in :attr:`types` are accepted.

        :param str value: One of the values contained in :attr:`types`
        """
        if value in self.types:
            self.xml.attrib['type'] = value
        return self

    def get_to(self) -> JID:
        """Return the value of the stanza's ``'to'`` attribute."""
        return JID(self._get_attr('to'))

    def set_to(self, value: JidStr) -> None:
        """Set the ``'to'`` attribute of the stanza.

        :param value: A string or :class:`slixmpp.xmlstream.JID` object
               representing the recipient's JID.
        """
        return self._set_attr('to', str(value))

    def get_from(self) -> JID:
        """Return the value of the stanza's ``'from'`` attribute."""
        return JID(self._get_attr('from'))

    def set_from(self, value: JidStr) -> None:
        """Set the 'from' attribute of the stanza.

        :param from: A string or JID object representing the sender's JID.
        :type from: str or :class:`.JID`
        """
        return self._set_attr('from', str(value))

    def get_payload(self) -> List[ET.Element]:
        """Return a list of XML objects contained in the stanza."""
        return list(self.xml)

    def set_payload(self, value: Union[List[ElementBase], ElementBase]) -> StanzaBase:
        """Add XML content to the stanza.

        :param value: Either an XML or a stanza object, or a list
                      of XML or stanza objects.
        """
        if not isinstance(value, list):
            value = [value]
        for val in value:
            self.append(val)
        return self

    def del_payload(self) -> StanzaBase:
        """Remove the XML contents of the stanza."""
        self.clear()
        return self

    def reply(self, clear: bool = True) -> StanzaBase:
        """Prepare the stanza for sending a reply.

        Swaps the ``'from'`` and ``'to'`` attributes.

        If ``clear=True``, then also remove the stanza's
        contents to make room for the reply content.

        For client streams, the ``'from'`` attribute is removed.

        :param bool clear: Indicates if the stanza's contents should be
                           removed. Defaults to ``True``.
        """
        new_stanza = copy.copy(self)
        # if it's a component, use from
        if self.stream and hasattr(self.stream, "is_component") and \
                getattr(self.stream, 'is_component'):
            new_stanza['from'], new_stanza['to'] = self['to'], self['from']
        else:
            new_stanza['to'] = self['from']
            del new_stanza['from']
        if clear:
            new_stanza.clear()
        return new_stanza

    def error(self) -> StanzaBase:
        """Set the stanza's type to ``'error'``."""
        self['type'] = 'error'
        return self

    def unhandled(self) -> None:
        """Called if no handlers have been registered to process this stanza.

        Meant to be overridden.
        """
        pass

    def exception(self, e: Exception) -> None:
        """Handle exceptions raised during stanza processing.

        Meant to be overridden.
        """
        log.exception('Error handling {%s}%s stanza', self.namespace,
                                                      self.name)

    def send(self) -> None:
        """Queue the stanza to be sent on the XML stream."""
        if self.stream is not None:
            self.stream.send(self)
        else:
            log.error("Tried to send stanza without a stream: %s", self)

    def __copy__(self) -> StanzaBase:
        """Return a copy of the stanza object that does not share the
        same underlying XML object, but does share the same XML stream.
        """
        return self.__class__(xml=copy.deepcopy(self.xml),
                              stream=self.stream)

    def __str__(self, top_level_ns: bool = False) -> str:
        """Serialize the stanza's XML to a string.

        :param bool top_level_ns: Display the top-most namespace.
                                  Defaults to ``False``.
        """
        xmlns = self.stream.default_ns if self.stream else ''
        return tostring(self.xml, xmlns=xmlns,
                        stream=self.stream,
                        top_level=(self.stream is None))
