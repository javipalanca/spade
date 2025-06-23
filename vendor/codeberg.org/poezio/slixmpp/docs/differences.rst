.. _differences:

Differences from SleekXMPP
==========================

**Python 3.7+ only**
    slixmpp will work on python 3.7 and above. It may work with previous
    versions but we provide no guarantees.

**Stanza copies**
    The same stanza object is given through all the handlers; a handler that
    edits the stanza object should make its own copy.

**Replies**
    Because stanzas are not copied anymore,
    :meth:`Stanza.reply() <.StanzaBase.reply>` calls
    (for :class:`IQs <.Iq>`, :class:`Messages <.Message>`, etc)
    now return a new object instead of editing the stanza object
    in-place.

**Block and threaded arguments**
    All the functions that had a ``threaded=`` or ``block=`` argument
    do not have it anymore. Also, :meth:`.Iq.send` **does not block
    anymore**.

**Coroutine facilities**
    **See** :ref:`using_asyncio`

    If an event handler is a coroutine, it will be called asynchronously
    in the event loop instead of inside the event caller.

    A CoroutineCallback class has been added to create coroutine stream
    handlers, which will be also handled in the event loop.

    The :class:`~.slixmpp.stanza.Iq` object’s :meth:`~.slixmpp.stanza.Iq.send`
    method now **always** return a :class:`~.asyncio.Future` which result will be set
    to the IQ reply when it is received, or to ``None`` if the IQ is not of
    type ``get`` or ``set``.

    Many plugins (WIP) calls which retrieve information also return the same
    future.

**Architectural differences**
    slixmpp does not have an event queue anymore, and instead processes
    handlers directly after receiving the XML stanza.

.. note::
    If you find something that doesn’t work but should, please report it.
