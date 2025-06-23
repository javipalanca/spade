"""
    Slixmpp: The Slick XMPP Library
    Copyright (C) 2017 Emmanuel Gil Peyrot
    This file is part of Slixmpp.

    See the file LICENSE for copying permission.
"""

import unittest
from slixmpp import Iq
from slixmpp.test import SlixTest
from slixmpp.plugins.xep_0300 import Hash
from slixmpp.xmlstream import register_stanza_plugin


class TestHash(SlixTest):

    def setUp(self):
        register_stanza_plugin(Iq, Hash)

    def testSimpleElement(self):
        """Test that the element is created correctly."""
        iq = Iq()
        iq['type'] = 'set'
        iq['hash']['algo'] = 'sha-256'
        iq['hash']['value'] = 'EQgS9n+h4fARf289cCQcGkKnsHcRqTwkd8xRbZBC+ds='

        self.check(iq, """
          <iq type="set">
            <hash xmlns="urn:xmpp:hashes:2" algo="sha-256">EQgS9n+h4fARf289cCQcGkKnsHcRqTwkd8xRbZBC+ds=</hash>
          </iq>
        """)

    def testInvalidAlgo(self):
        """Test that invalid algos raise an exception."""
        iq = Iq()
        iq['type'] = 'set'
        try:
            iq['hash']['algo'] = 'coucou'
        except ValueError:
            pass
        else:
            raise self.failureException

    #def testDisabledAlgo(self):
    #    """Test that disabled algos aren’t used."""
    #    iq = Iq()
    #    iq['type'] = 'set'
    #    try:
    #        iq['hash']['algo'] = 'sha-1'
    #    except ValueError:
    #        pass
    #    else:
    #        raise self.failureException


suite = unittest.TestLoader().loadTestsFromTestCase(TestHash)
