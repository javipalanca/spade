import unittest
from slixmpp.test.integration import SlixIntegration


class TestPing(SlixIntegration):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.add_client(
            self.envjid('CI_ACCOUNT1'),
            self.envstr('CI_ACCOUNT1_PASSWORD'),
        )
        self.register_plugins(['xep_0199'])
        await self.connect_clients()

    async def test_ping(self):
        """Check we can ping our own server"""
        rtt = await self.clients[0]['xep_0199'].ping()
        self.assertGreater(10, rtt)


suite = unittest.TestLoader().loadTestsFromTestCase(TestPing)
