===========
Quick Start
===========

Creating your first dummy agent
-------------------------------

It's time for us to build our first SPADE agent. We'll assume that we have a registered user in an XMPP server with a
jid and a password. The jid contains the agent's name (before the @) and the DNS or IP of the XMPP server (after the @).
But **remember**! You should have your own jid and password in an XMPP server running in your own computer or in the
Internet. In this example we will assume that our jid is *your_jid@your_xmpp_server* and the password is *your_password*.

A basic SPADE agent is really a python script that imports the spade module and that uses the constructs defined therein.
For starters, fire up you favorite Python editor and create a file called ``dummyagent.py``.

To create an agent in a project you just need to: ::

    import spade

    class DummyAgent(spade.agent.Agent):
        def setup(self):
            print("Hello World! I'm agent {}".format(str(self.jid)))

    dummy = DummyAgent("your_jid@your_xmpp_server", "your_password")

    dummy.stop()


This agent is only printing on screen a message during its setup and stopping. If you run this script you get
the following output::

    $ python dummyagent.py
    Hello World! I'm agent your_jid@your_xmpp_server
    $

And that's it! We have built our first SPADE Agent in 6 lines of code. Easy, isn't it? Of course, this is a very very
dumb agent that does nothing, but it serves well as a starting point to understand the logics behind SPADE.



An agent with a behaviour
-------------------------

Let's build a more functional agent, one that uses an actual behaviour to perform a task. As we stated earlier, the real
programming of the SPADE agents is done mostly in the behaviours. Let's see how.

Let's create a cyclic behaviour that performs a task. In this case, a simple counter. We can modify our existing
``dummyagent.py`` script::

    import time
    import asyncio
    from spade.agent import Agent
    from spade.behaviour import Behaviour

    class DummyAgent(Agent):
        class MyBehav(Behaviour):
            async def on_start(self):
                print("Starting behaviour . . .")
                self.counter = 0

            async def run(self):
                print("Counter: {}".format(self.counter))
                self.counter += 1
                await asyncio.sleep(1)

        def setup(self):
            print("Agent starting . . .")
            b = self.MyBehav()
            self.add_behaviour(b)

    if __name__ == "__main__":
        dummy = DummyAgent("your_jid@your_xmpp_server", "your_password")

        # wait until user interrupts with ctrl+C
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                break
        dummy.stop()


As you can see, we have defined a custom behaviour called MyBehav that inherits from the spade.Behaviour.Behaviour class,
the default class for all behaviours. This class represents a cyclic behaviour with no specific period, that is, a
loop-like behaviour.

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

Now look at the ``setup()`` method of the agent. There, we make an instance of MyBehav and add it to the current agent
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
