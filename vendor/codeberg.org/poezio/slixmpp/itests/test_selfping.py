import asyncio
import unittest
from uuid import uuid4
from slixmpp import JID
from slixmpp.test.integration import SlixIntegration
from slixmpp.plugins.xep_0410 import PingStatus

UNIQUE = uuid4().hex


class TestSelfPing(SlixIntegration):

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
        self.register_plugins(['xep_0410'], [{'ping_interval': 2}])
        await self.connect_clients()

    async def config_room(self):
        self.clients[0]['xep_0045'].join_muc(self.muc, 'client1')
        presence = await self.clients[0].wait_until('muc::%s::got_online' % self.muc)
        config = await self.clients[0]['xep_0045'].get_room_config(self.muc)
        values = config.get_values()
        values['muc#roomconfig_persistentroom'] = False
        values['muc#roomconfig_membersonly'] = True
        config['values'] = values
        config.reply()
        config = await self.clients[0]['xep_0045'].set_room_config(self.muc, config)
        await self.clients[0]['xep_0045'].send_affiliation_list(
            self.muc,
            [
                (self.clients[1].boundjid.bare, 'member'),
            ],
        )

    async def test_presence_monitor(self):
        """Check that the ping status gets updated on room changes"""
        await self.config_room()
        self.clients[1]['xep_0045'].join_muc(self.muc, 'client2')
        full = JID(self.muc)
        full.resource = 'client2'
        self.clients[1]['xep_0410'].enable_self_ping(full)
        await self.clients[1].wait_until('muc::%s::got_online' % self.muc)
        await asyncio.sleep(3)
        self.assertEqual(
            self.clients[1]['xep_0410'].get_ping_status(full),
            PingStatus.JOINED,
        )
        t = asyncio.create_task
        _, pending = await asyncio.wait(
            [
                t(self.clients[0]['xep_0045'].set_role(self.muc, 'client2', 'none')),
                t(self.clients[0].wait_until('muc::%s::got_offline' % self.muc)),
                t(self.clients[1].wait_until('muc_ping_changed')),
            ],
            timeout=10,
        )
        self.assertEqual(pending, set())
        self.assertEqual(
            self.clients[1]['xep_0410'].get_ping_status(full),
            PingStatus.DISCONNECTED,
        )
        self.clients[1]['xep_0045'].join_muc(self.muc, 'client2')
        await asyncio.wait(
            [
                t(self.clients[1].wait_until('muc::%s::got_online' % self.muc)),
                t(self.clients[1].wait_until('muc_ping_changed')),
                t(asyncio.sleep(3))],
            timeout=10,
        )
        self.assertEqual(
            self.clients[1]['xep_0410'].get_ping_status(full),
            PingStatus.JOINED,
        )


suite = unittest.TestLoader().loadTestsFromTestCase(TestSelfPing)
