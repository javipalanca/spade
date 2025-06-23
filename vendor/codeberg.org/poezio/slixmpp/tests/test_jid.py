# -*- encoding: utf8 -*-
from __future__ import unicode_literals
import unittest
from slixmpp.test import SlixTest
from slixmpp import JID, InvalidJID


class TestJIDClass(SlixTest):

    """Verify that the JID class can parse and manipulate JIDs."""

    def testJIDFromFull(self):
        """Test using JID of the form 'user@server/resource/with/slashes'."""
        self.check_jid(JID('user@someserver/some/resource'),
                       'user',
                       'someserver',
                       'some/resource',
                       'user@someserver',
                       'user@someserver/some/resource',
                       'user@someserver/some/resource')

    def testJIDchange(self):
        """Test changing JID of the form 'user@server/resource/with/slashes'"""
        j = JID('user1@someserver1/some1/resource1')
        j.user = 'user'
        j.domain = 'someserver'
        j.resource = 'some/resource'
        self.check_jid(j,
                       'user',
                       'someserver',
                       'some/resource',
                       'user@someserver',
                       'user@someserver/some/resource',
                       'user@someserver/some/resource')

        j.node = None
        self.check_jid(j,
                       None,
                       'someserver',
                       'some/resource',
                       'someserver',
                       'someserver/some/resource',
                       'someserver/some/resource')

        j.resource = None
        self.check_jid(j,
                       None,
                       'someserver',
                       None,
                       'someserver',
                       'someserver',
                       'someserver')

    def testJIDaliases(self):
        """Test changing JID using aliases for domain."""
        j = JID('user@someserver/resource')
        j.server = 'anotherserver'
        self.check_jid(j, domain='anotherserver')
        j.host = 'yetanother'
        self.check_jid(j, domain='yetanother')

    def testJIDSetFullWithUser(self):
        """Test setting the full JID with a user portion."""
        j = JID('user@domain/resource')
        j.full = 'otheruser@otherdomain/otherresource'
        self.check_jid(j,
                       'otheruser',
                       'otherdomain',
                       'otherresource',
                       'otheruser@otherdomain',
                       'otheruser@otherdomain/otherresource',
                       'otheruser@otherdomain/otherresource')

    def testJIDFullNoUserWithResource(self):
        """
        Test setting the full JID without a user
        portion and with a resource.
        """
        j = JID('user@domain/resource')
        j.full = 'otherdomain/otherresource'
        self.check_jid(j,
                       '',
                       'otherdomain',
                       'otherresource',
                       'otherdomain',
                       'otherdomain/otherresource',
                       'otherdomain/otherresource')

    def testJIDFullNoUserNoResource(self):
        """
        Test setting the full JID without a user
        portion and without a resource.
        """
        j = JID('user@domain/resource')
        j.full = 'otherdomain'
        self.check_jid(j,
                       '',
                       'otherdomain',
                       '',
                       'otherdomain',
                       'otherdomain',
                       'otherdomain')

    def testJIDBareUser(self):
        """Test setting the bare JID with a user."""
        j = JID('user@domain/resource')
        j.bare = 'otheruser@otherdomain'
        self.check_jid(j,
                       'otheruser',
                       'otherdomain',
                       'resource',
                       'otheruser@otherdomain',
                       'otheruser@otherdomain/resource',
                       'otheruser@otherdomain/resource')

    def testJIDBareNoUser(self):
        """Test setting the bare JID without a user."""
        j = JID('user@domain/resource')
        j.bare = 'otherdomain'
        self.check_jid(j,
                       '',
                       'otherdomain',
                       'resource',
                       'otherdomain',
                       'otherdomain/resource',
                       'otherdomain/resource')

    def testJIDNoResource(self):
        """Test using JID of the form 'user@domain'."""
        self.check_jid(JID('user@someserver'),
                       'user',
                       'someserver',
                       '',
                       'user@someserver',
                       'user@someserver',
                       'user@someserver')

    def testJIDNoUser(self):
        """Test JID of the form 'component.domain.tld'."""
        self.check_jid(JID('component.someserver'),
                       '',
                       'component.someserver',
                       '',
                       'component.someserver',
                       'component.someserver',
                       'component.someserver')

    def testJIDEquality(self):
        """Test that JIDs with the same content are equal."""
        jid1 = JID('user@domain/resource')
        jid2 = JID('user@domain/resource')
        self.assertTrue(jid1 == jid2, "Same JIDs are not considered equal")
        self.assertFalse(jid1 != jid2, "Same JIDs are considered not equal")

    def testJIDInequality(self):
        jid1 = JID('user@domain/resource')
        jid2 = JID('otheruser@domain/resource')
        self.assertFalse(jid1 == jid2, "Different JIDs are considered equal")
        self.assertTrue(jid1 != jid2, "Different JIDs are considered equal")

    def testZeroLengthDomain(self):
        jid1 = JID('')
        jid2 = JID()
        self.assertTrue(jid1 == jid2, "Empty JIDs are not considered equal")
        self.assertTrue(jid1.domain == '', "Empty JID’s domain part not empty")
        self.assertTrue(jid1.full == '', "Empty JID’s full part not empty")

        self.assertRaises(InvalidJID, JID, 'user@')
        self.assertRaises(InvalidJID, JID, '/resource')
        self.assertRaises(InvalidJID, JID, 'user@/resource')

    def testZeroLengthLocalPart(self):
        self.assertRaises(InvalidJID, JID, '@test.com')
        self.assertRaises(InvalidJID, JID, '@test.com/resource')

    def testZeroLengthNodeDomain(self):
        self.assertRaises(InvalidJID, JID, '@/test.com')

    def testZeroLengthResource(self):
        self.assertRaises(InvalidJID, JID, 'test.com/')
        self.assertRaises(InvalidJID, JID, 'user@test.com/')

    def test1023LengthLocalPart(self):
        local = 'a' * 1023
        jid = JID('%s@test.com' % local)

    def test1023LengthResource(self):
        resource = 'r' * 1023
        jid = JID('test.com/%s' % resource)

    def test1024LengthDomain(self):
        domain = ('a.' * 509) + 'aa.com'
        self.assertRaises(InvalidJID, JID, 'user@%s/resource' % domain)
        self.assertRaises(InvalidJID, JID, 'user@%s' % domain)
        self.assertRaises(InvalidJID, JID, '%s/resource' % domain)
        self.assertRaises(InvalidJID, JID, domain)

    def test1024LengthLocalPart(self):
        local = 'a' * 1024
        self.assertRaises(InvalidJID, JID, '%s@test.com' % local)
        self.assertRaises(InvalidJID, JID, '%s@test.com/resource' % local)

    def test1024LengthResource(self):
        resource = 'r' * 1024
        self.assertRaises(InvalidJID, JID, 'test.com/%s' % resource)
        self.assertRaises(InvalidJID, JID, 'user@test.com/%s' % resource)

    def testTooLongDomainLabel(self):
        domain = ('a' * 64) + '.com'
        self.assertRaises(InvalidJID, JID, 'user@%s/resource' % domain)

    def testDomainEmptyLabel(self):
        domain = 'aaa..bbb.com'
        self.assertRaises(InvalidJID, JID, 'user@%s/resource' % domain)

    def testDomainIPv4(self):
        domain = '127.0.0.1'

        jid1 = JID('%s' % domain)
        jid2 = JID('user@%s' % domain)
        jid3 = JID('%s/resource' % domain)
        jid4 = JID('user@%s/resource' % domain)

    def testDomainIPv6(self):
        domain = '[::1]'

        jid1 = JID('%s' % domain)
        jid2 = JID('user@%s' % domain)
        jid3 = JID('%s/resource' % domain)
        jid4 = JID('user@%s/resource' % domain)

    def testDomainInvalidIPv6NoBrackets(self):
        domain = '::1'

        self.assertRaises(InvalidJID, JID, '%s' % domain)
        self.assertRaises(InvalidJID, JID, 'user@%s' % domain)
        self.assertRaises(InvalidJID, JID, '%s/resource' % domain)
        self.assertRaises(InvalidJID, JID, 'user@%s/resource' % domain)

    def testDomainInvalidIPv6MissingBracket(self):
        domain = '[::1'

        self.assertRaises(InvalidJID, JID, '%s' % domain)
        self.assertRaises(InvalidJID, JID, 'user@%s' % domain)
        self.assertRaises(InvalidJID, JID, '%s/resource' % domain)
        self.assertRaises(InvalidJID, JID, 'user@%s/resource' % domain)

    def testDomainInvalidIPv6WrongBracket(self):
        domain = '[::]1]'

        self.assertRaises(InvalidJID, JID, '%s' % domain)
        self.assertRaises(InvalidJID, JID, 'user@%s' % domain)
        self.assertRaises(InvalidJID, JID, '%s/resource' % domain)
        self.assertRaises(InvalidJID, JID, 'user@%s/resource' % domain)

    def testDomainWithPort(self):
        domain = 'example.com:5555'

        self.assertRaises(InvalidJID, JID, '%s' % domain)
        self.assertRaises(InvalidJID, JID, 'user@%s' % domain)
        self.assertRaises(InvalidJID, JID, '%s/resource' % domain)
        self.assertRaises(InvalidJID, JID, 'user@%s/resource' % domain)

    def testDomainWithTrailingDot(self):
        domain = 'example.com.'
        jid = JID('user@%s/resource' % domain)

        self.assertEqual(jid.domain, 'example.com')

    def testDomainWithDashes(self):
        domain = 'example.com-'
        self.assertRaises(InvalidJID, JID, 'user@%s/resource' % domain)

        domain = '-example.com'
        self.assertRaises(InvalidJID, JID, 'user@%s/resource' % domain)

    def testStartOrEndWithEscapedSpaces(self):
        local = ' foo'
        self.assertRaises(InvalidJID, JID, '%s@example.com' % local)

        local = 'bar '
        self.assertRaises(InvalidJID, JID, '%s@example.com' % local)

        # Need more input for these cases. A JID starting with \20 *is* valid
        # according to RFC 6122, but is not according to XEP-0106.
        #self.assertRaises(InvalidJID, JID, '%s@example.com' % '\\20foo2')
        #self.assertRaises(InvalidJID, JID, '%s@example.com' % 'bar2\\20')

    def testJapaneseLocalpart(self):
        jid = JID('あいうえお@example.com')
        self.assertEqual(jid.node, 'あいうえお')
        self.assertEqual(jid.domain, 'example.com')

    def testHash(self):
        jid = JID('あいうえお@example.com')
        self.assertEqual(hash(jid.full), hash(jid))
        jid = JID('toto@example.com/aaa')
        self.assertEqual(hash(jid.full), hash(jid))
        jid = JID('totoéà@example.com/aaa')
        self.assertEqual(hash(jid.full), hash(jid))

    def test_comparison_invalid(self):
        jid = JID('toto@example.com')
        self.assertFalse(jid == "@@@@")
        self.assertFalse(jid in ["abc", "def", "@@@@"])


suite = unittest.TestLoader().loadTestsFromTestCase(TestJIDClass)
