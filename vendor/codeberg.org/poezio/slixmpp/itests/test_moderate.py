import asyncio
import unittest
import uuid
from slixmpp import JID
from slixmpp.test.integration import SlixIntegration

UNIQUE = uuid.uuid4().hex


class TestModerate(SlixIntegration):
    async def asyncSetUp(self):
        self.mucserver = self.envjid('CI_MUC_SERVER')
        self.muc = JID('%s@%s' % (UNIQUE, self.mucserver))
        self.add_client(
            self.envjid('CI_ACCOUNT1'),
            self.envstr('CI_ACCOUNT1_PASSWORD'),
        )
        self.add_client(
            self.envjid('CI_ACCOUNT2'),
            self.envstr('CI_ACCOUNT2_PASSWORD'),
        )
        self.register_plugins(['xep_0425', 'xep_0359', 'xep_0045'])
        await self.connect_clients()

    async def setup_muc(self):
        self.clients[0]['xep_0045'].join_muc(self.muc, 'client1')
        presence = await self.clients[0].wait_until('muc::%s::got_online' % self.muc)
        self.assertEqual(presence['muc']['affiliation'], 'owner')
        # Send initial configuration
        config = await self.clients[0]['xep_0045'].get_room_config(self.muc)
        values = config.get_values()
        values['muc#roomconfig_persistentroom'] = False
        values['muc#roomconfig_membersonly'] = True
        config['values'] = values
        config.reply()
        config = await self.clients[0]['xep_0045'].set_room_config(self.muc, config)

        # Send affiliation list including client 2
        await self.clients[0]['xep_0045'].send_affiliation_list(
            self.muc,
            [
                (self.clients[1].boundjid.bare, 'member'),
            ],
        )
        self.clients[1]['xep_0045'].join_muc(self.muc, 'client2')
        await self.clients[1].wait_until('muc::%s::got_online' % self.muc)

    async def test_moderate_msg(self):
        """Try to moderate a message"""
        await self.setup_muc()
        msg = self.clients[1].make_message(
            mto=self.muc, mtype='groupchat', mbody='Coucou'
        )
        msg.send()
        msg_recv = await self.clients[0].wait_until('groupchat_message')
        iqres, new_msg = await asyncio.gather(
            self.clients[0]['xep_0425'].moderate(
                self.muc,
                id=msg_recv['stanza_id']['id'],
                reason='Your message is bad.',
            ),
            self.clients[1].wait_until('moderated_message')
        )
        self.assertTrue(new_msg['apply_to']['id'], msg_recv['id'])

suite = unittest.TestLoader().loadTestsFromTestCase(TestModerate)
