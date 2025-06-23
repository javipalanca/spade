import unittest

from slixmpp.test import SlixTest
from slixmpp.plugins.xep_0446 import stanza


class TestFileMeta(SlixTest):
    def setUp(self):
        stanza.register_plugins()

    def test_simple(self):
        file = stanza.File()
        file["desc"] = "a description"
        file["name"] = "toto.jpg"
        file["media-type"] = "image/jpeg"
        file["height"] = 1024
        file["width"] = 768
        file["size"] = 2048
        self.check(
            file,
            """
            <file xmlns='urn:xmpp:file:metadata:0'>
              <desc>a description</desc>
              <name>toto.jpg</name>
              <media-type>image/jpeg</media-type>
              <height>1024</height>
              <width>768</width>
              <size>2048</size>
            </file>
            """,
        )

    def test_bad_value(self):
        file = stanza.File()
        file["desc"] = "My great video"
        file["name"] = "toto.mp4"
        file["media-type"] = "video/3gpp"
        file["height"] = 1024
        file["width"] = 768
        with self.assertRaises(ValueError):
            file["length"] = -100

    def test_hash_element(self):
        file = stanza.File()
        file["desc"] = "My great video"
        file["name"] = "toto.3gp"
        file["media-type"] = "video/3gpp"
        file["height"] = 1024
        file["width"] = 768
        file["length"] = 2000
        file["hash"]["algo"] = "sha3-256"
        file["hash"]["value"] = "abcdef="
        self.check(
            file,
            """
            <file xmlns='urn:xmpp:file:metadata:0'>
              <desc>My great video</desc>
              <name>toto.3gp</name>
              <media-type>video/3gpp</media-type>
              <height>1024</height>
              <width>768</width>
              <length>2000</length>
              <hash xmlns='urn:xmpp:hashes:2' algo="sha3-256">abcdef=</hash>
            </file>
            """,
        )

    def test_thumbnail_element(self):
        file = stanza.File()
        file["desc"] = "a description"
        file["name"] = "toto.jpg"
        file["media-type"] = "image/jpeg"
        file["height"] = 1024
        file["width"] = 768
        file["size"] = 2048
        file["thumbnail"]["media-type"] = "image/png"
        file["thumbnail"]["uri"] = "cid:sha1+deadbeef@bob.xmpp.org"
        file["thumbnail"]["width"] = 128
        file["thumbnail"]["height"] = 96
        self.check(
            file,
            """
            <file xmlns='urn:xmpp:file:metadata:0'>
              <desc>a description</desc>
              <name>toto.jpg</name>
              <media-type>image/jpeg</media-type>
              <height>1024</height>
              <width>768</width>
              <size>2048</size>
              <thumbnail xmlns='urn:xmpp:thumbs:1'
                 uri='cid:sha1+deadbeef@bob.xmpp.org'
                 media-type='image/png'
                 width='128'
                 height='96'/>
            </file>
            """,
        )



suite = unittest.TestLoader().loadTestsFromTestCase(TestFileMeta)
