===================
Advanced Behaviours
===================

There are more complex types of behaviours that you can use in SPADE. Let's see some of them.

Periodic Behaviour
------------------

This behaviour runs its ``run()`` body at a scheduled ``period``. This period is set in seconds.
You can also delay the startup of the periodic behaviour by setting a datetime in the ``start_at`` parameter.

.. warning:: Remember to change the example's jids and passwords by your own accounts. These accounts do not exist
    and are only for demonstration purposes.

Let's see an example::

    import datetime
    import getpass
    import time

    from spade import quit_spade
    from spade.agent import Agent
    from spade.behaviour import CyclicBehaviour, PeriodicBehaviour
    from spade.message import Message


    class PeriodicSenderAgent(Agent):
        class InformBehav(PeriodicBehaviour):
            async def run(self):
                print(f"PeriodicSenderBehaviour running at {datetime.datetime.now().time()}: {self.counter}")
                msg = Message(to=self.get("receiver_jid"))  # Instantiate the message
                msg.body = "Hello World"  # Set the message content

                await self.send(msg)
                print("Message sent!")

                if self.counter == 5:
                    self.kill()
                self.counter += 1

            async def on_end(self):
                # stop agent from behaviour
                await self.agent.stop()

            async def on_start(self):
                self.counter = 0

        async def setup(self):
            print(f"PeriodicSenderAgent started at {datetime.datetime.now().time()}")
            start_at = datetime.datetime.now() + datetime.timedelta(seconds=5)
            b = self.InformBehav(period=2, start_at=start_at)
            self.add_behaviour(b)


    class ReceiverAgent(Agent):
        class RecvBehav(CyclicBehaviour):
            async def run(self):
                print("RecvBehav running")
                msg = await self.receive(timeout=10)  # wait for a message for 10 seconds
                if msg:
                    print("Message received with content: {}".format(msg.body))
                else:
                    print("Did not received any message after 10 seconds")
                    self.kill()

            async def on_end(self):
                await self.agent.stop()

        async def setup(self):
            print("ReceiverAgent started")
            b = self.RecvBehav()
            self.add_behaviour(b)


    if __name__ == "__main__":
        receiver_jid = input("Receiver JID> ")
        passwd = getpass.getpass()
        receiveragent = ReceiverAgent(receiver_jid, passwd)

        sender_jid = input("Sender JID> ")
        passwd = getpass.getpass()
        senderagent = PeriodicSenderAgent(sender_jid, passwd)

        future = receiveragent.start(auto_register=True)
        future.result()  # wait for receiver agent to be prepared.

        senderagent.set("receiver_jid", receiver_jid)  # store receiver_jid in the sender knowledge base
        senderagent.start(auto_register=True)

        while receiveragent.is_alive():
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                senderagent.stop()
                receiveragent.stop()
                break
        print("Agents finished")
        quit_spade()

The output of this code would be similar to::

    $ python periodic.py
    ReceiverAgent started
    RecvBehav running
    PeriodicSenderAgent started at 17:40:39.901903
    PeriodicSenderBehaviour running at 17:40:45.720227: 0
    Message sent!
    Message received with content: Hello World
    RecvBehav running
    PeriodicSenderBehaviour running at 17:40:46.906229: 1
    Message sent!
    Message received with content: Hello World
    RecvBehav running
    PeriodicSenderBehaviour running at 17:40:48.906347: 2
    Message sent!
    Message received with content: Hello World
    RecvBehav running
    PeriodicSenderBehaviour running at 17:40:50.903576: 3
    Message sent!
    Message received with content: Hello World
    RecvBehav running
    PeriodicSenderBehaviour running at 17:40:52.905082: 4
    Message sent!
    Message received with content: Hello World
    RecvBehav running
    PeriodicSenderBehaviour running at 17:40:54.904886: 5
    Message sent!
    Message received with content: Hello World
    RecvBehav running
    Did not received any message after 10 seconds
    Agents finished



TimeoutBehaviour
----------------

You can also create a ``TimeoutBehaviour`` which is run once (like OneShotBehaviours) but its activation is triggered at
a specified ``datetime`` just as in ``PeriodicBehaviours``.

Let's see an example::

    import getpass
    import time
    import datetime
    from spade.agent import Agent
    from spade.behaviour import CyclicBehaviour, TimeoutBehaviour
    from spade.message import Message


    class TimeoutSenderAgent(Agent):
        class InformBehav(TimeoutBehaviour):
            async def run(self):
                print(f"TimeoutSenderBehaviour running at {datetime.datetime.now().time()}")
                msg = Message(to=self.get("receiver_jid"))  # Instantiate the message
                msg.body = "Hello World"  # Set the message content

                await self.send(msg)

            async def on_end(self):
                await self.agent.stop()

        async def setup(self):
            print(f"TimeoutSenderAgent started at {datetime.datetime.now().time()}")
            start_at = datetime.datetime.now() + datetime.timedelta(seconds=5)
            b = self.InformBehav(start_at=start_at)
            self.add_behaviour(b)


    class ReceiverAgent(Agent):
        class RecvBehav(CyclicBehaviour):
            async def run(self):
                msg = await self.receive(timeout=10)  # wait for a message for 10 seconds
                if msg:
                    print("Message received with content: {}".format(msg.body))
                else:
                    print("Did not received any message after 10 seconds")
                    self.kill()

            async def on_end(self):
                await self.agent.stop()

        async def setup(self):
            b = self.RecvBehav()
            self.add_behaviour(b)


    if __name__ == "__main__":
        receiver_jid = input("Receiver JID> ")
        passwd = getpass.getpass()
        receiveragent = ReceiverAgent(receiver_jid, passwd)

        sender_jid = input("Sender JID> ")
        passwd = getpass.getpass()
        senderagent = TimeoutSenderAgent(sender_jid, passwd)

        future = receiveragent.start(auto_register=True)
        future.result()  # wait for receiver agent to be prepared.

        senderagent.set("receiver_jid", receiver_jid)  # store receiver_jid in the sender knowledge base
        senderagent.start(auto_register=True)

        while receiveragent.is_alive():
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                senderagent.stop()
                receiveragent.stop()
                break
        print("Agents finished")

This would produce the following output::

    $python timeout.py
    TimeoutSenderAgent started at 18:12:09.620316
    TimeoutSenderBehaviour running at 18:12:14.625403
    Message received with content: Hello World
    Did not received any message after 10 seconds
    Agents finished


Finite State Machine Behaviour
------------------------------

SPADE agents can also have more complex behaviours which are a finite state machine (FSM) which has registered states and
transitions between states. This kind of behaviour allows SPADE agents to build much more complex and interesting
behaviours in our agent model.

The ``FSMBehaviour`` class is a container behaviour (subclass of ``CyclicBehaviour``) that implements the methods
``add_state(name, state, initial)`` and ``add_transition(source, dest)``. Every state of the FSM must be registered in
the behaviour with a string name and an instance of the ``State`` class. This ``State`` class represents a node of the
FSM and (since it's a subclass of ``OneShotBehaviour``) you must override the ``run`` coroutine just as in a regular
behaviour. Since a ``State`` is a regular behaviour, you can also override the ``on_start`` and ``on_end`` coroutines,
and, of course, use the ``send`` and ``receive`` coroutines to be able to interact with other agents via SPADE messaging.

.. note:: To mark a ``State`` as initial state of the FSM set **initial** parameter to *True* when calling *add_state*
    (``add_state(name, state, initial=True)``).
    **A FSM can only have ONE initial state, so the initial state will be the last one registered.**

Transitions in a ``FSMBehaviour`` define from which state to which state it is allowed to transit. A ``State`` defines
its transit to another state by using the ``set_next_state`` method in its ``run`` coroutine.
By using the ``set_next_state`` method a state dinamically expresses to which state it transits when it finishes. After
running a state, the FSM reads this *next_state* value and, if the transition is valid, it transits to that state.

.. warning:: If the transition is not registered it raises a ``NotValidTransition`` exception and the FSM behaviour is
    finished.

.. warning:: ``set_next_state`` must be called with the same string name with which that state was registered. If the
    state is not registered a ``NotValidState`` exception is raised and the FSM behaviour is finished.

A ``FSMBehaviour`` has a unique template, which is shared with all the states of the FSM. You must take this into account
when you describe your FSM states, because they will share the same message queue.

Next, we are going to see an example where a very simple FSM is defined, with three states, which transitate from one
state to the next one in order. It also sends a message to itself at the first initial state, which is received at the
third (and final) state. Also note that the third state is a final state because it does not set a *next_state* to
transit to::

    import time

    from spade.agent import Agent
    from spade.behaviour import FSMBehaviour, State
    from spade.message import Message

    STATE_ONE = "STATE_ONE"
    STATE_TWO = "STATE_TWO"
    STATE_THREE = "STATE_THREE"


    class ExampleFSMBehaviour(FSMBehaviour):
        async def on_start(self):
            print(f"FSM starting at initial state {self.current_state}")

        async def on_end(self):
            print(f"FSM finished at state {self.current_state}")
            await self.agent.stop()


    class StateOne(State):
        async def run(self):
            print("I'm at state one (initial state)")
            msg = Message(to=str(self.agent.jid))
            msg.body = "msg_from_state_one_to_state_three"
            await self.send(msg)
            self.set_next_state(STATE_TWO)


    class StateTwo(State):
        async def run(self):
            print("I'm at state two")
            self.set_next_state(STATE_THREE)


    class StateThree(State):
        async def run(self):
            print("I'm at state three (final state)")
            msg = await self.receive(timeout=5)
            print(f"State Three received message {msg.body}")
            # no final state is setted, since this is a final state


    class FSMAgent(Agent):
        async def setup(self):
            fsm = ExampleFSMBehaviour()
            fsm.add_state(name=STATE_ONE, state=StateOne(), initial=True)
            fsm.add_state(name=STATE_TWO, state=StateTwo())
            fsm.add_state(name=STATE_THREE, state=StateThree())
            fsm.add_transition(source=STATE_ONE, dest=STATE_TWO)
            fsm.add_transition(source=STATE_TWO, dest=STATE_THREE)
            self.add_behaviour(fsm)


    if __name__ == "__main__":
        fsmagent = FSMAgent("fsmagent@your_xmpp_server", "your_password")
        future = fsmagent.start()
        future.result()

        while fsmagent.is_alive():
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                fsmagent.stop()
                break
        print("Agent finished")




Waiting a Behaviour
-------------------

Sometimes you may need to wait for a behaviour to finish. In order to make this easy, behaviours provide a method called
``join``. Using this method you can wait for a behaviour to be finished. Be careful, since this is a blocking operation.
In order to make it usable inside and outside coroutines, this is also a morphing method (like ``start`` and ``stop``)
which behaves different depending on the context. It returns a coroutine or a future depending on whether it is called
from a coroutine or a synchronous method. Example::

    import asyncio
    import getpass

    from spade import quit_spade
    from spade.agent import Agent
    from spade.behaviour import OneShotBehaviour


    class DummyAgent(Agent):
        class LongBehav(OneShotBehaviour):
            async def run(self):
                await asyncio.sleep(5)
                print("Long Behaviour has finished")

        class WaitingBehav(OneShotBehaviour):
            async def run(self):
                await self.agent.behav.join()  # this join must be awaited
                print("Waiting Behaviour has finished")

        async def setup(self):
            print("Agent starting . . .")
            self.behav = self.LongBehav()
            self.add_behaviour(self.behav)
            self.behav2 = self.WaitingBehav()
            self.add_behaviour(self.behav2)


    if __name__ == "__main__":

        jid = input("JID> ")
        passwd = getpass.getpass()

        dummy = DummyAgent(jid, passwd)
        future = dummy.start()
        future.result()

        dummy.behav2.join()  # this join must not be awaited

        print("Stopping agent.")
        dummy.stop()

        quit_spade()
