import unittest
from random import randint
from slixmpp import JID
from slixmpp.test.integration import SlixIntegration


class TestMAM(SlixIntegration):
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
        self.register_plugins(['xep_0313'])
        await self.connect_clients()

    async def test_mam_retrieve(self):
        """Make sure we can get messages from our archive"""
        # send messages first
        tok = randint(1, 999999)
        self.clients[0].make_message(
            mto=self.clients[1].boundjid,
            mbody=f'coucou {tok}'
        ).send()
        await self.clients[1].wait_until('message')
        self.clients[1].make_message(
            mto=self.clients[0].boundjid,
            mbody=f'coucou coucou {tok}',
        ).send()
        await self.clients[0].wait_until('message')

        # Get archive
        retrieve = self.clients[0]['xep_0313'].retrieve(
            with_jid=JID(self.envjid('CI_ACCOUNT2')),
            iterator=True,
            reverse=True,
            rsm={'max': 2}
        )
        msgs = []
        count = 0
        async for rsm in retrieve:
            for msg in rsm['mam']['results']:
                msgs.append(
                    msg['mam_result']['forwarded']['stanza']
                )
                count += 1
            if count >= 2:
                break

        self.assertEqual(msgs[0]['body'], f'coucou {tok}')
        self.assertEqual(msgs[1]['body'], f'coucou coucou {tok}')

    async def test_mam_iterate(self):
        """Make sure we can iterate over messages from our archive"""
        # send messages first
        tok = randint(1, 999999)
        self.clients[0].make_message(
            mto=self.clients[1].boundjid,
            mbody=f'coucou {tok}'
        ).send()
        await self.clients[1].wait_until('message')
        self.clients[1].make_message(
            mto=self.clients[0].boundjid,
            mbody='coucou coucou %s' % tok,
        ).send()
        await self.clients[0].wait_until('message')

        # Get archive
        retrieve = self.clients[0]['xep_0313'].iterate(
            with_jid=JID(self.envjid('CI_ACCOUNT2')),
            reverse=True,
            rsm={'max': 1}
        )
        msgs = []
        count = 0
        async for msg in retrieve:
            msgs.append(
                msg['mam_result']['forwarded']['stanza']
            )
            count += 1
            if count >= 2:
                break

        self.assertEqual(msgs[0]['body'], f'coucou coucou {tok}')
        self.assertEqual(msgs[1]['body'], f'coucou {tok}')


suite = unittest.TestLoader().loadTestsFromTestCase(TestMAM)
