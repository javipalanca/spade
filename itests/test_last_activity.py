import unittest
from slixmpp.test.integration import SlixIntegration


class TestLastActivity(SlixIntegration):
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
        self.register_plugins(['xep_0012'])
        await self.connect_clients()

    async def test_activity(self):
        """Check we can set and get last activity"""
        await self.clients[0]['xep_0012'].set_last_activity(
            status='coucou',
            seconds=4242,
        )
        act = await self.clients[1]['xep_0012'].get_last_activity(
            self.clients[0].boundjid.full
        )
        self.assertEqual(act['last_activity']['status'], 'coucou')
        self.assertGreater(act['last_activity']['seconds'], 4241)
        self.assertGreater(4250, act['last_activity']['seconds'])


suite = unittest.TestLoader().loadTestsFromTestCase(TestLastActivity)
