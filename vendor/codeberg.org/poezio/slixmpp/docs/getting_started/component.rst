.. _echocomponent:

=================================
Create and Run a Server Component
=================================

.. note::

    If you have any issues working through this quickstart guide
    join the chat room at `slixmpp@muc.poez.io
    <xmpp:slixmpp@muc.poez.io?join>`_.

If you have not yet installed Slixmpp, do so now by either checking out a version
with `Git <https://codeberg.org/poezio/slixmpp>`_.

Many XMPP applications eventually graduate to requiring to run as a server
component in order to meet scalability requirements. To demonstrate how to
turn an XMPP client bot into a component, we'll turn the echobot example
(:ref:`echobot`) into a component version.

The first difference is that we will add an additional import statement:

.. code-block:: python

    from slixmpp.componentxmpp import ComponentXMPP

Likewise, we will change the bot's class definition to match:

.. code-block:: python

    class EchoComponent(ComponentXMPP):

        def __init__(self, jid, secret, server, port):
            ComponentXMPP.__init__(self, jid, secret, server, port)

A component instance requires two extra parameters compared to a client
instance: ``server`` and ``port``. These specifiy the name and port of
the XMPP server that will be accepting the component. For example, for
a MUC component, the following could be used:

.. code-block:: python

    muc = ComponentXMPP('muc.slixmpp.com', '******', 'slixmpp.com', 5555)

.. note::

    The ``server`` value is **NOT** derived from the provided JID for the
    component, unlike with client connections.

One difference with the component version is that we do not have
to handle the :term:`session_start` event if we don't wish to deal
with presence.

The other, main difference with components is that the
``'from'`` value for every stanza must be explicitly set, since
components may send stanzas from multiple JIDs. To do so,
the :meth:`~slixmpp.basexmpp.BaseXMPP.send_message()` and
:meth:`~slixmpp.basexmpp.BaseXMPP.send_presence()` accept the parameters
``mfrom`` and ``pfrom``, respectively. For any method that uses
:class:`~slixmpp.stanza.iq.Iq` stanzas, ``ifrom`` may be used.


Final Product
-------------

.. include:: ../../examples/echo_component.py
    :literal:
