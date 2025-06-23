import unittest
from slixmpp.test.integration import SlixIntegration


class TestConnect(SlixIntegration):
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
        await self.connect_clients()

    async def test_send_message(self):
        """Make sure we can send and receive messages"""
        msg = self.clients[0].make_message(
            mto=self.clients[1].boundjid, mbody='Msg body',
        )
        msg.send()
        message = await self.clients[1].wait_until('message')
        self.assertEqual(message['body'], msg['body'])


suite = unittest.TestLoader().loadTestsFromTestCase(TestConnect)
