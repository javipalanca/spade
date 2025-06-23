import unittest
from slixmpp.test import SlixTest
from slixmpp.util import (
    MemoryCache, MemoryPerJidCache,
    FileSystemCache, FileSystemPerJidCache
)
from tempfile import TemporaryDirectory

class TestCacheClass(SlixTest):

    def testMemoryCache(self):
        cache = MemoryCache()

        cache.store("test", "test_value")
        self.assertEqual(cache.retrieve("test"), "test_value")
        self.assertEqual(cache.retrieve("test2"), None)

        cache.remove("test")
        self.assertEqual(cache.retrieve("test"), None)

    def testMemoryPerJidcache(self):
        cache = MemoryPerJidCache()

        cache.store_by_jid("test@example.com", "test", "test_value")
        self.assertEqual(
            cache.retrieve_by_jid("test@example.com", "test"),
            "test_value"
        )

        cache.remove_by_jid("test@example.com", "test")
        self.assertEqual(
            cache.retrieve_by_jid("test@example.com", "test"),
            None
        )

    def testFileSystemCache(self):
        def failing_decode(value):
            if value == "failme":
                raise Exception("you failed")
            return value
        with TemporaryDirectory() as tmpdir:
            cache = FileSystemCache(tmpdir, "test", decode=failing_decode)
            cache.store("test", "test_value")
            cache.store("test2", "failme")
            self.assertEqual(
                cache.retrieve("test"),
                "test_value"
            )
            cache.remove("test")
            self.assertEqual(
                cache.retrieve("test"),
                None
            )

            self.assertEqual(
                cache.retrieve("test2"),
                None
            )

    def testFileSystemPerJidCache(self):
        with TemporaryDirectory() as tmpdir:
            cache = FileSystemPerJidCache(tmpdir, "test")
            cache.store_by_jid("test@example.com", "test", "test_value")
            self.assertEqual(
                cache.retrieve_by_jid("test@example.com", "test"),
                "test_value"
            )
            cache.remove_by_jid("test@example.com", "test")
            self.assertEqual(
                cache.retrieve_by_jid("test@example.com", "test"),
                None
            )

suite = unittest.TestLoader().loadTestsFromTestCase(TestCacheClass)
