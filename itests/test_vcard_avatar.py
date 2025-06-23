import asyncio
import unittest
from slixmpp import JID
from slixmpp.test.integration import SlixIntegration
from hashlib import sha1


class TestVcardAvatar(SlixIntegration):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.add_client(
            self.envjid('CI_ACCOUNT1'),
            self.envstr('CI_ACCOUNT1_PASSWORD'),
        )
        self.register_plugins(['xep_0153'])
        self.data = b'coucou coucou'
        self.hashed_data = sha1(self.data).hexdigest()
        await self.connect_clients()

    async def _clear_avatar(self):
        """Utility for purging remote state"""
        await self.clients[0]['xep_0153'].set_avatar(avatar=b'')

    async def test_set_avatar(self):
        """Check we can set and get a PEP avatar and metadata"""
        await self._clear_avatar()

        event = self.clients[0].wait_until('vcard_avatar_update')
        update = self.clients[0]['xep_0153'].set_avatar(
            avatar=self.data
        )
        result = await asyncio.gather(
            event,
            update,
        )
        presence = result[0]
        hash = presence['vcard_temp_update']['photo']
        self.assertEqual(hash, self.hashed_data)

        iq = await self.clients[0]['xep_0054'].get_vcard(
            JID(self.clients[0].boundjid.bare)
        )
        photo = iq['vcard_temp']['PHOTO']['BINVAL']
        self.assertEqual(photo, self.data)

        await self._clear_avatar()


suite = unittest.TestLoader().loadTestsFromTestCase(TestVcardAvatar)
