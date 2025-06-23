.. _remove-process:

How to remove xmpp.process()
============================


Starting from slixmpp 1.8.0, running ``process()`` on an
XMLStream/ClientXMPP/ComponentXMPP instance is deprecated, and starting from
1.9.0, it will be removed.

Why
---

This has been the usual way of running an application using SleekXMPP/slixmpp
for ages, but it has come at a price: people do not understand how they
should run their application without it, or how to integrate their slixmpp
code with the rest of their asyncio application.

In essence, ``process()`` is only a very thin wrapper around asyncio loop
functions:

.. code-block:: python

        if timeout is None:
            if forever:
                self.loop.run_forever()
            else:
                self.loop.run_until_complete(self.disconnected)
        else:
            tasks: List[Future] = [asyncio.sleep(timeout)]
            if not forever:
                tasks.append(self.disconnected)
            self.loop.run_until_complete(asyncio.wait(tasks))

How
---

Hence it can be replaced according to what you want your application to do:

- To run forever, ``loop.run_forever()`` will work just fine

- To run until disconnected, ``loop.run_until_complete(xmpp.disconnected)``
  will be enough (XMLStream.disconnected is an future which result is set when
  the stream gets disconnected.

- To run for a scheduled time (and still abort when disconnected):

.. code-block:: python

    tasks = [asyncio.sleep(timeout)]
    tasks.append(xmpp.disconnected)
    loop.run_until_complete(asyncio.wait(tasks))

There is no magic at play here and anything is possible if a more flexible
execution scheme is expected.
