===========
Quick Start
===========

Preparing the environment
-------------------------------
Before you start using the SPADE platform, you need to set up the execution environment.
The platform is based on the XMPP communication protocol and requires a dedicated server to function properly.
At this point, you can choose between three scenarios:

SPADE coroutine executor
########################
A SPADE agent is asynchronous, meaning that all the code required to run an agent must be executed within an asynchronous loop.
This is achieved using the *spade.run()* function. This function takes a coroutine as its first parameter and runs it within an
asynchronous loop. The second parameter is a boolean (default is False). If set to True, an internal server instance will be
launched, managed during the coroutine's lifespan, and deleted once it finishes.

.. code-block:: python

    async def main():
            dummy = DummyAgent("dummy@localhost", "your_password")
            await dummy.start()

        if __name__ == "__main__":
            spade.run(main(), embedded_xmpp_server=True)
                        ^       ^
                        |       |
                    coroutine   |
                                |
                            Server Flag

This is the preferred method for launching SPADE scripts, as it eliminates the need for the user to install or manage any external server.


.. note:: The launched server will use *localhost* as its host. Keep this in mind when creating agents and assigning their JIDs.
    A valid JID would be something like *agent1@localhost* or *agent1@127.0.0.1*



SPADE CLI command
#####################
The same server described previously can be launched independently from any agent using *spade run*.
This approach is useful for more complex MAS integrations and for obtaining a detailed log of the messages exchanged between agents.


.. code-block:: bash

    $ spade run
    ╭─────────────────────────────── SPADE ────────────────────────────────╮
    │ SPADE - Smart Python Agent Development Environment                   │
    │                                                                      │
    │ Development Lead:                                                    │
    │   - Javi Palanca                                                     │
    │ Funded by:                                                           │
    │   - Valencian Research Institute for Artificial Intelligence (VRAIN) │
    │ URL:                                                                 │
    │   -  https://spadeagents.eu                                          │
    │ Documentation:                                                       │
    │   -  http://spade-mas.readthedocs.io/                                │
    ╰────────────────── Version: 4.1.2      License: MIT ──────────────────╯
    yyyy-m-d h:m:s | INFO     | pyjabber.server:run_server:89 - Starting server...
    yyyy-m-d h:m:s | INFO     | pyjabber.server:run_server:133 - Client domain => 0.0.0.0
    yyyy-m-d h:m:s | INFO     | pyjabber.server:run_server:134 - Server is listening clients on [('0.0.0.0', 5222), ('158.42.184.157', 5222)]
    yyyy-m-d h:m:s | INFO     | pyjabber.server:run_server:149 - Server is listening servers on [('0.0.0.0', 5269)]
    yyyy-m-d h:m:s | INFO     | pyjabber.server:run_server:150 - Server started...
    yyyy-m-d h:m:s | INFO     | pyjabber.webpage.adminPage:start:35 - Serving admin webpage on http://localhost:9090

.. note:: The launched server will use *localhost* as its host. Keep this in mind when creating agents and assigning their JIDs.
    A valid JID would be something like *agent1@localhost* or *agent1@127.0.0.1*

Dedicated XMPP server
#####################

Any XMPP server can be used with the SPADE platform. *Prosody* is a well-tested solution with SPADE,
but there is a wide range of popular servers with large communities.

.. warning:: Make sure that *spade.run()* does not launch the internal server if your dedicated server
    is already running, as this can cause conflicts with the port binding.


Creating your first dummy agent
-------------------------------

It's time for us to build our first SPADE agent.


.. warning:: The SPADE server **MUST** be running in order to run the agents. If you close the server, the agents will stop working.

.. hint:: To install a different XMPP server visit https://xmpp.org/software/servers.html (we recommend `Prosody IM <https://prosody.im>`_)

.. hint:: To create a new XMPP account you can follow the steps of https://xmpp.org/getting-started/


A basic SPADE agent is really a Python script that imports the spade module and that
uses the constructs defined therein. For starters, fire up your favorite Python editor and create a file called ``dummyagent.py``.


.. warning:: Remember to change the example's jids and passwords by your own accounts. These accounts do not exist and are only for demonstration purposes.

To create an agent in a project you just need to: ::

    import spade

    class DummyAgent(spade.agent.Agent):
        async def setup(self):
            print("Hello World! I'm agent {}".format(str(self.jid)))

    async def main():
        dummy = DummyAgent("dummy@localhost", "your_password")
        await dummy.start()

    if __name__ == "__main__":
        spade.run(main())


This agent is only printing on screen a message during its setup and stopping. If you run this script you get
the following output

.. code-block:: console

    $ python dummyagent.py
    Hello World! I'm agent dummy@localhost
    $

And that's it! We have built our first SPADE Agent in 6 lines of code. Easy, isn't it? Of course, this is a very very
dumb agent that does nothing, but it serves well as a starting point to understand the logics behind SPADE.

.. note:: A SPADE agent is an asyncronous agent. That means that all the code to run an agent must be executed in an
    asyncronous loop. This is done by the ``spade.run()`` function. This function receives a coroutine as a parameter
    and runs it in an async loop. In our example, the ``main()`` coroutine is the one that is run in the loop.

.. note:: If you need to run a set of agents in parallel you can use the ``spade.start_agents(agent_list)`` function. This function
    receives a list of agents and runs them in parallel. This is useful when you need to run a big set of agents.

An agent with a behaviour
-------------------------

Let's build a more functional agent, one that uses an actual behaviour to perform a task. As we stated earlier, the real
programming of the SPADE agents is done mostly in the behaviours. Let's see how.

Let's create a cyclic behaviour that performs a task. In this case, a simple counter. We can modify our existing
``dummyagent.py`` script.

.. warning:: Remember to change the example's jids and passwords by your own accounts. These accounts do not exist
    and are only for demonstration purposes.

Example::

    import asyncio
    import spade
    from spade import wait_until_finished
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

    async def main():
        dummy = DummyAgent("dummy@localhost", "your_password")
        await dummy.start()
        print("DummyAgent started. Check its console to see the output.")

        print("Wait until user interrupts with ctrl+C")
        await wait_until_finished(dummy)

    if __name__ == "__main__":
        spade.run(main())


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
    DummyAgent started. Check its console to see the output.
    Wait until user interrupts with ctrl+C
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

    import asyncio
    import spade
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

    async def main():
        dummy = DummyAgent("your_jid@your_xmpp_server", "your_password")
        await dummy.start()

        # wait until user interrupts with ctrl+C
        while not dummy.my_behav.is_killed():
            try:
                await asyncio.sleep(1)
            except KeyboardInterrupt:
                break

        assert dummy.my_behav.exit_code == 10

        await dummy.stop()


    if __name__ == "__main__":
            spade.run(main())


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

A SPADE script will be running until all agents are stopped. If you want to stop all agents and finish the script you
may send a SIGINT (ctrl+C) signal. This signal will stop all agents.

.. warning:: The ``quit_spade()`` method has been deprecated since the current version of SPADE (3.3).


Creating an agent from within another agent
-------------------------------------------

There is a common use case where you may need to create an agent from within another agent, that is, from within another
agent's behaviour. This is a common case where ``start`` must be called with an ``await`` statement in order to work properly. Example::

    import spade
    from spade.agent import Agent
    from spade.behaviour import OneShotBehaviour


    class AgentExample(Agent):
        async def setup(self):
            print(f"{self.jid} created.")


    class CreateBehav(OneShotBehaviour):
        async def run(self):
            agent2 = AgentExample("agent2_example@your_xmpp_server", "fake_password")
            await agent2.start(auto_register=True)

    async def main():
        agent1 = AgentExample("agent1_example@your_xmpp_server", "fake_password")
        behav = CreateBehav()
        agent1.add_behaviour(behav)
        await agent1.start(auto_register=True)

        # wait until the behaviour is finished to quit spade.
        await behav.join()

    if __name__ == "__main__":
        spade.run(main())




