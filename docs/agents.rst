====================
Agent communitcation
====================

Sending and Receiving Messages
------------------------------

As you know, messages are the basis of every MAS. They are the centre of the whole "computing as interaction" paradigm
in which MAS are based. So it is very important to understand which facilities are present in SPADE to work with
agent messages.

First and foremost, threre is a ``Message`` class. This class is ``spade.message.Message`` and you can instantiate it to
create new messages to work with. The class provides a method to introduce metadata into messages, this is useful for
using the fields present in standard FIPA-ACL Messages. When a message is ready to be sent, it can be passed on to the
send() method of the behaviour, which will trigger the internal communication process to actually send it to its
destination. Here is a self-explaining example::

    import time
    from spade.agent import Agent
    from spade.behaviour import OneShotBehaviour
    from spade.message import Message


    class SenderAgent(Agent):
        class InformBehav(OneShotBehaviour):
            async def run(self):
                print("Behaviour running")
                msg = Message(to="receiver@jabber.org")     # Instantiate the message
                msg.set_metadata("performative", "inform")  # Set the "inform" FIPA performative
                msg.set_metadata("ontology", "myOntology")  # Set the ontology of the message content
                msg.set_metadata("language", "OWL-S")       # Set the language of the message content
                msg.body = "Hello World"                    # Set the message content

                self.send(msg)
                print("Message sent!")

                # stop agent from behaviour
                self.agent.stop()

        def setup(self):
            print("Agent started")
            b = self.InformBehav()
            self.add_behaviour(b)


    if __name__ == "__main__":
        agent = SenderAgent("sender@jabber.org", "sender_password")

        while agent.is_alive():
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                agent.stop()
                break
        print("Agent finished")

