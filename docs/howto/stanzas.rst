.. _work-with-stanzas:

How to Work with Stanza Objects
===============================

Slixmpp provides a large variety of facilities for abstracting the underlying
XML payloads of XMPP. Most of the visible user interface comes in a
dict-like interface provided in a specific ``__getitem__`` implementation
for :class:`~slixmpp.xmlstream.ElementBase` objects.


As a very high-level example, here is how to create a stanza with
an XEP-0191 payload, assuming the :class:`xep_0191 <slixmpp.plugins.xep_0191.XEP_0191>`
plugin is loaded:

.. code-block:: python

    from slixmpp.stanza import Iq
    iq = Iq()
    iq['to'] = 'toto@example.com'
    iq['type'] = 'set'
    iq['block']['items'] = {'a@example.com', 'b@example.com'}

Printing the resulting :class:`~slixmpp.stanaz.Iq` object gives us the
following XML (reformatted for readability):

.. code-block:: xml

    <iq xmlns="jabber:client" id="0" to="toto@example.com" type="set">
        <block xmlns="urn:xmpp:blocking">
            <item jid="b@example.com" />
            <item jid="a@example.com" />
        </block>
    </iq>


Realistically, users of the Slixmpp library should make use of the shorthand
functions available in their :class:`~.ClientXMPP` or
:class:`~.ComponentXMPP` objects to create :class:`~.Iq`, :class:`~.Message`
or :class:`~.Presence` objects that are bound to a stream, and which have
a generated unique identifier.

The most relevant functions are:

.. autofunction:: slixmpp.BaseXMPP.make_iq_get

.. autofunction:: slixmpp.BaseXMPP.make_iq_set

.. autofunction:: slixmpp.BaseXMPP.make_message

.. autofunction:: slixmpp.BaseXMPP.make_presence

The previous example then becomes:

.. code-block:: python

    iq = xmpp.make_iq_get(ito='toto@example.com')
    iq['block']['items'] = {'a@example.com', 'b@example.com'}


.. note::

    xml:lang is handled by piping the lang name after the attribute. For
    example ``message['body|fr']`` will return the ``<body/>`` attribute
    with ``xml:lang="fr``.

The next sections will try to explain as clearly as possible
how the magic operates.

.. _create-stanza-interfaces:

Defining Stanza Interfaces
--------------------------

The stanza interface is very rich and let developers have full control
over the API they want to have to manipulate stanzas.

The entire interface is defined as class attributes that are redefined
when subclassing :class:`~.ElementBase` when `creating a stanza plugin <create-stanza-plugins>`_.


The main attributes defining a stanza interface:

- plugin_attrib_: ``str``, the name of this element on the parent
- plugin_multi_attrib_: ``str``, the name of the iterable for this element on the parent
- interfaces_: ``set``, all known interfaces for this element
- sub_interfaces_: ``set`` (subset of ``interfaces``), for sub-elements with only text nodes
- bool_interfaces_: ``set`` (subset of ``interfaces``), for empty-sub-elements
- overrides_: ``list`` (subset of ``interfaces``), for ``interfaces`` to ovverride on the parent
- is_extension_: ``bool``, if the element is only an extension of the parent stanza

.. _plugin_attrib:

plugin_attrib
~~~~~~~~~~~~~

The ``plugin_attrib`` string is the defining element of any stanza plugin,
as it the name through which the element is accessed (except for ``overrides``
and ``is_extension``).

The extension is then registered through the help of :func:`~.register_stanza_plugin`
which will attach the plugin to its parent.

.. code-block:: python

    from slixmpp import ElementBase, Iq

    class Payload(ElementBase):
        name = 'apayload'
        plugin_attrib = 'mypayload'
        namespace = 'x-toto'

    register_stanza_plugin(Iq, Payload)

    iq = Iq()
    iq.enable('mypayload') # Similar to iq['mypayload']

The :class:`~.Iq` element created now contains our custom ``<apayload/>`` element.

.. code-block:: xml

    <iq xmlns="jabber:client" id="0">
        <apayload xmlns="x-toto"/>
    </iq>


.. _plugin_multi_attrib:

plugin_multi_attrib
~~~~~~~~~~~~~~~~~~~

The :func:`~.register_stanza_plugin` function has an ``iterable`` parameter, which
defaults to ``False``. When set to ``True``, it means that iterating over the element
is possible.


.. code-block:: python

    class Parent(ElementBase):
        pass # does not matter

    class Sub(ElementBase):
        name = 'sub'
        plugin_attrib = 'sub'

    class Sub2(ElementBase):
        name = 'sub2'
        plugin_attrib = 'sub2'

    register_stanza_plugin(Parent, Sub, iterable=True)
    register_stanza_plugin(Parent, Sub2, iterable=True)

    parent = Parent()
    parent.append(Sub())
    parent.append(Sub2())
    parent.append(Sub2())
    parent.append(Sub())

    for element in parent:
        do_something # A mix of Sub and Sub2 elements

In this situation, iterating over ``parent`` will yield each of the appended elements,
one after the other.

Sometimes you only want one specific type of sub-element, which is the use of
the ``plugin_multi_attrib`` string interface. This name will be mapped on the
parent, just like ``plugin_attrib``, but will return a list of all elements
of the same type only.

Re-using our previous example:

.. code-block:: python

    class Parent(ElementBase):
        pass # does not matter

    class Sub(ElementBase):
        name = 'sub'
        plugin_attrib = 'sub'
        plugin_multi_attrib = 'subs'

    class Sub2(ElementBase):
        name = 'sub2'
        plugin_attrib = 'sub2'
        plugin_multi_attrib = 'subs2'

    register_stanza_plugin(Parent, Sub, iterable=True)
    register_stanza_plugin(Parent, Sub2, iterable=True)

    parent = Parent()
    parent.append(Sub())
    parent.append(Sub2())
    parent.append(Sub2())
    parent.append(Sub())

    for sub in parent['subs']:
        do_something # ony Sub objects here

    for sub2 in parent['subs2']:
        do_something # ony Sub2 objects here


.. _interfaces:

interfaces
~~~~~~~~~~

The ``interfaces`` set **must** contain all the known ways to interact with
this element. It does not include plugins (registered to the element through
:func:`~.register_stanza_plugin`), which are dynamic.

By default, a name present in ``interfaces`` will be mapped to an attribute
of the element with the same name.

.. code-block:: python

    class Example(Element):
        name = 'example'
        interfaces = {'toto'}

    example = Example()
    example['toto'] = 'titi'

In this case, ``example`` contains ``<example toto="titi"/>``.

For empty and text_only sub-elements, there are sub_interfaces_ and
bool_interfaces_ (the keys **must** still be in ``interfaces``.

You can however define any getter, setter, and delete custom method for any of
those interfaces. Keep in mind that if one of the three is not custom,
Slixmpp will use the default one, so you have to make sure that either you
redefine all get/set/del custom methods, or that your custom methods are
compatible with the default ones.

In the following example, we want the ``toto`` attribute to be an integer.

.. code-block:: python

    class Example(Element):
        interfaces = {'toto', 'titi', 'tata'}

        def get_toto(self) -> Optional[int]:
            try:
                return int(self.xml.attrib.get('toto', ''))
            except ValueError:
                return None

        def set_toto(self, value: int):
            int(value) # make sure the value is an int
            self.xml.attrib['toto'] = str(value)

        example = Example()
        example['tata'] = "Test" # works
        example['toto'] = 1 # works
        print(type(example['toto'])) # the value is an int
        example['toto'] = "Test 2" # ValueError


One important thing to keep in mind is that the ``get_`` methods must be resilient
(when having a default value makes sense) because they are called on objects
received from the network.

.. _sub_interfaces:

sub_interfaces
~~~~~~~~~~~~~~

The ``bool_interfaces`` set allows mapping an interface to the text node of
sub-element of the current payload, with the same namespace

Here is a simple example:

.. code-block:: python

    class FirstLevel(ElementBase):
        name = 'first'
        namespace = 'ns'
        interfaces = {'second'}
        sub_interfaces = {'second'}

    parent = FirstLevel()
    parent['second'] = 'Content of second node'


Which will produces the following:

.. code-block:: xml

    <first xmlns="ns">
        <second>Content of second node</second>
    </first>

We can see that ``sub_interfaces`` allows to quickly create a sub-element and
manipulate its text node without requiring a custom element, getter or setter.

.. _bool_interfaces:

bool_interfaces
~~~~~~~~~~~~~~~

The ``bool_interfaces`` set allows mapping an interface to a direct sub-element of the
current payload, with the same namespace.


Here is a simple example:

.. code-block:: python

    class FirstLevel(ElementBase):
        name = 'first'
        namespace = 'ns'
        interfaces = {'second'}
        bool_interfaces = {'second'}

    parent = FirstLevel()
    parent['second'] = True


Which will produces the following:

.. code-block:: xml

    <first xmlns="ns">
        <second/>
    </first>

We can see that ``bool_interfaces`` allows to quickly create sub-elements with no
content, without the need to create a custom class or getter/setter.


.. _overrides:

overrides
~~~~~~~~~

List of ``interfaces`` on the present element that should override the
parent ``interfaces`` with the same name.

.. code-block:: python

    class Parent(ElementBase):
        name = 'parent'
        interfaces = {'toto', 'titi'}

    class Sub(ElementBase):
        name = 'sub'
        plugin_attrib = name
        interfaces = {'toto', 'titi'}
        overrides = ['toto']

    register_stanza_plugin(Parent, Sub)

    parent = Parent()
    parent['toto'] = 'test' # equivalent to parent['sub']['toto'] = "test"

.. _is_extension:

is_extension
~~~~~~~~~~~~

Stanza extensions are a specific kind of stanza plugin which have
the ``is_extension`` class attribute set to ``True``.

The following code will directly plug the extension into the
:class:`~.Message` element, allowing direct access
to the interface:

.. code-block:: python

    class MyCustomExtension(ElementBase):
        is_extension = True
        name = 'mycustom'
        namespace = 'custom-ns'
        plugin_attrib = 'mycustom'
        interfaces = {'mycustom'}

    register_stanza_plugin(Message, MyCustomExtension)

With this extension, we can do the folliowing:

.. code-block:: python

    message = Message()
    message['mycustom'] = 'toto'

Without the extension, obtaining the same results would be:

.. code-block:: python

    message = Message()
    message['mycustom']['mycustom'] = 'toto'


The extension is therefore named extension because it extends the
parent element transparently.


.. _create-stanza-plugins:

Creating Stanza Plugins
-----------------------

A stanza plugin is a class that inherits from :class:`~.ElementBase`, and
**must** contain at least the following attributes:

- name: XML element name (e.g. ``toto`` if the element is ``<toto/>``
- namespace: The XML namespace of the element.
- plugin_attrib_: ``str``, the name of this element on the parent
- interfaces_: ``set``, all known interfaces for this element

It is then registered through :func:`~.register_stanza_plugin` on the parent
element.

.. note::

    :func:`~.register_stanza_plugin` should NOT be called at the module level,
    because it executes code, and executing code at the module level can slow
    down import significantly!
