import asyncio
import time

import unittest
from slixmpp.test import SlixTest


class TestStreamDisco(SlixTest):

    """
    Test using the XEP-0030 plugin.
    """

    def testInfoEmptyDefaultNode(self):
        """
        Info query result from an entity MUST have at least one identity
        and feature, namely http://jabber.org/protocol/disco#info.

        Since the XEP-0030 plugin is loaded, a disco response should
        be generated and not an error result.
        """
        self.stream_start(mode='client',
                          plugins=['xep_0030'])

        self.recv("""
          <iq type="get" id="test">
            <query xmlns="http://jabber.org/protocol/disco#info" />
          </iq>
        """)

        self.send("""
          <iq type="result" id="test">
            <query xmlns="http://jabber.org/protocol/disco#info">
              <identity category="client" type="bot" />
              <feature var="http://jabber.org/protocol/disco#info" />
            </query>
          </iq>
        """)

    def testInfoEmptyDefaultNodeComponent(self):
        """
        Test requesting an empty, default node using a Component.
        """
        self.stream_start(mode='component',
                          jid='tester.localhost',
                          plugins=['xep_0030'])

        self.recv("""
          <iq type="get" id="test">
            <query xmlns="http://jabber.org/protocol/disco#info" />
          </iq>
        """)

        self.send("""
          <iq type="result" id="test">
            <query xmlns="http://jabber.org/protocol/disco#info">
              <identity category="component" type="generic" />
              <feature var="http://jabber.org/protocol/disco#info" />
            </query>
          </iq>
        """)

    def testInfoIncludeNode(self):
        """
        Results for info queries directed to a particular node MUST
        include the node in the query response.
        """
        self.stream_start(mode='client',
                          plugins=['xep_0030'])


        self.xmpp['xep_0030'].static.add_node(node='testing')

        self.recv("""
          <iq to="tester@localhost/resource" type="get" id="test">
            <query xmlns="http://jabber.org/protocol/disco#info"
                   node="testing" />
          </iq>
        """)

        self.send("""
          <iq type="result" id="test">
            <query xmlns="http://jabber.org/protocol/disco#info"
                   node="testing">
            </query>
          </iq>""",
          method='mask')

    def testItemsIncludeNode(self):
        """
        Results for items queries directed to a particular node MUST
        include the node in the query response.
        """
        self.stream_start(mode='client',
                          plugins=['xep_0030'])


        self.xmpp['xep_0030'].static.add_node(node='testing')

        self.recv("""
          <iq to="tester@localhost/resource" type="get" id="test">
            <query xmlns="http://jabber.org/protocol/disco#items"
                   node="testing" />
          </iq>
        """)

        self.send("""
          <iq type="result" id="test">
            <query xmlns="http://jabber.org/protocol/disco#items"
                   node="testing">
            </query>
          </iq>""",
          method='mask')

    def testDynamicInfoJID(self):
        """
        Test using a dynamic info handler for a particular JID.
        """
        self.stream_start(mode='client',
                          plugins=['xep_0030'])

        def dynamic_jid(jid, node, ifrom, iq):
            result = self.xmpp['xep_0030'].stanza.DiscoInfo()
            result['node'] = node
            result.add_identity('client', 'console', name='Dynamic Info')
            return result

        self.xmpp['xep_0030'].set_node_handler('get_info',
                                               jid='tester@localhost',
                                               handler=dynamic_jid)

        self.recv("""
          <iq type="get" id="test" to="tester@localhost">
            <query xmlns="http://jabber.org/protocol/disco#info"
                   node="testing" />
          </iq>
        """)

        self.send("""
          <iq type="result" id="test">
            <query xmlns="http://jabber.org/protocol/disco#info"
                   node="testing">
              <identity category="client"
                        type="console"
                        name="Dynamic Info" />
            </query>
          </iq>
        """)

    def testDynamicInfoGlobal(self):
        """
        Test using a dynamic info handler for all requests.
        """
        self.stream_start(mode='component',
                          jid='tester.localhost',
                          plugins=['xep_0030'])

        def dynamic_global(jid, node, ifrom, iq):
            result = self.xmpp['xep_0030'].stanza.DiscoInfo()
            result['node'] = node
            result.add_identity('component', 'generic', name='Dynamic Info')
            return result

        self.xmpp['xep_0030'].set_node_handler('get_info',
                                               handler=dynamic_global)

        self.recv("""
          <iq type="get" id="test"
              to="user@tester.localhost"
              from="tester@localhost">
            <query xmlns="http://jabber.org/protocol/disco#info"
                   node="testing" />
          </iq>
        """)

        self.send("""
          <iq type="result" id="test"
              to="tester@localhost"
              from="user@tester.localhost">
            <query xmlns="http://jabber.org/protocol/disco#info"
                   node="testing">
              <identity category="component"
                        type="generic"
                        name="Dynamic Info" />
            </query>
          </iq>
        """)

    def testOverrideJIDInfoHandler(self):
        """Test overriding a JID info handler."""
        self.stream_start(mode='client',
                          plugins=['xep_0030'])

        def dynamic_jid(jid, node, ifrom, iq):
            result = self.xmpp['xep_0030'].stanza.DiscoInfo()
            result['node'] = node
            result.add_identity('client', 'console', name='Dynamic Info')
            return result

        self.xmpp['xep_0030'].set_node_handler('get_info',
                                               jid='tester@localhost',
                                               handler=dynamic_jid)


        self.xmpp['xep_0030'].restore_defaults(jid='tester@localhost',
                                               node='testing')

        self.xmpp['xep_0030'].add_identity(jid='tester@localhost',
                                           node='testing',
                                           category='automation',
                                           itype='command-list')

        self.recv("""
          <iq type="get" id="test" to="tester@localhost">
            <query xmlns="http://jabber.org/protocol/disco#info"
                   node="testing" />
          </iq>
        """)

        self.send("""
          <iq type="result" id="test">
            <query xmlns="http://jabber.org/protocol/disco#info"
                   node="testing">
              <identity category="automation"
                        type="command-list" />
            </query>
          </iq>
        """)

    def testOverrideGlobalInfoHandler(self):
        """Test overriding the global JID info handler."""
        self.stream_start(mode='component',
                          jid='tester.localhost',
                          plugins=['xep_0030'])

        def dynamic_global(jid, node, ifrom, iq):
            result = self.xmpp['xep_0030'].stanza.DiscoInfo()
            result['node'] = node
            result.add_identity('component', 'generic', name='Dynamic Info')
            return result

        self.xmpp['xep_0030'].set_node_handler('get_info',
                                               handler=dynamic_global)

        self.xmpp['xep_0030'].restore_defaults(jid='user@tester.localhost',
                                               node='testing')

        self.xmpp['xep_0030'].add_feature(jid='user@tester.localhost',
                                          node='testing',
                                          feature='urn:xmpp:ping')

        self.recv("""
          <iq type="get" id="test"
              to="user@tester.localhost"
              from="tester@localhost">
            <query xmlns="http://jabber.org/protocol/disco#info"
                   node="testing" />
          </iq>
        """)

        self.send("""
          <iq type="result" id="test"
              to="tester@localhost"
              from="user@tester.localhost">
            <query xmlns="http://jabber.org/protocol/disco#info"
                   node="testing">
              <feature var="urn:xmpp:ping" />
            </query>
          </iq>
        """)

    def testGetInfoRemote(self):
        """
        Test sending a disco#info query to another entity
        and receiving the result.
        """
        self.stream_start(mode='client',
                          plugins=['xep_0030'])

        events = set()

        def handle_disco_info(iq):
            events.add('disco_info')


        self.xmpp.add_event_handler('disco_info', handle_disco_info)


        self.xmpp.wrap(self.xmpp['xep_0030'].get_info('user@localhost', 'foo'))
        self.wait_()

        self.send("""
          <iq type="get" to="user@localhost" id="1">
            <query xmlns="http://jabber.org/protocol/disco#info"
                   node="foo" />
          </iq>
        """)

        self.recv("""
          <iq type="result" to="tester@localhost" id="1">
            <query xmlns="http://jabber.org/protocol/disco#info"
                   node="foo">
              <identity category="client" type="bot" />
              <feature var="urn:xmpp:ping" />
            </query>
          </iq>
        """)

        self.assertEqual(events, {'disco_info'},
                "Disco info event was not triggered: %s" % events)

    def testDynamicItemsJID(self):
        """
        Test using a dynamic items handler for a particular JID.
        """
        self.stream_start(mode='client',
                          plugins=['xep_0030'])

        def dynamic_jid(jid, node, ifrom, iq):
            result = self.xmpp['xep_0030'].stanza.DiscoItems()
            result['node'] = node
            result.add_item('tester@localhost', node='foo', name='JID')
            return result

        self.xmpp['xep_0030'].set_node_handler('get_items',
                                               jid='tester@localhost',
                                               handler=dynamic_jid)

        self.recv("""
          <iq type="get" id="test" to="tester@localhost">
            <query xmlns="http://jabber.org/protocol/disco#items"
                   node="testing" />
          </iq>
        """)

        self.send("""
          <iq type="result" id="test">
            <query xmlns="http://jabber.org/protocol/disco#items"
                   node="testing">
              <item jid="tester@localhost" node="foo" name="JID" />
            </query>
          </iq>
        """)

    def testDynamicItemsGlobal(self):
        """
        Test using a dynamic items handler for all requests.
        """
        self.stream_start(mode='component',
                          jid='tester.localhost',
                          plugins=['xep_0030'])

        def dynamic_global(jid, node, ifrom, iq):
            result = self.xmpp['xep_0030'].stanza.DiscoItems()
            result['node'] = node
            result.add_item('tester@localhost', node='foo', name='Global')
            return result

        self.xmpp['xep_0030'].set_node_handler('get_items',
                                               handler=dynamic_global)

        self.recv("""
          <iq type="get" id="test"
              to="user@tester.localhost"
              from="tester@localhost">
            <query xmlns="http://jabber.org/protocol/disco#items"
                   node="testing" />
          </iq>
        """)

        self.send("""
          <iq type="result" id="test"
              to="tester@localhost"
              from="user@tester.localhost">
            <query xmlns="http://jabber.org/protocol/disco#items"
                   node="testing">
              <item jid="tester@localhost" node="foo" name="Global" />
            </query>
          </iq>
        """)

    def testOverrideJIDItemsHandler(self):
        """Test overriding a JID items handler."""
        self.stream_start(mode='client',
                          plugins=['xep_0030'])

        def dynamic_jid(jid, node, ifrom, iq):
            result = self.xmpp['xep_0030'].stanza.DiscoItems()
            result['node'] = node
            result.add_item('tester@localhost', node='foo', name='Global')
            return result

        self.xmpp['xep_0030'].set_node_handler('get_items',
                                               jid='tester@localhost',
                                               handler=dynamic_jid)


        self.xmpp['xep_0030'].restore_defaults(jid='tester@localhost',
                                               node='testing')

        self.xmpp['xep_0030'].add_item(ijid='tester@localhost',
                                       node='testing',
                                       jid='tester@localhost',
                                       subnode='foo',
                                       name='Test')

        self.recv("""
          <iq type="get" id="test" to="tester@localhost">
            <query xmlns="http://jabber.org/protocol/disco#items"
                   node="testing" />
          </iq>
        """)

        self.send("""
          <iq type="result" id="test">
            <query xmlns="http://jabber.org/protocol/disco#items"
                   node="testing">
              <item jid="tester@localhost" node="foo" name="Test" />
            </query>
          </iq>
        """)

    def testOverrideGlobalItemsHandler(self):
        """Test overriding the global JID items handler."""
        self.stream_start(mode='component',
                          jid='tester.localhost',
                          plugins=['xep_0030'])

        def dynamic_global(jid, node, ifrom, iq):
            result = self.xmpp['xep_0030'].stanza.DiscoItems()
            result['node'] = node
            result.add_item('tester.localhost', node='foo', name='Global')
            return result

        self.xmpp['xep_0030'].set_node_handler('get_items',
                                               handler=dynamic_global)

        self.xmpp['xep_0030'].restore_defaults(jid='user@tester.localhost',
                                               node='testing')

        self.xmpp['xep_0030'].add_item(ijid='user@tester.localhost',
                                       node='testing',
                                       jid='user@tester.localhost',
                                       subnode='foo',
                                       name='Test')

        self.recv("""
          <iq type="get" id="test"
              to="user@tester.localhost"
              from="tester@localhost">
            <query xmlns="http://jabber.org/protocol/disco#items"
                   node="testing" />
          </iq>
        """)

        self.send("""
          <iq type="result" id="test"
              to="tester@localhost"
              from="user@tester.localhost">
            <query xmlns="http://jabber.org/protocol/disco#items"
                   node="testing">
              <item jid="user@tester.localhost" node="foo" name="Test" />
            </query>
          </iq>
        """)

    def testGetItemsRemote(self):
        """
        Test sending a disco#items query to another entity
        and receiving the result.
        """
        self.stream_start(mode='client',
                          plugins=['xep_0030'])

        events = set()
        results = set()

        def handle_disco_items(iq):
            events.add('disco_items')
            results.update(iq['disco_items']['items'])


        self.xmpp.add_event_handler('disco_items', handle_disco_items)

        self.xmpp.wrap(self.xmpp['xep_0030'].get_items('user@localhost', 'foo'))
        self.wait_()

        self.send("""
          <iq type="get" to="user@localhost" id="1">
            <query xmlns="http://jabber.org/protocol/disco#items"
                   node="foo" />
          </iq>
        """)

        self.recv("""
          <iq type="result" to="tester@localhost" id="1">
            <query xmlns="http://jabber.org/protocol/disco#items"
                   node="foo">
              <item jid="user@localhost" node="bar" name="Test" />
              <item jid="user@localhost" node="baz" name="Test 2" />
            </query>
          </iq>
        """)

        items = {('user@localhost', 'bar', 'Test'),
                 ('user@localhost', 'baz', 'Test 2')}
        self.assertEqual(events, {'disco_items'},
                "Disco items event was not triggered: %s" % events)
        self.assertEqual(results, items,
                "Unexpected items: %s" % results)

    def testGetItemsIterators(self):
        """Test interaction between XEP-0030 and XEP-0059 plugins."""
        iteration_finished = []
        jids_found = set()

        self.stream_start(mode='client',
                          plugins=['xep_0030', 'xep_0059'])

        async def run_test():
            iterator = await self.xmpp['xep_0030'].get_items(
                jid='foo@localhost',
                node='bar',
                iterator=True
            )
            iterator.amount = 10
            async for page in iterator:
                for item in page['disco_items']['items']:
                    jids_found.add(item[0])
            iteration_finished.append(True)

        test_run = self.xmpp.wrap(run_test())
        self.wait_()
        self.send("""
          <iq id="2" type="get" to="foo@localhost">
            <query xmlns="http://jabber.org/protocol/disco#items"
                   node="bar">
              <set xmlns="http://jabber.org/protocol/rsm">
                <max>10</max>
              </set>
            </query>
          </iq>
        """)
        self.recv("""
          <iq id="2" type="result" to="tester@localhost">
            <query xmlns="http://jabber.org/protocol/disco#items">
              <item jid="a@b" node="1"/>
              <item jid="b@b" node="2"/>
              <item jid="c@b" node="3"/>
              <item jid="d@b" node="4"/>
              <item jid="e@b" node="5"/>
              <set xmlns="http://jabber.org/protocol/rsm">
                <first index='0'>a@b</first>
                <last>e@b</last>
                <count>10</count>
              </set>
            </query>
          </iq>
        """)
        self.wait_()
        self.send("""
          <iq id="3" type="get" to="foo@localhost">
            <query xmlns="http://jabber.org/protocol/disco#items"
                   node="bar">
              <set xmlns="http://jabber.org/protocol/rsm">
                <max>10</max>
                <after>e@b</after>
              </set>
            </query>
          </iq>
        """)
        self.recv("""
          <iq id="3" type="result" to="tester@localhost">
            <query xmlns="http://jabber.org/protocol/disco#items">
              <item jid="f@b" node="6"/>
              <item jid="g@b" node="7"/>
              <item jid="h@b" node="8"/>
              <item jid="i@b" node="9"/>
              <item jid="j@b" node="10"/>
              <set xmlns="http://jabber.org/protocol/rsm">
                <first index='5'>f@b</first>
                <last>j@b</last>
                <count>10</count>
              </set>
            </query>
          </iq>
        """)
        expected_jids = {'%s@b' % i for i in 'abcdefghij'}
        self.run_coro(test_run)
        self.assertEqual(expected_jids, jids_found)
        self.assertEqual(iteration_finished, [True])


suite = unittest.TestLoader().loadTestsFromTestCase(TestStreamDisco)
