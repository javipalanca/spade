# Overview
[![Downloads](https://pypip.in/d/SPADE/badge.png)](https://pypi.python.org/pypi/SPADE)
[![Version](https://pypip.in/v/SPADE/badge.png)](https://pypi.python.org/pypi/SPADE)
[![Build Status](https://travis-ci.org/javipalanca/spade.png)](https://travis-ci.org/javipalanca/spade)

SPADE (Smart Python multi-Agent Development Environment) is a Multiagent and Organizations Platform based on the <a href="http://www.xmpp.org">XMPP/Jabber technology</a> and written in the <a href="http://www.python.org">Python</a> programming language. This technology offers by itself many features and facilities that ease the construction of MAS, such as an existing communication channel, the concepts of users (agents) and servers (platforms) and an extensible communication protocol based on XML, just like <a href="http://www.fipa.org">FIPA-ACL</a>. Many other agent platforms exist, but SPADE is the first to base its roots on the XMPP technology.

<img src="http://spade2.googlecode.com/files/spade_overview.png" height=420px/> 

# User Documentation

- [User Manual](http://packages.python.org/SPADE/index.html)

# Installing

You can install SPADE with easy_install or pip:

    pip install SPADE

or

    easy_install SPADE

It can also be installed from inside the package using the setup.py script:

    python setup.py install

...and the package will install automatically.

# Features

The main features of SPADE are:
- Developed using Python
- Covers the FIPA standard
- Implements four MTPs: XMPP, P2P, HTTP and SIMBA
- Supports two content languages: FIPA-SL and RDF
- SPADE agents do reach their goals by running deliberative and reactive tasks
- Has a web interface to manage the platform
- Allows its execution in several platforms and operating systems
- Presence notification allows the system to determine the current state of the agents in real-time
- Multi-user conference allows agents to create organizations and groups of agents

The SPADE Agent Platform does not require (but strongly recommends) the operation of agents made with the SPADE Agent Library. The platform itself uses the library to empower its internals, but aside from that, you can develop your own agents in the programming language of your choice and use them with SPADE. The only requirement those agents must fulfill is to be able to communicate through the XMPP protocol. The FIPA-ACL messages will be embedded in XMPP messages. Be warned, however, that some features of the whole SPADE experience may not be available if you do not use the SPADE Agent Library to build your agents.

The SPADE Agent Library is a module for the Python programming language for building SPADE agents. It is a collection of classes, functions and tools for creating new SPADE agents that can work with the SPADE Agent Platform. Using it is the best way to start developing your own SPADE agents. In the future, we would like to offer bindings of the SPADE Agent Library for more programming languages, like Java or C#, but for now only Python is supported.

If you have worked with Python before, you will find the SPADE Agent Library easy to understand and use, with classes ready to use and expand, and many functionalities already built in the library. If you have worked with other high-level behavioral agent platforms (like Jade or Madkit) you will find some similarities in the way the library works, although the agent model present in SPADE is a bit different.
