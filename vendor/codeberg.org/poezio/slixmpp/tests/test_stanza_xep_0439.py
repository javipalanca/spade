import unittest
from slixmpp import Message
from slixmpp.test import SlixTest
from slixmpp.plugins.xep_0439 import stanza


class TestQuickResponse(SlixTest):

    def setUp(self):
        stanza.register_plugins()

    def testResponse(self):
        message = Message()
        message['body'] = 'Reply 1 or 2?'
        for (value, label) in [('1', 'Rep 1'), ('2', 'Rep 2')]:
            rep = stanza.Response()
            rep['value'] = value
            rep['label'] = label
            message.append(rep)

        self.check(message, """
<message>
  <body>Reply 1 or 2?</body>
  <response xmlns="urn:xmpp:tmp:quick-response" value="1" label="Rep 1" />
  <response xmlns="urn:xmpp:tmp:quick-response" value="2" label="Rep 2" />
</message>
        """, use_values=False)

    def testAction(self):
        message = Message()
        message['body'] = 'action 1 or 2?'
        for (id_, label) in [('1', 'action 1'), ('2', 'action 2')]:
            act = stanza.Action()
            act['id'] = id_
            act['label'] = label
            message.append(act)

        self.check(message, """
<message>
  <body>action 1 or 2?</body>
  <action xmlns="urn:xmpp:tmp:quick-response" id="1" label="action 1" />
  <action xmlns="urn:xmpp:tmp:quick-response" id="2" label="action 2" />
</message>
        """, use_values=False)

    def testActionSelected(self):
        message = Message()
        message['action_selected']['id'] = 'act1'

        self.check(message, """
<message>
  <action-selected xmlns="urn:xmpp:tmp:quick-response" id="act1" />
</message>
        """, use_values=False)


suite = unittest.TestLoader().loadTestsFromTestCase(TestQuickResponse)
