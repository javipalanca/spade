# Slixmpp: The Slick XMPP Library
# Copyright (C) 2017 Emmanuel Gil Peyrot
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from base64 import b64encode
import hashlib
import logging

from slixmpp.plugins import BasePlugin
from slixmpp.plugins.xep_0300 import stanza, Hash


log = logging.getLogger(__name__)


class XEP_0300(BasePlugin):
    """
    XEP-0300: Use of Cryptographic Hash Functions in XMPP
    """

    name = 'xep_0300'
    description = 'XEP-0300: Use of Cryptographic Hash Functions in XMPP'
    dependencies = {'xep_0030'}
    stanza = stanza
    default_config = {
        'block_size': 1024 * 1024,  # One MiB
        'preferred': 'sha-256',
        'enable_sha-1': False,
        'enable_sha-256': True,
        'enable_sha-512': True,
        'enable_sha3-256': True,
        'enable_sha3-512': True,
        'enable_BLAKE2b256': True,
        'enable_BLAKE2b512': True,
    }

    _hashlib_function = {
        'sha-1': hashlib.sha1,
        'sha-256': hashlib.sha256,
        'sha-512': hashlib.sha512,
        'sha3-256': hashlib.sha3_256,
        'sha3-512': hashlib.sha3_512,
        'BLAKE2b256': lambda: hashlib.blake2b(digest_size=32),
        'BLAKE2b512': lambda: hashlib.blake2b(digest_size=64),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enabled_hashes = []

    def plugin_init(self):
        namespace = 'urn:xmpp:hash-function-text-names:%s'
        self.enabled_hashes.clear()
        for algo in self._hashlib_function:
            if getattr(self, 'enable_' + algo, False):
                self.enabled_hashes.append(namespace % algo)

    def session_bind(self, jid):
        self.xmpp['xep_0030'].add_feature(Hash.namespace)

        for namespace in self.enabled_hashes:
            self.xmpp['xep_0030'].add_feature(namespace)

    def plugin_end(self):
        for namespace in self.enabled_hashes:
            self.xmpp['xep_0030'].del_feature(feature=namespace)
        self.enabled_hashes.clear()

        self.xmpp['xep_0030'].del_feature(feature=Hash.namespace)

    def compute_hash(self, filename, function=None):
        if function is None:
            function = self.preferred
        h = self._hashlib_function[function]()
        with open(filename, 'rb') as f:
            while True:
                block = f.read(self.block_size)
                if not block:
                    break
                h.update(block)
        hash_elem = Hash()
        hash_elem['algo'] = function
        hash_elem['value'] = b64encode(h.digest())
        return hash_elem
