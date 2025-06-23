# Slixmpp: The Slick XMPP Library
# Copyright (C) 2025 nicoco
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.

import unittest
from xml.etree import ElementTree as ET

from slixmpp import register_stanza_plugin, ElementBase
from slixmpp.test import SlixTest
from slixmpp.plugins.xep_0492 import stanza
from slixmpp.plugins.xep_0402 import stanza as b_stanza


class TestNotificationSetting(SlixTest):
    def setUp(self):
        b_stanza.register_plugin()
        stanza.register_plugin()

    def test_never(self):
        bookmark = b_stanza.Conference()
        bookmark["extensions"]["notify"].configure("never")
        self.check(
            bookmark,
            """
            <conference xmlns='urn:xmpp:bookmarks:1'>
              <extensions>
                <notify xmlns='urn:xmpp:notification-settings:0'>
                  <never />
                </notify>
              </extensions>
            </conference>
            """,
            use_values=False,
        )

    def test_always(self):
        bookmark = b_stanza.Conference()
        bookmark["extensions"]["notify"].configure("always")
        self.check(
            bookmark,
            """
            <conference xmlns='urn:xmpp:bookmarks:1'>
              <extensions>
                <notify xmlns='urn:xmpp:notification-settings:0'>
                  <always />
                </notify>
              </extensions>
            </conference>
            """,
            use_values=False,
        )

    def test_on_mention(self):
        bookmark = b_stanza.Conference()
        bookmark["extensions"]["notify"].configure("on-mention")
        self.check(
            bookmark,
            """
            <conference xmlns='urn:xmpp:bookmarks:1'>
              <extensions>
                <notify xmlns='urn:xmpp:notification-settings:0'>
                  <on-mention />
                </notify>
              </extensions>
            </conference>
            """,
            use_values=False,
        )

    def test_advanced(self):
        bookmark = b_stanza.Conference()
        bookmark["extensions"]["notify"].configure("never", client_type="pc")
        bookmark["extensions"]["notify"].configure("on-mention", client_type="mobile")

        register_stanza_plugin(stanza.Advanced, AdvancedExtension)
        bookmark["extensions"]["notify"]["advanced"].enable("cool")
        bookmark["extensions"]["notify"]["advanced"]["cool"]["attrib"] = "cool-attrib"
        bookmark["extensions"]["notify"]["advanced"]["cool"]["content"] = "cool-content"
        self.check(
            bookmark,
            """
            <conference xmlns='urn:xmpp:bookmarks:1'>
              <extensions>
                <notify xmlns='urn:xmpp:notification-settings:0'>
                  <never client-type="pc" />
                  <on-mention client-type="mobile" />
                  <advanced>
                    <cool xmlns="cool-ns" attrib="cool-attrib">cool-content</cool>
                  </advanced>
                </notify>
              </extensions>
            </conference>
            """,
            use_values=False,
        )

    def test_change_config(self):
        bookmark = b_stanza.Conference()
        bookmark["extensions"]["notify"].configure("never")
        bookmark["extensions"]["notify"].configure("never", client_type="pc")
        bookmark["extensions"]["notify"].configure("on-mention", client_type="mobile")

        self.check(
            bookmark,
            """
            <conference xmlns='urn:xmpp:bookmarks:1'>
              <extensions>
                <notify xmlns='urn:xmpp:notification-settings:0'>
                  <never />
                  <never client-type="pc" />
                  <on-mention client-type="mobile" />
                </notify>
              </extensions>
            </conference>
            """,
            use_values=False,
        )

        bookmark["extensions"]["notify"].configure("always")

        self.check(
            bookmark,
            """
            <conference xmlns='urn:xmpp:bookmarks:1'>
              <extensions>
                <notify xmlns='urn:xmpp:notification-settings:0'>
                  <always />
                  <never client-type="pc" />
                  <on-mention client-type="mobile" />
                </notify>
              </extensions>
            </conference>
            """,
            use_values=False,
        )

        bookmark["extensions"]["notify"].configure("always", "mobile")

        self.check(
            bookmark,
            """
            <conference xmlns='urn:xmpp:bookmarks:1'>
              <extensions>
                <notify xmlns='urn:xmpp:notification-settings:0'>
                  <always />
                  <never client-type="pc" />
                  <always client-type="mobile" />
                </notify>
              </extensions>
            </conference>
            """,
            use_values=False,
        )

    def test_get_config(self):
        bookmark = b_stanza.Conference()
        bookmark["extensions"]["notify"].configure("never")
        bookmark["extensions"]["notify"].configure("never", client_type="pc")
        bookmark["extensions"]["notify"].configure("on-mention", client_type="mobile")

        self.assertEqual(bookmark["extensions"]["notify"].get_config(), "never")
        self.assertEqual(bookmark["extensions"]["notify"].get_config("pc"), "never")
        self.assertEqual(
            bookmark["extensions"]["notify"].get_config("mobile"), "on-mention"
        )

    def test_get_config_2(self):
        notify = stanza.Notify()
        notify.configure("always")
        self.assertEqual(notify.get_config(), "always")

        notify = stanza.Notify(
            xml=ET.fromstring(
                "<notify xmlns='urn:xmpp:notification-settings:0'><always /></notify>"
            )
        )
        self.assertEqual(notify.get_config(), "always")

        notify = stanza.Notify(
            xml=ET.fromstring(
                "<notify xmlns='urn:xmpp:notification-settings:0'>"
                "<always client-type='pc'/>"
                "</notify>"
            )
        )
        self.assertIsNone(notify.get_config())
        self.assertEqual(notify.get_config("pc"), "always")

    def test_add_config(self):
        notify = stanza.Notify(
            xml=ET.fromstring(
                "<notify xmlns='urn:xmpp:notification-settings:0'>"
                "<always client-type='pc'/>"
                "</notify>"
            )
        )
        notify.configure("never")
        self.check(
            notify,
            """
            <notify xmlns='urn:xmpp:notification-settings:0'>
                <never/>
                <always client-type='pc'/>
            </notify>
            """,
            use_values=False
        )

    def test_update_config(self):
        notify = stanza.Notify(
            xml=ET.fromstring(
                "<notify xmlns='urn:xmpp:notification-settings:0'>"
                "<always />"
                "</notify>"
            )
        )
        notify.configure("never")
        self.check(
            notify,
            """
            <notify xmlns='urn:xmpp:notification-settings:0'>
                <never/>
            </notify>
            """,
            use_values=False
        )

        notify = stanza.Notify(
            xml=ET.fromstring(
                "<notify xmlns='urn:xmpp:notification-settings:0'>"
                "<always client-type='pc'/>"
                "</notify>"
            )
        )
        notify.configure("never", client_type="pc")
        self.check(
            notify,
            """
            <notify xmlns='urn:xmpp:notification-settings:0'>
                <never client-type='pc'/>
            </notify>
            """,
            use_values=False
        )

class AdvancedExtension(ElementBase):
    namespace = "cool-ns"
    name = "cool"
    plugin_attrib = name
    interfaces = {"attrib", "content"}

    def set_content(self, content: str):
        self.xml.text = content


suite = unittest.TestLoader().loadTestsFromTestCase(TestNotificationSetting)
