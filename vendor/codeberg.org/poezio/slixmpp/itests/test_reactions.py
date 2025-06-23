import unittest
from slixmpp.test.integration import SlixIntegration


class TestReactions(SlixIntegration):
    async def asyncSetUp(self):
        self.add_client(
            self.envjid('CI_ACCOUNT1'),
            self.envstr('CI_ACCOUNT1_PASSWORD'),
        )
        self.add_client(
            self.envjid('CI_ACCOUNT2'),
            self.envstr('CI_ACCOUNT2_PASSWORD'),
        )
        self.register_plugins(['xep_0444'])
        await self.connect_clients()

    async def test_send_reaction(self):
        """Make sure we can send and receive reactions"""
        self.clients[0]['xep_0444'].send_reactions(
            self.clients[1].boundjid.full,
            to_id='toto',
            reactions=['🦙', '🦦'],
        )
        msg = await self.clients[1].wait_until('reactions')
        self.assertEqual(
            msg['reactions'].get_values(),
            {'🦙', '🦦'},
        )
        self.assertEqual(msg['reactions']['id'], 'toto')

suite = unittest.TestLoader().loadTestsFromTestCase(TestReactions)
