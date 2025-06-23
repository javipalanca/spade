import asyncio
import unittest
from uuid import uuid4
from slixmpp import JID
from slixmpp.test.integration import SlixIntegration

UNIQUE = uuid4().hex


class TestMUC(SlixIntegration):

    async def asyncSetUp(self):
        self.mucserver = self.envjid('CI_MUC_SERVER', default='chat.jabberfr.org')
        self.muc = JID('%s@%s' % (UNIQUE, self.mucserver))
        self.add_client(
            self.envjid('CI_ACCOUNT1'),
            self.envstr('CI_ACCOUNT1_PASSWORD'),
        )
        self.add_client(
            self.envjid('CI_ACCOUNT2'),
            self.envstr('CI_ACCOUNT2_PASSWORD'),
        )
        self.register_plugins(['xep_0045'])
        await self.connect_clients()

    async def test_initial_join(self):
        """Check that we can connect to a new muc"""
        self.clients[0]['xep_0045'].join_muc(self.muc, 'client1')
        presence = await self.clients[0].wait_until('muc::%s::got_online' % self.muc)
        self.assertEqual(presence['muc']['affiliation'], 'owner')

    async def test_setup_muc(self):
        """Check that sending the initial room config and affiliation list works"""
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

    async def test_join_after_config(self):
        """Join a room after being added to the affiliation list"""
        await self.test_setup_muc()
        self.clients[1]['xep_0045'].join_muc(self.muc, 'client2')
        await self.clients[1].wait_until('muc::%s::got_online' % self.muc)

    async def test_nick_change_leave(self):
        """Check that we change nicks and leave properly"""
        await self.test_join_after_config()
        nick = 'coucoucou2'
        new_nick = await self.clients[0]['xep_0045'].set_self_nick(self.muc, nick)
        assert new_nick == nick
        self.clients[0]['xep_0045'].leave_muc(self.muc, 'client1', 'boooring')
        pres = await self.clients[1].wait_until('muc::%s::got_offline' % self.muc)
        self.assertEqual(pres['status'], 'boooring')
        self.assertEqual(pres['type'], 'unavailable')

    async def test_kick(self):
        """Test kicking a user"""
        await self.test_join_after_config()
        await asyncio.gather(
            self.clients[0].wait_until('muc::%s::got_offline' % self.muc),
            self.clients[0]['xep_0045'].set_role(self.muc, 'client2', 'none')
        )


suite = unittest.TestLoader().loadTestsFromTestCase(TestMUC)
