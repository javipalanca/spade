=====
SPADE
=====


.. image:: https://img.shields.io/pypi/v/spade.svg
    :target: https://pypi.python.org/pypi/spade

.. image:: https://img.shields.io/pypi/pyversions/spade.svg
    :target: https://pypi.python.org/pypi/spade
    :alt: Python Versions

.. image:: https://img.shields.io/github/languages/count/javipalanca/spade?label=languages
    :alt: Languages
    :target: https://pepy.tech/project/spade

.. image:: https://img.shields.io/github/languages/code-size/javipalanca/spade
    :alt: Code Size
    :target: https://pepy.tech/project/spade

.. image:: https://img.shields.io/pypi/l/spade
    :target: https://opensource.org/licenses/MIT
    :alt: MIT License

.. image:: https://pepy.tech/badge/spade
    :target: https://pepy.tech/project/spade
    :alt: Downloads

.. image:: https://github.com/javipalanca/spade/actions/workflows/python-package.yml/badge.svg
    :target: https://github.com/javipalanca/spade/actions/workflows/python-package.yml
    :alt: Continuous Integration Status

.. image:: https://coveralls.io/repos/github/javipalanca/spade/badge.svg?branch=master
    :target: https://coveralls.io/github/javipalanca/spade?branch=master
    :alt: Code Coverage Status

.. image:: https://readthedocs.org/projects/spade/badge/?version=latest
    :target: https://spade-mas.readthedocs.io?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/pypi/format/spade.svg
    :target: https://pypi.python.org/pypi/spade




Smart Python Agent Development Environment

A multi-agent systems platform written in Python and based on instant messaging (XMPP).

Develop agents that can chat both with other agents and humans.


* Free software: MIT license
* Documentation: http://spade-mas.readthedocs.io/


Features
--------

* Multi-agent platform based on XMPP_
* Presence notification allows the system to know the current state of the agents in real-time
* Python >=3.8
* Asyncio-based
* Agent model based on behaviours
* Supports FIPA metadata using XMPP Data Forms (XEP-0004_: Data Forms)
* Web-based interface
* Incorporates a custom XMPP server (pyjabber)
* Use any XMPP server

Plugins
-------

- **spade_bdi** (BDI agents with AgentSpeak):
        - Code: https://github.com/javipalanca/spade_bdi
        - Documentation: https://spade-bdi.readthedocs.io
- **spade_pubsub** (PubSub protocol for agents):
        - Code: https://github.com/javipalanca/spade_pubsub
        - Documentation: https://spade-pubsub.readthedocs.io
- **spade_artifact** (Artifacts for SPADE):
        - Code: https://github.com/javipalanca/spade_artifact
        - Documentation: https://spade-artifact.readthedocs.io
- **spade_norms** (Norms for SPADE):
        - Code: https://github.com/javipalanca/spade_norms
        - Documentation: https://spade-norms.readthedocs.io/
- **spade_bokeh** (bokeh plots for agents):
        - Code: https://github.com/javipalanca/spade_bokeh
        - Documentation: https://spade-bokeh.readthedocs.io

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _XMPP: http://www.xmpp.org
.. _`XEP-0004` : https://xmpp.org/extensions/xep-0004.html
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

