===========
Quick Start
===========

Creating your first dummy agent
-------------------------------

It's time for us to build our first SPADE agent. We'll assume that we have a registered user in an XMPP server with a
jid and a password. The jid contains the agent's name (before the @) and the DNS or IP of the XMPP server (after the @).
But **remember**! You should have your own jid and password in an XMPP server running in your own computer or in the
Internet. In this example we will assume that our jid is *your_jid@your_xmpp_server* and the password is *your_password*.

.. hint:: To create a new XMPP account you can follow the steps of https://xmpp.org/getting-started/

.. hint:: To install an XMPP server visit https://xmpp.org/software/servers.html (we recommend `Prosody IM <https://prosody.im>`_)

A basic SPADE agent is really a python script that imports the spade module and that uses the constructs defined therein.
For starters, fire up you favorite Python editor and create a file called ``dummyagent.py``.

.. warning:: Remember to change the example's jids and passwords by your own accounts. These accounts do not exist
    and are only for demonstration purposes.

To create an agent in a project you just need to: ::

    from spade import agent, quit_spade

    class DummyAgent(agent.Agent):
        async def setup(self):
            print("Hello World! I'm agent {}".format(str(self.jid)))

    dummy = DummyAgent("your_jid@your_xmpp_server", "your_password")
    future = dummy.start()
    future.result()

    dummy.stop()
    quit_spade()


This agent is only printing on screen a message during its setup and stopping. If you run this script you get
the following output::

    $ python dummyagent.py
    Hello World! I'm agent your_jid@your_xmpp_server
    $

And that's it! We have built our first SPADE Agent in 6 lines of code. Easy, isn't it? Of course, this is a very very
dumb agent that does nothing, but it serves well as a starting point to understand the logics behind SPADE.

.. note:: Note how the ``start`` function returns a future (or promise) which you can wait for with the result method
          (``future.result()``) to make sure that the ``start`` coroutine has finished before invoking the ``stop`` coroutine.

An agent with a behaviour
-------------------------

Let's build a more functional agent, one that uses an actual behaviour to perform a task. As we stated earlier, the real
programming of the SPADE agents is done mostly in the behaviours. Let's see how.

Let's create a cyclic behaviour that performs a task. In this case, a simple counter. We can modify our existing
``dummyagent.py`` script.

.. warning:: Remember to change the example's jids and passwords by your own accounts. These accounts do not exist
    and are only for demonstration purposes.

Example::

    import time
    import asyncio
    from spade.agent import Agent
    from spade.behaviour import CyclicBehaviour

    class DummyAgent(Agent):
        class MyBehav(CyclicBehaviour):
            async def on_start(self):
                print("Starting behaviour . . .")
                self.counter = 0

            async def run(self):
                print("Counter: {}".format(self.counter))
                self.counter += 1
                await asyncio.sleep(1)

        async def setup(self):
            print("Agent starting . . .")
            b = self.MyBehav()
            self.add_behaviour(b)

    if __name__ == "__main__":
        dummy = DummyAgent("your_jid@your_xmpp_server", "your_password")
        future = dummy.start()
        future.result()

        print("Wait until user interrupts with ctrl+C")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping...")
        dummy.stop()


As you can see, we have defined a custom behaviour called MyBehav that inherits from the spade.behaviour.CyclicBehaviour
class, the default class for all behaviours. This class represents a cyclic behaviour with no specific period, that is,
a loop-like behaviour.

You can see that there is a coroutine called ``on_start()`` in the behaviour. This method is similar to the ``setup()``
method of the agent class but it is run in the async loop. It is executed just before the main iteration of the
behaviour begins and it is used for initialization code. In this case, we print a line and initialize the variable for
the counter. There is also an ``on_end()`` coroutine that is executed when a behaviour is done or killed.

Also, there is the ``run()`` method, which is very important. In all behaviours, this is the method in which the core of
the programming is done, because this method is called on each iteration of the behaviour loop. It acts as the body of
the loop, sort of. In our example, the ``run()`` method prints the current value of the counter, increases it and then
waits for a second (to iterate again).

.. warning:: **Note** that the ``run()`` method is an async coroutine!. This is very important since SPADE is an
    **async library** based on python's `asyncio <https://docs.python.org/3/library/asyncio.html>`_. That's why we can
    call async methods inside the ``run()`` method, like the ``await asyncio.sleep(1)``, which sleeps during one second
    without blocking the event loop.

Now look at the ``setup()`` coroutine of the agent. There, we make an instance of MyBehav and add it to the current agent
by means of the ``add_behaviour()`` method. The first parameter of this method is the behaviour we want to add, and
there is also a second optional parameter which is the template associated to that behaviour, but we will talk later
about templates.

Let's test our new agent::

    $ python dummyagent.py
    Agent starting . . .
    Starting behaviour . . .
    Counter: 0
    Counter: 1
    Counter: 2
    Counter: 3
    Counter: 4
    Counter: 5
    Counter: 6
    Counter: 7

. . . and so on. As we have not set any end condition, this agent would go on counting forever until we press ctrl+C.


Finishing a behaviour
---------------------

If you want to finish a behaviour you can kill it by using the ``self.kill(exit_code)`` method. This method **marks**
the behaviour to be killed at the next loop iteration and stores the exit_code to be queried later.

An example of how to kill a behaviour::

    import time
    import asyncio
    from spade.agent import Agent
    from spade.behaviour import CyclicBehaviour

    class DummyAgent(Agent):
        class MyBehav(CyclicBehaviour):
            async def on_start(self):
                print("Starting behaviour . . .")
                self.counter = 0

            async def run(self):
                print("Counter: {}".format(self.counter))
                self.counter += 1
                if self.counter > 3:
                    self.kill(exit_code=10)
                    return
                await asyncio.sleep(1)

            async def on_end(self):
                print("Behaviour finished with exit code {}.".format(self.exit_code))

        async def setup(self):
            print("Agent starting . . .")
            self.my_behav = self.MyBehav()
            self.add_behaviour(self.my_behav)

    if __name__ == "__main__":
        dummy = DummyAgent("your_jid@your_xmpp_server", "your_password")
        future = dummy.start()
        future.result()  # Wait until the start method is finished

        # wait until user interrupts with ctrl+C
        while not dummy.my_behav.is_killed():
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                break
        dummy.stop()


And the output of this example would be::

    $ python killbehav.py
    Agent starting . . .
    Starting behaviour . . .
    Counter: 0
    Counter: 1
    Counter: 2
    Counter: 3
    Behaviour finished with exit code 10.


.. note:: An exit code may be of any type you need: int, dict, string, exception, etc.

.. warning::
    Remember that killing a behaviour does not cancel its current run loop, if you need to finish the current
    iteration you'll have to call return.

.. hint::
    If a exception occurs inside an ``on_start``, ``run`` or ``on_end`` coroutines, the behaviour will be
    automatically killed and the exception will be stored as its ``exit_code``.


Finishing SPADE
---------------

There is a helper to quickly finish all the agents and behaviors running in your process. This helper function is
``quit_spade``::

    from spade import quit_spade

    from spade import agent

    class DummyAgent(agent.Agent):
        async def setup(self):
            print("Hello World! I'm agent {}".format(str(self.jid)))

    dummy = DummyAgent("your_jid@your_xmpp_server", "your_password")
    future = dummy.start()
    future.result()

    dummy.stop()

    quit_spade()



.. hint::
    The ``quit_spade`` helper is not mandatory, but it helps to terminate all agents of the active container along with
    their behaviors, as well as free all pending resources (threads, etc...).

Creating an agent from within another agent
-------------------------------------------

There is a common use case where you may need to create an agent from within another agent, that is, from within another
agent's behaviour. This is a *special* case because you can't create a new event loop when you have a loop already
running. For this special case you can use the ``start`` method as usual. But in this case ```start`` behaves as a
coroutine, so it MUST be called with an ``await`` statement in order to work properly. Example::

    from spade import quit_spade
    from spade.agent import Agent
    from spade.behaviour import OneShotBehaviour


    class AgentExample(Agent):
        async def setup(self):
            print(f"{self.jid} created.")


    class CreateBehav(OneShotBehaviour):
        async def run(self):
            agent2 = AgentExample("agent2_example@your_xmpp_server", "fake_password")
            # This start is inside an async def, so it must be awaited
            await agent2.start(auto_register=True)


    if __name__ == "__main__":
        agent1 = AgentExample("agent1_example@your_xmpp_server", "fake_password")
        behav = CreateBehav()
        agent1.add_behaviour(behav)
        # This start is in a synchronous piece of code, so it must NOT be awaited
        future = agent1.start(auto_register=True)
        future.result()

        # wait until the behaviour is finished to quit spade.
        behav.join()
        quit_spade()



.. warning:: Remember to call ``start`` with an ``await`` whenever you are inside an asyncronous method (another coroutine).
             Otherwise, call ``start`` as usual (without the ``await`` statement).


.. note:: The ``stop`` method behaves just like ``start``. They change depending on the context.
          They return a coroutine or a future depending on whether they are called from a coroutine or a synchronous method.
