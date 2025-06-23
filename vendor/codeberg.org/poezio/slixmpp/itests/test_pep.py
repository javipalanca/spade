import asyncio
import unittest
from uuid import uuid4
from slixmpp.exceptions import IqError
from slixmpp.test.integration import SlixIntegration
from slixmpp.xmlstream import ElementBase, register_stanza_plugin
from slixmpp.plugins.xep_0060.stanza import Item

class Mystanza(ElementBase):
    namespace = 'random-ns'
    name = 'mystanza'
    plugin_attrib = 'mystanza'
    interfaces = {'test'}

register_stanza_plugin(Item, Mystanza)

class TestPEP(SlixIntegration):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.add_client(
            self.envjid('CI_ACCOUNT1'),
            self.envstr('CI_ACCOUNT1_PASSWORD'),
        )
        self.add_client(
            self.envjid('CI_ACCOUNT2'),
            self.envstr('CI_ACCOUNT2_PASSWORD'),
        )
        self.register_plugins(['xep_0222', 'xep_0223'])
        for client in self.clients:
            client.auto_authorize = True
        await self.connect_clients()

    async def test_pep_public(self):
        """Check we can get and set public PEP data"""
        stanza = Mystanza()
        stanza['test'] = str(uuid4().hex)
        try:
            await self.clients[0]['xep_0060'].delete_node(
                self.clients[0].boundjid.bare,
                node=stanza.namespace,
            )
        except:
            pass
        await self.clients[0]['xep_0222'].store(stanza, node=stanza.namespace, id='toto')
        fetched = await self.clients[0]['xep_0222'].retrieve(
            stanza.namespace,
        )
        fetched_stanza = fetched['pubsub']['items']['item']['mystanza']
        self.assertEqual(fetched_stanza['test'], stanza['test'])

    async def test_pep_private(self):
        """Check we can get and set private PEP data"""
        stanza = Mystanza()
        stanza['test'] = str(uuid4().hex)
        await self.clients[0]['xep_0223'].store(
            stanza, node='private-random', id='toto'
        )
        fetched = await self.clients[0]['xep_0223'].retrieve(
            'private-random',
        )
        fetched_stanza = fetched['pubsub']['items']['item']['mystanza']
        self.assertEqual(fetched_stanza['test'], stanza['test'])

        with self.assertRaises(IqError):
            fetched = await self.clients[1]['xep_0060'].get_item(
                jid=self.clients[0].boundjid.bare,
                node='private-random',
                item_id='toto',
            )

suite = unittest.TestLoader().loadTestsFromTestCase(TestPEP)
