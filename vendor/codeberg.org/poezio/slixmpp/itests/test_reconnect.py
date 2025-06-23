import unittest
from slixmpp.test.integration import SlixIntegration


class TestReconnect(SlixIntegration):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.add_client(
            self.envjid('CI_ACCOUNT1'),
            self.envstr('CI_ACCOUNT1_PASSWORD'),
        )
        await self.connect_clients()

    async def test_disconnect_connect(self):
        """Check we can disconnect and connect again"""
        await self.clients[0].disconnect()
        self.clients[0].connect()
        await self.clients[0].wait_until('session_start')

    async def test_reconnect(self):
        """Check we can reconnect()"""
        self.clients[0].reconnect()
        await self.clients[0].wait_until("session_start")

suite = unittest.TestLoader().loadTestsFromTestCase(TestReconnect)
