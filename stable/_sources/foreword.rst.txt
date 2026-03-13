========
Foreword
========

The idea of an XMPP-based agent platform appeared one night at 4 A.M. when, studying the features of the Jabber
architecture, we found out great similarities with the ones of a FIPA-compliant agent platform. The XMPP protocol
offered a great architecture for agents to communicate in a structured way and solved many issues present when designing
a platform, such as authenticating the users (the agents), provide a directory or create communication channels.

We started to work on our first prototype of this Jabber-powered platform and within a week we had a small working proof
of concept by the name of *Fipper* which eventually allowed for dumb agents to connect and communicate through a common
XMPP server.

Since that day, things have changed a bit. The small proof of concept evolved into a full-featured FIPA platform, and
the new SPADE name was coined. As usual, we later had to find the meaning of the beautiful acronym. We came up with
**Smart Python multi-Agent Development Environment**, which sounded both good and geek enough.

The years passed, and everything evolved except the platform. Python reached version 3, which came with lots of
interesting changes and improvements. We also became better programmers (just because of the grounding and the
experience that the years give), we met the `PEP8 <https://www.python.org/dev/peps/pep-0008/>`_ and the  `Clean Code
principles <http://www.matthewrenze.com/articles/what-is-clean-code/>`_ and they opened our eyes to a new world. That's
why in 2017 SPADE was fully rewritten in Python 3.6, using asyncio and strictly following PEP8 and Clean Code principles.

We hope you like this software and have as much fun using it as we had writing it. Of course we also hope that it may
become useful, but that is a secondary matter.
