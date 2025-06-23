import asyncio
import unittest
from slixmpp import JID
from slixmpp.test.integration import SlixIntegration


class TestUserAvatar(SlixIntegration):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.add_client(
            self.envjid('CI_ACCOUNT1'),
            self.envstr('CI_ACCOUNT1_PASSWORD'),
        )
        self.register_plugins(['xep_0084', 'xep_0115'])
        self.data = b'coucou coucou'
        await self.connect_clients()
        await asyncio.gather(
            self.clients[0]['xep_0115'].update_caps(),
        )

    async def _clear_avatar(self):
        """Utility for purging remote state"""
        await self.clients[0]['xep_0084'].stop()
        await self.clients[0]['xep_0084'].publish_avatar(b'')

    async def test_set_avatar(self):
        """Check we can set and get a PEP avatar and metadata"""
        await self._clear_avatar()

        await self.clients[0]['xep_0084'].publish_avatar(
            self.data
        )
        metadata = {
            'id': self.clients[0]['xep_0084'].generate_id(self.data),
            'bytes': 13,
            'type': 'image/jpeg',
        }
        # Wait for metadata publish event
        event = self.clients[0].wait_until('avatar_metadata_publish')
        publish = self.clients[0]['xep_0084'].publish_avatar_metadata(
            metadata,
        )
        res = await asyncio.gather(
            event,
            publish,
        )
        message = res[0]
        recv_meta = message['pubsub_event']['items']['item']['avatar_metadata']
        info = recv_meta['info']
        self.assertEqual(info['bytes'], metadata['bytes'])
        self.assertEqual(info['type'], metadata['type'])
        self.assertEqual(info['id'], metadata['id'])

        recv = await self.clients[0]['xep_0084'].retrieve_avatar(
            JID(self.clients[0].boundjid.bare),
            info['id']
        )
        avatar = recv['pubsub']['items']['item']['avatar_data']['value']
        self.assertEqual(avatar, self.data)

        await self._clear_avatar()


suite = unittest.TestLoader().loadTestsFromTestCase(TestUserAvatar)
