=====
Usage
=====

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
