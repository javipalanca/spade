import asyncio
import unittest
from slixmpp.test.integration import SlixIntegration


class TestBOB(SlixIntegration):
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
        self.register_plugins(['xep_0231'])
        self.data = b'to' * 257
        await self.connect_clients()

    async def test_bob(self):
        """Check we can send and receive a BOB."""
        cid = await self.clients[0]['xep_0231'].set_bob(
            self.data,
            'image/jpeg',
        )
        recv = await self.clients[1]['xep_0231'].get_bob(
            jid=self.clients[0].boundjid,
            cid=cid,
        )

        self.assertEqual(self.data, recv['bob']['data'])


suite = unittest.TestLoader().loadTestsFromTestCase(TestBOB)
