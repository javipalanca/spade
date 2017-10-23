========================
Behaviours and Templates
========================

There are more complex types of behaviours that you can use in SPADE. Let's see some of them.

Periodic Behaviour
------------------

This behaviour runs its ``run()`` body at a scheduled ``period``. This period is set in seconds.
You can also delay the startup of the periodic behaviour by setting a datetime in the ``start_at`` parameter.

.. warning:: Remember to change the example's jids and passwords by your own accounts. These accounts do not exist
    and are only for demonstration purposes.

Let's see an example::

    import datetime
    import time
    from spade.agent import Agent
    from spade.behaviour import Behaviour, PeriodicBehaviour
    from spade.message import Message
    from spade.template import Template


    class PeriodicSenderAgent(Agent):
        class InformBehav(PeriodicBehaviour):
            async def run(self):
                print(f"PeriodicSenderBehaviour running at {datetime.datetime.now().time()}: {self.counter}")
                msg = Message(to="receiver@your_xmpp_server")  # Instantiate the message
                msg.body = "Hello World"  # Set the message content

                await self.send(msg)
                print("Message sent!")

                if self.counter == 5:
                    self.kill()
                self.counter += 1

            async def on_end(self):
                # stop agent from behaviour
                self.agent.stop()

            async def on_start(self):
                self.counter = 0

        def setup(self):
            print(f"PeriodicSenderAgent started at {datetime.datetime.now().time()}")
            start_at = datetime.datetime.now() + datetime.timedelta(seconds=5)
            b = self.InformBehav(period=2, start_at=start_at)
            self.add_behaviour(b)


    class ReceiverAgent(Agent):
        class RecvBehav(Behaviour):
            async def run(self):
                print("RecvBehav running")
                msg = await self.receive(timeout=10)  # wait for a message for 10 seconds
                if msg:
                    print("Message received with content: {}".format(msg.body))
                else:
                    print("Did not received any message after 10 seconds")
                    self.kill()

            async def on_end(self):
                self.agent.stop()

        def setup(self):
            print("ReceiverAgent started")
            b = self.RecvBehav()
            self.add_behaviour(b)


    if __name__ == "__main__":
        receiveragent = ReceiverAgent("receiver@your_xmpp_server", "receiver_password")
        time.sleep(1) # wait for receiver agent to be prepared. In next sections we'll use presence notification.
        senderagent = PeriodicSenderAgent("sender@your_xmpp_server", "sender_password")

        while receiveragent.is_alive():
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                senderagent.stop()
                receiveragent.stop()
                break
        print("Agents finished")

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

