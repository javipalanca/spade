=======
History
=======

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

* Started writting 3.0 version.
