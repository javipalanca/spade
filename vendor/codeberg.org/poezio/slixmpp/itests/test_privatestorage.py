import unittest
from slixmpp import ET
from slixmpp.test.integration import SlixIntegration
from slixmpp.plugins.xep_0048.stanza import Bookmarks


class TestPrivateStorage(SlixIntegration):
    async def asyncSetUp(self):
        self.add_client(
            self.envjid('CI_ACCOUNT1'),
            self.envstr('CI_ACCOUNT1_PASSWORD'),
        )
        self.register_plugins(['xep_0048', 'xep_0049'])
        await self.connect_clients()

    async def test_privatestorage(self):
        """Check we can set, get, and delete private in xml storage"""
        # Set a bookmark using private storage
        el = Bookmarks()
        el.add_conference('test@example.com', 'toto')
        await self.clients[0]['xep_0049'].store(
            el,
        )
        result = await self.clients[0]['xep_0049'].retrieve('bookmarks')

        self.assertEqual(result['private']['bookmarks'], el)

        # Purge bookmarks
        await self.clients[0]['xep_0049'].store(
            Bookmarks(),
        )
        result = await self.clients[0]['xep_0049'].retrieve('bookmarks')
        self.assertEqual(result['private']['bookmarks'], Bookmarks())


suite = unittest.TestLoader().loadTestsFromTestCase(TestPrivateStorage)
