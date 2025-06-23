import datetime
import unittest

from slixmpp import Iq
from slixmpp.test import SlixTest

from slixmpp.plugins.xep_0292 import stanza


REF = """
<iq>
    <vcard xmlns='urn:ietf:params:xml:ns:vcard-4.0'>
        <fn>
            <text>Full Name</text>
        </fn>
        <n><given>Full</given><surname>Name</surname></n>
        <nickname>
            <text>some nick</text>
        </nickname>
        <bday>
            <date>1984-05-21</date>
        </bday>
        <url>
            <uri>https://nicoco.fr</uri>
        </url>
        <note>
            <text>About me</text>
        </note>
        <impp>
            <uri>xmpp:test@localhost</uri>
        </impp>
        <email>
            <text>test@gmail.com</text>
        </email>
        <tel>
            <parameters>
                <type><text>work</text></type>
            </parameters>
            <uri>tel:+555</uri>
        </tel>
        <adr>
            <locality>Nice</locality>
            <country>France</country>
        </adr>
    </vcard>
</iq>
"""


class TestVcard(SlixTest):
    def test_basic_interfaces(self):
        iq = Iq()
        x = iq["vcard"]

        x["fn"]["text"] = "Full Name"
        x["nickname"]["text"] = "some nick"
        x["n"]["given"] = "Full"
        x["n"]["surname"] = "Name"
        x["bday"]["date"] = datetime.date(1984, 5, 21)
        x["note"]["text"] = "About me"
        x["url"]["uri"] = "https://nicoco.fr"
        x["impp"]["uri"] = "xmpp:test@localhost"
        x["email"]["text"] = "test@gmail.com"

        x["tel"]["uri"] = "tel:+555"
        x["tel"]["parameters"]["type_"]["text"] = "work"
        x["adr"]["locality"] = "Nice"
        x["adr"]["country"] = "France"

        self.check(iq, REF, use_values=False)

    def test_easy_interface(self):
        iq = Iq()
        x: stanza.VCard4 = iq["vcard"]

        x["full_name"] = "Full Name"
        x["given"] = "Full"
        x["surname"] = "Name"
        x["birthday"] = datetime.date(1984, 5, 21)
        x.add_nickname("some nick")
        x.add_note("About me")
        x.add_url("https://nicoco.fr")
        x.add_impp("xmpp:test@localhost")
        x.add_email("test@gmail.com")
        x.add_tel("+555", "work")
        x.add_address("France", "Nice")

        self.check(iq, REF, use_values=False)

    def test_2_phones(self):
        vcard = stanza.VCard4()
        tel1 = stanza.Tel()
        tel1["parameters"]["type_"]["text"] = "work"
        tel1["uri"] = "tel:+555"
        tel2 = stanza.Tel()
        tel2["parameters"]["type_"]["text"] = "devil"
        tel2["uri"] = "tel:+666"
        vcard.append(tel1)
        vcard.append(tel2)
        self.check(
            vcard,
            """
            <vcard xmlns='urn:ietf:params:xml:ns:vcard-4.0'>
                <tel>
                    <parameters>
                        <type><text>work</text></type>
                    </parameters>
                    <uri>tel:+555</uri>
                </tel>
                <tel>
                    <parameters>
                        <type><text>devil</text></type>
                    </parameters>
                    <uri>tel:+666</uri>
                </tel>
            </vcard>
            """,
            use_values=False
        )

suite = unittest.TestLoader().loadTestsFromTestCase(TestVcard)
