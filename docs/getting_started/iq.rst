Send/Receive IQ Stanzas
=======================

Unlike :class:`~slixmpp.stanza.message.Message` and
:class:`~slixmpp.stanza.presence.Presence` stanzas which only use
text data for basic usage, :class:`~slixmpp.stanza.Iq` stanzas
require using XML payloads, and generally entail creating a new
Slixmpp plugin to provide the necessary convenience methods to
make working with them easier.

Basic Use
---------

XMPP's use of :class:`~slixmpp.stanza.Iq` stanzas is built around
namespaced ``<query />`` elements. For clients, just sending the
empty ``<query />`` element will suffice for retrieving information. For
example, a very basic implementation of service discovery would just
need to be able to send:

.. code-block:: xml

    <iq to="user@example.com" type="get" id="1">
      <query xmlns="http://jabber.org/protocol/disco#info" />
    </iq>

Creating Iq Stanzas
~~~~~~~~~~~~~~~~~~~

Slixmpp provides built-in support for creating basic :class:`~slixmpp.stanza.Iq`
stanzas this way. The relevant methods are:

* :meth:`~slixmpp.basexmpp.BaseXMPP.make_iq`
* :meth:`~slixmpp.basexmpp.BaseXMPP.make_iq_get`
* :meth:`~slixmpp.basexmpp.BaseXMPP.make_iq_set`
* :meth:`~slixmpp.basexmpp.BaseXMPP.make_iq_result`
* :meth:`~slixmpp.basexmpp.BaseXMPP.make_iq_error`
* :meth:`~slixmpp.basexmpp.BaseXMPP.make_iq_query`

These methods all follow the same pattern: create or modify an existing
:class:`~slixmpp.stanza.Iq` stanza, set the ``'type'`` value based
on the method name, and finally add a ``<query />`` element with the given
namespace. For example, to produce the query above, you would use:

.. code-block:: python

    self.make_iq_get(queryxmlns='http://jabber.org/protocol/disco#info',
                     ito='user@example.com')


Sending Iq Stanzas
~~~~~~~~~~~~~~~~~~

Once an :class:`~slixmpp.stanza.Iq` stanza is created, sending it
over the wire is done using its :meth:`~slixmpp.stanza.Iq.send()`
method, like any other stanza object. However, there are a few extra
options to control how to wait for the query's response, as well as
how to handle the result.

:meth:`~slixmpp.stanza.Iq.send()` returns an :class:`~asyncio.Future`
object, which can be awaited on until a ``result`` is received.

These options are:

* ``timeout``: When using the blocking behaviour, the call will eventually
  timeout with an error. The default timeout is 30 seconds, but this may
  be overidden two ways. To change the timeout globally, set:

    .. code-block:: python

        self.response_timeout = 10

  To change the timeout for a single call, the ``timeout`` parameter works:

    .. code-block:: python

        iq.send(timeout=60)

* ``callback``: When not using a blocking call, using the ``callback``
  argument is a simple way to register a handler that will execute
  whenever a response is finally received.

    .. code-block:: python

       iq.send(callback=self.a_callback)


.. note::

    ``callback`` can be effectively
    replaced using ``await``, and standard exception handling
    (see below), which provide a more linear and readable workflow.

Properly working with :class:`~slixmpp.stanza.Iq` stanzas requires
handling the intended, normal flow, error responses, and timed out
requests. To make this easier, two exceptions may be thrown by
:meth:`~slixmpp.stanza.Iq.send()`: :exc:`~slixmpp.exceptions.IqError`
and :exc:`~slixmpp.exceptions.IqTimeout`. These exceptions only
apply to the default, blocking calls.

.. code-block:: python

    try:
        resp = await iq.send()
        # ... do stuff with expected Iq result
    except IqError as e:
        err_resp = e.iq
        # ... handle error case
    except IqTimeout:
        # ... no response received in time
        pass

If you do not care to distinguish between errors and timeouts, then you
can combine both cases with a generic :exc:`~slixmpp.exceptions.XMPPError`
exception:

.. code-block:: python

    try:
        resp = await iq.send()
    except XMPPError:
        # ... Don't care about the response
        pass

Advanced Use
------------

Going beyond the basics provided by Slixmpp requires building at least a
rudimentary Slixmpp plugin to create a :term:`stanza object` for
interfacting with the :class:`~slixmpp.stanza.Iq` payload.

.. seealso::

    * :ref:`create-plugin`
    * :ref:`work-with-stanzas`
    * :ref:`using-handlers-matchers`


The typical way to respond to :class:`~slixmpp.stanza.Iq` requests is
to register stream handlers. As an example, suppose we create a stanza class
named ``CustomXEP`` which uses the XML element ``<query xmlns="custom-xep" />``,
and has a :attr:`~slixmpp.xmlstream.stanzabase.ElementBase.plugin_attrib` value
of ``custom_xep``.

There are two types of incoming :class:`~slixmpp.stanza.Iq` requests:
``get`` and ``set``. You can register a handler that will accept both and then
filter by type as needed, as so:

.. code-block:: python

    self.register_handler(Callback(
        'CustomXEP Handler',
        StanzaPath('iq/custom_xep'),
        self._handle_custom_iq))

    # ...

    def _handle_custom_iq(self, iq):
        if iq['type'] == 'get':
            # ...
            pass
        elif iq['type'] == 'set':
            # ...
            pass
        else:
            # ... This will capture error responses too
            pass

If you want to filter out query types beforehand, you can adjust the matching
filter by using ``@type=get`` or ``@type=set`` if you are using the recommended
:class:`~slixmpp.xmlstream.matcher.stanzapath.StanzaPath` matcher.

.. code-block:: python

    self.register_handler(Callback(
        'CustomXEP Handler',
        StanzaPath('iq@type=get/custom_xep'),
        self._handle_custom_iq_get))

    # ...

    def _handle_custom_iq_get(self, iq):
        assert(iq['type'] == 'get')
