import unittest
from base64 import b64encode
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from hashlib import sha256

from slixmpp.plugins.xep_0082 import format_datetime
from slixmpp.test import SlixTest

class TestSIMS(SlixTest):
    def setUp(self):
        self.stream_start(
            mode="component", jid="whatevs.shakespeare.lit", plugins={"xep_0385"}
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
            sims = self.xmpp["xep_0385"].get_sims(
                Path(f.name),
                ["https://xxx.com"],
                media_type="MEDIA",
                desc="DESCRIPTION",
            )

            self.check(
                sims,
                f"""
                <reference xmlns='urn:xmpp:reference:0' type='data'>
                <media-sharing xmlns='urn:xmpp:sims:1'>
                  <file xmlns='urn:xmpp:jingle:apps:file-transfer:5'>
                    <media-type>MEDIA</media-type>
                    <name>{Path(f.name).name}</name>
                    <size>{size}</size>
                    <hash xmlns='urn:xmpp:hashes:2' algo='sha-256'>{h}</hash>
                    <desc>DESCRIPTION</desc>
                    <date>{format_datetime(datetime.fromtimestamp(Path(f.name).stat().st_mtime))}</date>
                  </file>
                  <sources>
                    <reference xmlns='urn:xmpp:reference:0' type='data' uri='https://xxx.com' />
                  </sources>
                </media-sharing>
                </reference>
                """,
                use_values=False,
            )


suite = unittest.TestLoader().loadTestsFromTestCase(TestSIMS)
