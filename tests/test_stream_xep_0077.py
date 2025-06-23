"""
This only covers the component registration side of the XEP-0077 plugin
"""

import unittest

from slixmpp import ComponentXMPP, Iq
from slixmpp.xmlstream import register_stanza_plugin
from slixmpp.test import SlixTest
from slixmpp.plugins.xep_0077 import Register


class TestRegistration(SlixTest):
    def setUp(self):
        self.stream_start(
            mode="component", plugins=["xep_0077"], jid="shakespeare.lit", server="lit"
        )

    def testRegistrationForm(self):
        self.stream_start(
            mode="component", plugins=["xep_0077"], jid="shakespeare.lit", server="lit"
        )
        self.recv(
            """
            <iq type='get' id='reg1' to='shakespeare.lit' from='bill@server/resource'>
                <query xmlns='jabber:iq:register'/>
            </iq>
            """,
        )
        self.send(
            f"""
            <iq type='result' id='reg1' from='shakespeare.lit' to='bill@server/resource'>
                <query xmlns='jabber:iq:register'>
                    <instructions>{self.xmpp["xep_0077"].form_instructions}</instructions>
                    <username/>
                    <password/>
                </query>
            </iq>
            """,
            use_values=False  # Fails inconsistently without this
        )

    def testRegistrationSuccessAndModif(self):
        self.recv(
            """
            <iq type='set' id='reg2' to='shakespeare.lit' from="bill@server/resource">
                <query xmlns='jabber:iq:register'>
                    <username>bill</username>
                    <password>Calliope</password>
                </query>
            </iq>
            """
        )
        self.send("<iq type='result' id='reg2' from='shakespeare.lit' to='bill@server/resource'/>")
        user_store = self.xmpp["xep_0077"]._user_store
        self.assertEqual(user_store["bill@server"]["username"], "bill")
        self.assertEqual(user_store["bill@server"]["password"], "Calliope")

        self.recv(
            """
            <iq type='get' id='reg1' to='shakespeare.lit' from="bill@server/resource">
                <query xmlns='jabber:iq:register'/>
            </iq>
            """,
        )
        self.send(
            f"""
            <iq type='result' id='reg1' to="bill@server/resource" from='shakespeare.lit'>
                <query xmlns='jabber:iq:register'>
                    <instructions>{self.xmpp["xep_0077"].form_instructions}</instructions>
                    <username>bill</username>
                    <password>Calliope</password>
                    <registered />
                </query>
            </iq>
            """,
            use_values=False  # Fails inconsistently without this
        )

    def testRegistrationAndRemove(self):
        self.recv(
            """
            <iq type='set' id='reg2' to='shakespeare.lit' from="bill@shakespeare.lit/globe">
                <query xmlns='jabber:iq:register'>
                    <username>bill</username>
                    <password>Calliope</password>
                </query>
            </iq>
            """
        )
        self.send("<iq type='result' id='reg2' from='shakespeare.lit' to='bill@shakespeare.lit/globe'/>")
        pseudo_iq = self.xmpp.Iq()
        pseudo_iq["from"] = "bill@shakespeare.lit/globe"
        fut = self.xmpp.wrap(self.xmpp["xep_0077"].api["user_get"](None, None, None, pseudo_iq))
        self.run_coro(fut)
        user = fut.result()
        self.assertEqual(user["username"], "bill")
        self.assertEqual(user["password"], "Calliope")
        self.recv(
            """
            <iq type='set' from='bill@shakespeare.lit/globe' id='unreg1'>
            <query xmlns='jabber:iq:register'>
                <remove/>
            </query>
            </iq>
            """
        )
        self.send("<iq type='result' to='bill@shakespeare.lit/globe' id='unreg1'/>")
        user_store = self.xmpp["xep_0077"]._user_store
        self.assertIs(user_store.get("bill@shakespeare.lit"), None)



suite = unittest.TestLoader().loadTestsFromTestCase(TestRegistration)
