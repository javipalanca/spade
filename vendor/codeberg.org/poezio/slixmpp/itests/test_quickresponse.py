import unittest
from slixmpp.test.integration import SlixIntegration
from slixmpp.plugins.xep_0439 import stanza


class TestQuickResponse(SlixIntegration):
    async def asyncSetUp(self):
        self.add_client(
            self.envjid('CI_ACCOUNT1'),
            self.envstr('CI_ACCOUNT1_PASSWORD'),
        )
        self.add_client(
            self.envjid('CI_ACCOUNT2'),
            self.envstr('CI_ACCOUNT2_PASSWORD'),
        )
        self.register_plugins(['xep_0439'])
        await self.connect_clients()

    async def test_quickresponse(self):
        """Send and receive actions and responses"""
        actions = [
            ('id1', 'Action 1'),
            ('id2', 'Action 2'),
        ]
        self.clients[0]['xep_0439'].ask_for_actions(
            self.clients[1].boundjid.full,
            "Action 1 or 2 ?",
            actions
        )
        msg = await self.clients[1].wait_until('action_received')
        actions_recv = [
            (st['id'], st['label']) for st in msg if isinstance(st, stanza.Action)
        ]
        self.assertEqual(
                actions,
                actions_recv,
        )

        reply = self.clients[1].make_message(
            mto=self.clients[0].boundjid.full
        )
        reply['action_selected']['id'] = 'id1'
        reply.send()

        reply_recv = await self.clients[0].wait_until('action_selected')
        self.assertEqual(
            reply_recv['action_selected']['id'],
            'id1',
        )

        self.clients[0]['xep_0439'].ask_for_response(
            self.clients[1].boundjid.full,
            "Reply with action 1 or 2 (id1/id2) ?",
            actions
        )
        msg = await self.clients[1].wait_until('responses_received')


suite = unittest.TestLoader().loadTestsFromTestCase(TestQuickResponse)
