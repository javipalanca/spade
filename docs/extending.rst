.. _extending:

============================
Extending SPADE with plugins
============================

This release of SPADE is designed as a very light version of the platform (compared with SPADE<3.0) which provides only
the core features that a MAS platform should have. This implies that some of the features that were provided by previous
versions of the platform are now not included.

*How makes that sense?* Well, all that previous features are not lost, but
are going to be turned into plugins that you can connect to your MAS application.

This way it is very easy to add new features to SPADE without disturbing the core development.

We have planned three different ways to design plugins for the SPADE platform, but of course we are open to suggestions.

.. warning::
    A plugin needs to comply with some requirements to be accepted as a SPADE plugin and be listed as an official
    plugin on the main page:
        #. It must be open source (of course!) and published in PyPi.
        #. The package must be called spade-* (e.g.: spade-bdi, spade-owl, etc.) and be imported as ``import spade_*``.
        #. It must be tested.
        #. It must follow the `PEP8 <https://www.python.org/dev/peps/pep-0008/>`_.

You can develop *new behaviours*, *new mixins* that modify behaviours, and of course *new libraries* that your agents
can use inside your behaviours. Let's see some examples of each of these ones:


New Behaviours
--------------

Developing new behaviours is as easy as creating a new class that inherits from ``spade.behaviour.CyclicBehaviour`` (or
any of its subclassed behaviours) and overload the methods that are needed. Pay atention to the methods that are related
with the control flow of a behaviour like ``_step``, ``done`` and ``_run``. And remember that you *should not* overload
the methods that are reserved for the user to be overloaded: ``on_start``, ``run`` and ``on_end``.

Example::

    class BDIBehaviour(spade.behaviour.PeriodicBehaviour):

        async def _step(self):
            # the bdi stuff

        def add_belief(self, ...):
            ...
        def add_desire(self, ...):
            ...
        def add_intention(self, ...):
            ...
        def done(self):
            # the done evaluation

        ...


New Mixins
----------

Some cases you don't want to add a new behaviour, but to add new features to current behaviours or agents. This can be done by
means of *mixins*. A mixin is a class that a behaviour or an agent can inherit from, in addition to the original parent class,
making use of the multiple inheritance of python. This way, when we are creating our agent and we implement its
behaviour which is (for example) a cyclic behaviour and we want to add this behaviour a feature that is provided by a
plugin called ``spade-p2p`` that allows the agent to send P2P messages (by modifying the send and receive methods of the
behaviour) we should do the following::

    from spade_p2p import P2PMixin

    class MyNewBehaviour(P2PMixin, CyclicBehaviour):
        ...
        async def run(self):
            ...
            self.send(my_message, p2p=True)
            ...


.. warning::
    The order of your mixins is important! The base behaviour class **must** be **always** the last one in the
    method resolution order.

.. hint::
    Remember that if you need to call the parent function of the base behaviour (or any other mixin in the method
    resolution order), you must use the ``super()`` function (see the following example).

To develop this example mixin you should do the following::

    class P2PMixin(object):
        async def send(self, msg, p2p=False):
            if p2p:
                await self.send_p2p(msg)
            else:
                await super().send(msg)


        async def send_p2p(self, msg):
            ...


In case you need to apply the mixin to the ``Agent`` class there are two hook coroutines that are prepared to be overriden
if needed. These coroutines are ``_hook_plugin_before_connection`` and ``_hook_plugin_after_connection``. They will be called
before and after the connection to the server is done respectively.
In order to support multiple mixins it is **important** to call always to the parent method. Next, an example of how to
build a simple mixin is shown::

    class MyMixin:
        async def _hook_plugin_before_connection(self, *args, **kwargs):
            await super()._hook_plugin_before_connection(*args, **kwargs)
            # do my plugin stuff before the connection is done

        async def _hook_plugin_after_connection(self, *args, **kwargs):
            await super()._hook_plugin_after_connection(*args, **kwargs)
            # do my plugin stuff after the connection is done

    class MyAgent(MyMixin, Agent):
        # Inherit always from mixins first. Last class to inherit from is Agent.


New Libraries
-------------

Finally, the easiest way to add new features to your agents is by means of *libraries*. If you want your agents to
support, for example, the OWL content language, you don't need to change spade, just make a library that handles it.
Example::

    from spade_owl import parse as owl_parse
    from spade_owl import dump as owl_dump

    class MyBehaviour(spade.behaviour.CyclicBehaviour):
        async def run(self):
            msg = await self.receive()

            owl_content = owl_parse(msg.content)
            # do wat you want with the owl content

            reply.content = owl_dump(...my owl reply...)

            await self.send(reply)

