#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8 et ts=4 sts=4 sw=4
#
# Copyright © 2022 Maxime “pep” Buquet <pep@bouah.net>
#
# Distributed under terms of the GPLv3+ license.

"""
    Tests for XEP-0454 (OMEMO Media Sharing) plugin.
"""

import unittest
from io import BytesIO
from slixmpp.test import SlixTest
from slixmpp.plugins.xep_0454 import XEP_0454


class TestMediaSharing(SlixTest):

    def testEncryptDecryptSmall(self):
        plain = b'qwertyuiop'
        ciphertext, fragment = XEP_0454.encrypt(input_file=BytesIO(plain))
        result = XEP_0454.decrypt(BytesIO(ciphertext), fragment)

        self.assertEqual(plain, result)

    def testEncryptDecrypt(self):
        plain = b'a' * 4096 + b'qwertyuiop'
        ciphertext, fragment = XEP_0454.encrypt(input_file=BytesIO(plain))
        result = XEP_0454.decrypt(BytesIO(ciphertext), fragment)

        self.assertEqual(plain, result)

    def testFormatURL(self):
        url = 'https://foo.bar'
        fragment = 'a' * 88
        result = XEP_0454.format_url(url, fragment)
        self.assertEqual('aesgcm://foo.bar#' + 'a' * 88, result)

suite = unittest.TestLoader().loadTestsFromTestCase(TestMediaSharing)
