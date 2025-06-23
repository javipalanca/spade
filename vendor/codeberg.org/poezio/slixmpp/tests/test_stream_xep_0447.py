import unittest
from datetime import datetime
from base64 import b64encode
from pathlib import Path
from tempfile import NamedTemporaryFile
from hashlib import sha256

from slixmpp.test import SlixTest
from slixmpp.plugins.xep_0082 import format_datetime


class TestStatelessFileSharing(SlixTest):
    def setUp(self):
        self.stream_start(
            mode="component", jid="whatevs.shakespeare.lit", plugins={"xep_0447"}
        )


    def test_set_file(self):
        with NamedTemporaryFile("wb+") as f:
            n = 10
            size = 0
            for i in range(n):
                size += len(bytes(i))
                f.write(bytes(i))

            f.seek(0)
            h = b64encode(sha256(f.read()).digest()).decode()
            sfs = self.xmpp["xep_0447"].get_sfs(
                Path(f.name),
                ["https://xxx.com"],
                media_type="MEDIA",
                desc="DESCRIPTION",
            )

            self.check(
                sfs,
                f"""
                  <file-sharing xmlns='urn:xmpp:sfs:0' disposition='inline'>
                    <file xmlns='urn:xmpp:file:metadata:0'>
                      <media-type>MEDIA</media-type>
                      <name>{Path(f.name).name}</name>
                      <size>{size}</size>
                      <hash xmlns='urn:xmpp:hashes:2' algo='sha-256'>{h}</hash>
                      <desc>DESCRIPTION</desc>
                      <date>{format_datetime(datetime.fromtimestamp(Path(f.name).stat().st_mtime))}</date>
                    </file>
                    <sources>
                      <url-data xmlns='http://jabber.org/protocol/url-data'
                                target='https://xxx.com' />
                    </sources>
                  </file-sharing>
                """,
                use_values=False,
            )

suite = unittest.TestLoader().loadTestsFromTestCase(TestStatelessFileSharing)
