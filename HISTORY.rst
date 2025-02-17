=======
History
=======

4.0.3 (2025-02-17)
--------------------
* Prepare XMPP messages linked to client stream.
* Added CLI support for in-memory database in the XMPP server.
* Added CLI support for custom connection timeout.
* Fixed bug in XMPP sending method.

4.0.2 (2025-01-09)
--------------------
* Fixed bug sending messages to external agents.

4.0.1 (2024-12-26)
--------------------

* Fixed minor bugs.
* Agents are now stopped when Ctrl+C is pressed.
* Added --debug flag to the CLI.
* Updated documentation config file.
* Lint examples.

4.0.0 (2024-12-19)
--------------------

* Added custom XMPP server as cli.
* Migrated to pyproject.
* Migrated linter to ruff.
* Improved presence management API.
* Agents can now select the XMPP port.
* Use uvloop or winloop if available.

3.3.3 (2024-09-05)
------------------

* Added support to Python 3.11 and 3.12
* Upgraded aiohttp to 3.10.5.
* Fixed viz.js CDN

3.3.2 (2023-09-18)
------------------

* Added add_template_path function to the web component.

3.3.1 (2023-09-18)
------------------

* Added menu entries support for the web interface.
* Minor typos in documentation.

3.3.0 (2023-06-13)
------------------

* Updated to Python>=3.8
* Changed the way agents are launched (now with `spade.run()`)
* Python 3.11 still not supported due to a bug in `aiohttp`
* Deprecated support for Python<=3.7

3.2.3 (2022-12-13)
------------------

* Updated third-party libs

3.2.2 (2021-11-25)
------------------

* Hotfix for the event loop in windows when python is 3.6

3.2.1 (2021-11-16)
------------------

* Fixed event loop for windows

3.2.0 (2021-07-13)
------------------

* Added support for Python 3.8 and 3.9
* Fixed support for Linux, Windows and macOS

3.1.9 (2021-07-08)
------------------

* Minor fix in docs.

3.1.8 (2021-07-08)
------------------

* Added examples.
* Fixed documentation examples.
* Added Github CI support.

3.1.7 (2021-06-25)
------------------

* Added hooks for plugins.
* Minor bug fixings.

3.1.6 (2020-05-22)
------------------

* Fixed coverage and ci.

3.1.5 (2020-05-21)
------------------

* Fixed how to stop behaviours.
* Fixed some tests.
* Blackstyled code.

3.1.4 (2019-11-04)
------------------

* Fixed issue with third party versions.
* Use factories in tests.
* Updated documentation and examples.
* Minor bug fixing.

3.1.3 (2019-07-18)
------------------

* Added BDI plugin (https://github.com/javipalanca/spade_bdi).
* Improved the platform stop (quit_spade).
* Minor bug fixing.

3.1.2 (2019-05-14)
------------------

* Hotfix docs.

3.1.1 (2019-05-14)
------------------

* Added Python 3.7 support.
* Added Code of Conduct.
* Minor bugs fixed.

3.1.0 (2019-03-22)
------------------

* Agents now run in a single event loop managed by the container.
* Behaviors can be waited for using the "join" method.
* To check if a behaviours is done you can now use the "is_done" method.
* The "setup" method is now a coroutine.
* New "quit_spade" helper to stop the whole process.
* The "start" and "stop" methods change depending on the context, since it is the container who will properly start or stop the agent.
  They return a coroutine or a future depending on whether they are called from a coroutine or a synchronous method.

3.0.9 (2018-10-24)
------------------

* Added raw parameter to allow raw web responses.
* Changed default agent urls to the "/spade" namespace to avoid conflicts.

3.0.8 (2018-10-02)
------------------

* Added a container mechanism to speedup local sends.
* Added performance example.
* Improved API doc.
* Added container tests.

3.0.7 (2018-09-27)
------------------

* Fixed bug when running FSM states.
* Improved Message __str__.
* Fixed bug when thread is not defined in a message.
* aioxmpp send method is now in client instead of stream.

3.0.6 (2018-09-27)
------------------

* Added statement to relinquish the cpu at each behaviour loop.
* Message Thread is now stored as metadata for simplicity.

3.0.5 (2018-09-21)
------------------

* Added JSON responses in web module.
* Some improvements in aiothread management.

3.0.4 (2018-09-20)
------------------

* Added coroutines to start agents from within other agents.
* Improved API doc format.


3.0.3 (2018-09-12)
------------------

* Rename internal templates to avoid conflicts.
* Added API doc.
* Minor bug fixes.

3.0.2 (2018-09-12)
------------------

* Fixed presence notification updates.
* Fixed FSM graphviz visualization.
* Raise AuthenticationFailure Exception when user is not registered or user or password is wrong.
* Import init improvements.
* Attribute auto_register is now default True.
* Improved documentation.
* Other minor fixes.

3.0.1 (2018-09-07)
------------------

* Minor doc fixings and improvements.


3.0.0 (2017-10-06)
------------------

* Started writing 3.0 version.
