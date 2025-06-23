import unittest
from slixmpp import Message, Presence, Iq, JID
from slixmpp.test import SlixTest
from slixmpp.plugins.xep_0045.stanza import (
    MUCPresence,
    MUCJoin,
    MUCMessage,
    MUCAdminQuery,
    MUCAdminItem,
    MUCHistory,
    MUCOwnerQuery,
    MUCOwnerDestroy,
    MUCStatus,
    MUCInvite,
    MUCDecline,
    MUCUserItem,
    MUCActor,
)
from slixmpp.xmlstream import register_stanza_plugin, ET


class TestMUC(SlixTest):

    def setUp(self):
        register_stanza_plugin(MUCPresence, MUCUserItem)
        register_stanza_plugin(MUCMessage, MUCUserItem)
        register_stanza_plugin(MUCUserItem, MUCActor)
        register_stanza_plugin(MUCMessage, MUCInvite)
        register_stanza_plugin(MUCMessage, MUCDecline)
        register_stanza_plugin(MUCMessage, MUCStatus)
        register_stanza_plugin(MUCPresence, MUCStatus)
        register_stanza_plugin(Presence, MUCPresence)
        register_stanza_plugin(Presence, MUCJoin)
        register_stanza_plugin(MUCJoin, MUCHistory)
        register_stanza_plugin(Message, MUCMessage)
        register_stanza_plugin(Iq, MUCAdminQuery)
        register_stanza_plugin(Iq, MUCOwnerQuery)
        register_stanza_plugin(MUCOwnerQuery, MUCOwnerDestroy)
        register_stanza_plugin(MUCAdminQuery, MUCAdminItem, iterable=True)


    def testPresence(self):
        presence = Presence()
        presence['from'] = JID('muc@service/nick')
        presence['muc']['item']['affiliation'] = 'member'
        presence['muc']['item']['role'] = 'participant'
        presence['muc']['status_codes'] = (100, 110, 210)

        self.check(presence, """
<presence from='muc@service/nick'>
  <x xmlns='http://jabber.org/protocol/muc#user'>
    <item affiliation='member' role='participant'/>
    <status code='100'/>
    <status code='110'/>
    <status code='210'/>
  </x>
</presence>
        """, use_values=False)

    def testPresenceReason(self):
        presence = Presence()
        presence['from'] = JID('muc@service/nick')
        presence['muc']['item']['affiliation'] = 'member'
        presence['muc']['item']['role'] = 'participant'
        presence['muc']['item']['reason'] = 'coucou'
        presence['muc']['item']['actor']['nick'] = 'JPR'

        self.check(presence, """
<presence from='muc@service/nick'>
  <x xmlns='http://jabber.org/protocol/muc#user'>
    <item affiliation='member' role='participant'>
      <actor nick="JPR"/>
      <reason>coucou</reason>
    </item>
  </x>
</presence>
        """, use_values=False)


    def testPresenceLegacy(self):
        presence = Presence()
        presence['from'] = JID('muc@service/nick')
        presence['muc']['affiliation'] = 'member'
        presence['muc']['role'] = 'participant'
        presence['muc']['status_codes'] = (100, 110, 210)

        self.check(presence, """
<presence from='muc@service/nick'>
  <x xmlns='http://jabber.org/protocol/muc#user'>
    <item affiliation='member' role='participant'/>
    <status code='100'/>
    <status code='110'/>
    <status code='210'/>
  </x>
</presence>
        """, use_values=False)


    def testInvite(self):
        message = Message()
        message['from'] = 'user@server'
        message['to'] = 'muc@service'
        message['muc']['invite']['to'] = JID('user2@server2')
        message['muc']['invite']['reason'] = 'Hey'

        self.check(message, """
<message
    from='user@server'
    to='muc@service'>
  <x xmlns='http://jabber.org/protocol/muc#user'>
    <invite to='user2@server2'>
      <reason>Hey</reason>
    </invite>
  </x>
</message>
        """, use_values=False)

    def testAdmin(self):
        iq = Iq()
        iq['id'] = '0'
        iq['type'] = 'set'
        iq.enable('mucadmin_query')
        items = [
            ('none', 'test@example/a'),
            ('owner', 'owner@example/a'),
        ]
        for aff, jid in items:
            item_el = MUCAdminItem()
            item_el['affiliation'] = aff
            item_el['jid'] = jid
            iq['mucadmin_query'].append(item_el)
        self.check(iq, """
<iq type='set' id='0'>
  <query xmlns='http://jabber.org/protocol/muc#admin'>
    <item jid='test@example/a'
          affiliation='none'/>
    <item jid='owner@example/a'
          affiliation='owner'/>
  </query>
</iq>
        """, use_values=False)

    def testSetAffiliation(self):
        iq = Iq()
        iq['type'] = 'set'
        iq['id'] = '1'
        iq['mucadmin_query']['item']['jid'] = JID('test@example.com')
        iq['mucadmin_query']['item']['affiliation'] = 'owner'
        self.check(iq, """
<iq type='set' id='1'>
  <query xmlns='http://jabber.org/protocol/muc#admin'>
    <item jid='test@example.com'
          affiliation='owner'/>
  </query>
</iq>
        """, use_values=False)


suite = unittest.TestLoader().loadTestsFromTestCase(TestMUC)
