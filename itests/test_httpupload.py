try:
    import aiohttp
except ImportError:
    aiohttp = None
import unittest
from io import BytesIO
from slixmpp.test.integration import SlixIntegration


class TestHTTPUpload(SlixIntegration):
    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.add_client(
            self.envjid('CI_ACCOUNT1'),
            self.envstr('CI_ACCOUNT1_PASSWORD'),
        )
        self.register_plugins(['xep_0363'])
        # Minimal data, we do not want to clutter the remote server
        self.data = b'tototo'
        await self.connect_clients()


    @unittest.skipIf(aiohttp is None, "aiohttp is not installed")
    async def test_httpupload(self):
        """Check we can upload a file properly."""
        url = await self.clients[0]['xep_0363'].upload_file(
            'toto.txt',
            input_file=BytesIO(self.data),
            size=len(self.data),
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                text = await resp.text()
        self.assertEqual(text.encode('utf-8'), self.data)


suite = unittest.TestLoader().loadTestsFromTestCase(TestHTTPUpload)
