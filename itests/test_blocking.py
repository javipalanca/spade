import unittest
from slixmpp import JID
from slixmpp.test.integration import SlixIntegration


class TestBlocking(SlixIntegration):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.add_client(
            self.envjid('CI_ACCOUNT1'),
            self.envstr('CI_ACCOUNT1_PASSWORD'),
        )
        self.register_plugins(['xep_0191'])
        await self.connect_clients()

    async def test_blocking(self):
        """Check we can block, unblock, and list blocked"""
        await self.clients[0]['xep_0191'].block(
            [JID('toto@example.com'), JID('titi@example.com')]
        )
        blocked = {JID('toto@example.com'), JID('titi@example.com')}
        iq = await self.clients[0]['xep_0191'].get_blocked()
        self.assertEqual(iq['blocklist']['items'], blocked)

        info = await self.clients[0]['xep_0191'].unblock(
            blocked,
        )
        iq = await self.clients[0]['xep_0191'].get_blocked()
        self.assertEqual(len(iq['blocklist']['items']), 0)


suite = unittest.TestLoader().loadTestsFromTestCase(TestBlocking)
