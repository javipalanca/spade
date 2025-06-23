.. _internal-api:

Internal "API"
==============

Slixmpp has a generic API registry that can be used by its plugins to allow
access control, redefinition of behaviour, without having to inherit from the
plugin or do more dark magic.

The idea is that each api call can be replaced, most of them use a form
of in-memory storage that can be, for example, replaced with database
or file-based storaged.


Each plugin is assigned an API proxy bound to itself, but only a few make use
of it.

See also :ref:`api-simple-tuto`.

Description of a generic API call
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    def get_toto(jid, node, ifrom, args):
        return 'toto'

    self.xmpp.plugin['xep_XXXX'].api.register(handler, 'get_toto')

Each API call will receive 4 parameters (which can be ``None`` if data
is not relevant to the operation), which are ``jid`` (``Optional[JID]``),
``node`` (``Optional[str]``), ``ifrom`` (``Optional[JID]``), and ``args``
(``Any``).

- ``jid``, if relevant, represents the JID targeted by that operation
- ``node``, if relevant is an arbitrary string, but was thought for, e.g.,
  a pubsub or disco node.
- ``ifrom``, if relevant, is the JID the event is coming from.
- ``args`` is the event-specific data passed on by the plugin, often a dict
  of arguments (can be None as well).

.. note::
    Since 1.8.0, API calls can be coroutines.


Handler hierarchy
~~~~~~~~~~~~~~~~~

The ``self.api.register()`` signature is as follows:

.. code-block:: python

    def register(handler, op, jid=None, node=None, default=False):
        pass

As you can see, :meth:`~.APIRegistry.register` takes an additional ctype
parameter, but the :class:`~.APIWrapper` takes care of that for us (in most
cases, it is the name of the XEP plugin, such as ``'xep_0XXX'``).

When you register a handler, you register it for an ``op``, for **operation**.
For example, ``get_vcard``.

``handler`` and ``op`` are the only two required parameters (and in many cases,
all you will ever need). You can, however, go further and register handlers
for specific values of the ``jid`` and ``node`` parameters of the calls.

The priority of the execution of handlers is as follows:

- Check if a handler for both values of ``node`` and ``jid`` has been defined
- If not found, check if a handler for this value of ``jid`` has been defined
- If not found, check if a handler for this value of ``node`` has been defined
- If still not found, get the global handler (no parameter registered)


Raw documentation
~~~~~~~~~~~~~~~~~

This documentation is provided for reference, but :meth:`~.APIRegistry.register`
should be all you need.


.. module:: slixmpp.api

.. autoclass:: APIRegistry
    :members:

.. autoclass:: APIWrapper

