import unittest
from slixmpp.test.integration import SlixIntegration


class TestMarkers(SlixIntegration):
    async def asyncSetUp(self):
        self.add_client(
            self.envjid('CI_ACCOUNT1'),
            self.envstr('CI_ACCOUNT1_PASSWORD'),
        )
        self.add_client(
            self.envjid('CI_ACCOUNT2'),
            self.envstr('CI_ACCOUNT2_PASSWORD'),
        )
        self.register_plugins(['xep_0333'])
        await self.connect_clients()

    async def test_send_marker(self):
        """Send and receive a chat marker"""
        self.clients[0]['xep_0333'].send_marker(
            self.clients[1].boundjid.full,
            'toto',
            'displayed',
        )
        msg = await self.clients[1].wait_until('marker_displayed')

suite = unittest.TestLoader().loadTestsFromTestCase(TestMarkers)
