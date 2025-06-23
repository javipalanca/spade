import unittest
from slixmpp.test import SlixTest
from slixmpp.stanza.message import Message
from slixmpp.stanza.htmlim import HTMLIM
from slixmpp.plugins.xep_0172 import UserNick
from slixmpp.xmlstream import register_stanza_plugin


class TestMessageStanzas(SlixTest):

    def setUp(self):
        register_stanza_plugin(Message, HTMLIM)
        register_stanza_plugin(Message, UserNick)

    def testGroupchatReplyRegression(self):
        "Regression groupchat reply should be to barejid"
        msg = self.Message()
        msg['to'] = 'me@myserver.tld'
        msg['from'] = 'room@someservice.someserver.tld/somenick'
        msg['type'] = 'groupchat'
        msg['body'] = "this is a message"
        msg = msg.reply()
        self.assertTrue(str(msg['to']) == 'room@someservice.someserver.tld')

    def testHTMLPlugin(self):
        "Test message/html/body stanza"
        msg = self.Message()
        msg['to'] = "fritzy@netflint.net/slixmpp"
        msg['body'] = "this is the plaintext message"
        msg['type'] = 'chat'
        msg['html']['body'] = '<p>This is the htmlim message</p>'
        self.check(msg, """
          <message to="fritzy@netflint.net/slixmpp" type="chat">
            <body>this is the plaintext message</body>
            <html xmlns="http://jabber.org/protocol/xhtml-im">
              <body xmlns="http://www.w3.org/1999/xhtml">
                <p>This is the htmlim message</p>
             </body>
            </html>
          </message>""")

    def testNickPlugin(self):
        "Test message/nick/nick stanza."
        msg = self.Message()
        msg['nick']['nick'] = 'A nickname!'
        self.check(msg, """
          <message>
            <nick xmlns="http://jabber.org/protocol/nick">A nickname!</nick>
          </message>
        """)


suite = unittest.TestLoader().loadTestsFromTestCase(TestMessageStanzas)
