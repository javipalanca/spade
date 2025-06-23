import asyncio
import unittest
from slixmpp.test.integration import SlixIntegration


class TestIBB(SlixIntegration):
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
        config = {'block_size': 256, 'auto_accept': True}
        self.register_plugins(['xep_0047'], [config])
        self.data = b'to' * 257
        await self.connect_clients()

    async def test_ibb(self):
        """Check we can send and receive data through ibb"""
        coro_in = self.clients[1].wait_until('ibb_stream_start')
        coro_out = self.clients[0]['xep_0047'].open_stream(
            self.clients[1].boundjid,
            sid='toto'
        )
        instream, outstream = await asyncio.gather(coro_in, coro_out)

        async def send_and_close():
            await outstream.sendall(self.data)
            await outstream.close()

        in_data, _ = await asyncio.gather(instream.gather(), send_and_close())

        self.assertEqual(self.data, in_data)


suite = unittest.TestLoader().loadTestsFromTestCase(TestIBB)
