import unittest
from slixmpp.test.integration import SlixIntegration


class TestVersion(SlixIntegration):
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
        self.register_plugins(
            ['xep_0092'],
            configs=[{
                'software_name': 'Slix Test',
                'version': '1.2.3.4',
                'os': 'I use arch btw',
            }]
        )
        await self.connect_clients()

    async def test_version(self):
        """Check we can set and query software version info"""
        iq = await self.clients[1]['xep_0092'].get_version(
            self.clients[0].boundjid.full
        )
        version = iq['software_version']
        self.assertEqual(version['name'], 'Slix Test')
        self.assertEqual(version['version'], '1.2.3.4')
        self.assertEqual(version['os'], 'I use arch btw')


suite = unittest.TestLoader().loadTestsFromTestCase(TestVersion)
