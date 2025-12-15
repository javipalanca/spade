.. highlight:: shell

============
Installation
============


Stable release
--------------

**Adding SPADE to your Python project**

We recommend using `uv`_ to manage your Python projects. It's fast and makes dependency management easy.

If you don't have `uv` installed, see the `uv installation guide`_.

If you haven't created a `uv`-managed project yet, create one:

.. code-block:: console

    $ uv init spade-demo
    $ cd spade-demo

Then add SPADE to your project dependencies:

.. code-block:: console

    $ uv add spade

**Installing SPADE without a project**

If you don't want to create a `uv` project, you can still install SPADE globally using `uv`'s `pip` interface:

.. code-block:: console

    $ uv pip install spade

**Traditional installation with pip**

For projects using `pip` directly for dependencies:

.. code-block:: console

    $ pip install spade

This will install the most recent stable release. If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _uv: https://docs.astral.sh/uv/
.. _uv installation guide: https://docs.astral.sh/uv/getting-started/installation/
.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


From sources
------------

The sources for SPADE can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/javipalanca/spade

Or download the `tarball`_:

.. code-block:: console

    $ curl  -OL https://github.com/javipalanca/spade/tarball/master

Once you have a copy of the source, you can install it with `uv` (recommended):

.. code-block:: console

    $ uv sync

Or with `pip` (traditional method):

.. code-block:: console

    $ pip install -e .

For development purposes, you can install with development dependencies:

.. code-block:: console

    $ uv sync --extra dev

Or with `pip`:

.. code-block:: console

    $ pip install -e .[dev]


.. _Github repo: https://github.com/javipalanca/spade
.. _tarball: https://github.com/javipalanca/spade/tarball/master
