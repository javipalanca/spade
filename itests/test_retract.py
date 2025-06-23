import unittest
from slixmpp.test.integration import SlixIntegration


class TestRetract(SlixIntegration):
    async def asyncSetUp(self):
        self.add_client(
            self.envjid('CI_ACCOUNT1'),
            self.envstr('CI_ACCOUNT1_PASSWORD'),
        )
        self.add_client(
            self.envjid('CI_ACCOUNT2'),
            self.envstr('CI_ACCOUNT2_PASSWORD'),
        )
        self.register_plugins(['xep_0424'])
        await self.connect_clients()

    async def test_retract_msg(self):
        """Try to retract a message"""
        self.clients[0]['xep_0424'].send_retraction(
            self.clients[1].boundjid.full,
            id='toto',
            fallback_text='Twas a mistake',
        )
        msg = await self.clients[1].wait_until('message_retract')
        self.assertEqual(msg['retract']['id'], 'toto')

suite = unittest.TestLoader().loadTestsFromTestCase(TestRetract)
