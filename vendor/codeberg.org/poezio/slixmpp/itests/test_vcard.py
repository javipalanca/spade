import unittest
from slixmpp.test.integration import SlixIntegration


class TestVcardTemp(SlixIntegration):
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
        self.register_plugins(['xep_0054'])
        await self.connect_clients()

    async def _clear_vcard(self):
        # cleanup
        await self.clients[0]['xep_0054'].publish_vcard(
            self.clients[0]['xep_0054'].make_vcard()
        )

    async def test_vcard(self):
        """Check we can set and get a vcard"""
        await self._clear_vcard()

        # Check that vcard is empty
        recv = await self.clients[1]['xep_0054'].get_vcard(
            self.clients[0].boundjid.bare
        )
        self.assertEqual(recv['vcard_temp']['TITLE'], None)

        vcard = self.clients[0]['xep_0054'].make_vcard()
        vcard['TITLE'] = 'Coucou coucou'
        await self.clients[0]['xep_0054'].publish_vcard(
            vcard,
        )
        #
        recv = await self.clients[1]['xep_0054'].get_vcard(
            self.clients[0].boundjid.bare
        )
        self.assertEqual(recv['vcard_temp']['TITLE'], 'Coucou coucou')

        await self._clear_vcard()


suite = unittest.TestLoader().loadTestsFromTestCase(TestVcardTemp)
