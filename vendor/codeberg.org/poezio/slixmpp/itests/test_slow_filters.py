import asyncio
import unittest
from slixmpp.test.integration import SlixIntegration
from slixmpp import Message


class TestSlowFilter(SlixIntegration):
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

    async def test_filters(self):
        """Make sure filters work"""
        def add_a(stanza):
            if isinstance(stanza, Message):
                stanza['body'] = stanza['body'] + ' a'
            return stanza

        async def add_b(stanza):
            if isinstance(stanza, Message):
                stanza['body'] = stanza['body'] + ' b'
            return stanza

        async def add_c_wait(stanza):
            if isinstance(stanza, Message):
                await asyncio.sleep(2)
                stanza['body'] = stanza['body'] + ' c'
            return stanza
        self.clients[0].add_filter('out', add_a)
        self.clients[0].add_filter('out', add_b)
        self.clients[0].add_filter('out', add_c_wait)
        body = 'Msg body'
        msg = self.clients[0].make_message(
            mto=self.clients[1].boundjid, mbody=body,
        )
        msg.send()
        message = await self.clients[1].wait_until('message')
        self.assertEqual(message['body'], body + ' a b c')


suite = unittest.TestLoader().loadTestsFromTestCase(TestSlowFilter)
