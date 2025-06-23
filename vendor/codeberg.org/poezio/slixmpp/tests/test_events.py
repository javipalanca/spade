import time
import unittest
from slixmpp.test import SlixTest


class TestEvents(SlixTest):

    def setUp(self):
        self.stream_start()

    def testEventHappening(self):
        """Test handler working"""
        happened = []

        def handletestevent(event):
            happened.append(True)

        self.xmpp.add_event_handler("test_event", handletestevent)
        self.xmpp.event("test_event")
        self.xmpp.event("test_event")

        msg = "Event was not triggered the correct number of times: %s"
        self.assertTrue(happened == [True, True], msg)

    def testDelEvent(self):
        """Test handler working, then deleted and not triggered"""
        happened = []

        def handletestevent(event):
            happened.append(True)

        self.xmpp.add_event_handler("test_event", handletestevent)
        self.xmpp.event("test_event", {})

        self.xmpp.del_event_handler("test_event", handletestevent)

        # Should not trigger because it was deleted
        self.xmpp.event("test_event", {})

        msg = "Event was not triggered the correct number of times: %s"
        self.assertTrue(happened == [True], msg % happened)

    def testAddDelAddEvent(self):
        """Test adding, then removing, then adding an event handler."""
        happened = []

        def handletestevent(event):
            happened.append(True)

        self.xmpp.add_event_handler("test_event", handletestevent)
        self.xmpp.event("test_event", {})

        self.xmpp.del_event_handler("test_event", handletestevent)
        # Should not trigger because it was deleted
        self.xmpp.event("test_event", {})

        self.xmpp.add_event_handler("test_event", handletestevent)
        self.xmpp.event("test_event", {})

        msg = "Event was not triggered the correct number of times: %s"
        self.assertTrue(happened == [True, True], msg % happened)

    def testDisposableEvent(self):
        """Test disposable handler working, then not being triggered again."""
        happened = []

        def handletestevent(event):
            happened.append(True)

        self.xmpp.add_event_handler("test_event", handletestevent,
                                    disposable=True)
        self.xmpp.event("test_event", {})

        # Should not trigger because it was deleted
        self.xmpp.event("test_event", {})

        msg = "Event was not triggered the correct number of times: %s"
        self.assertTrue(happened == [True], msg % happened)


suite = unittest.TestLoader().loadTestsFromTestCase(TestEvents)
