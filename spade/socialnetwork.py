# -*- coding: utf-8 -*-
import Behaviour
import AID
from xmpp import *
from xmpp.protocol import Presence


class PresenceBehaviour(Behaviour.EventBehaviour):
    def _process(self):
        self.msg = self._receive(False)
        if self.msg is not None:
            typ = self.msg.getType()
            to = self.msg.getFrom()
            if typ == "":
                typ = "available"
            self.DEBUG("Presence msg received:" + str(self.msg), 'ok')
            if typ == "subscribe":
                self.DEBUG("Agent " + str(to) + " wants to subscribe to me", "info")
                # Subscribe petition
                if self.myAgent.roster._acceptAllSubscriptions:
                    self.myAgent.roster.acceptSubscription(to)

                    if self.myAgent.roster._followbackAllSubscriptions:
                        self.myAgent.roster.subscribe(to)

                elif self.myAgent.roster._declineAllSubscriptions:
                    to = self.msg.getFrom()
                    self.myAgent.roster.declineSubscription(to)

            elif typ == "subscribed":
                if self.msg.getFrom() == self.myAgent.getAMS().getName():
                    # Subscription confirmation from AMS
                    self.DEBUG("Agent: " + str(self.myAgent.getAID().getName()) + " registered correctly (inform)", "ok")
                else:
                    self.DEBUG(str(self.msg.getFrom()) + " has accepted my subscription")
            elif typ == "unsubscribed":
                # Unsubscription from AMS
                if self.msg.getFrom() == self.myAgent.getAMS().getName():
                    self.DEBUG("There was an error registering in the AMS: " + str(self.getAID().getName()), "err")
                else:
                    self.DEBUG(str(self.msg.getFrom()) + " has unsubscribed me")


            elif typ in ["available", ""]:
                self.msg.setType("")
                self.myAgent.roster.roster.PresenceHandler(dis=None, pres=self.msg)
                self.DEBUG(str(self.msg.getFrom()) + " is now available.", 'ok','presence')
            elif typ == "unavailable":
                self.myAgent.roster.roster.PresenceHandler(dis=None, pres=self.msg)
                self.DEBUG(str(self.msg.getFrom()) + " is now unavailable.", 'ok','presence')

            else:
                self.myAgent.roster.roster.PresenceHandler(dis=None, pres=self.msg)

            #Send and ACLMessage with the presence information to be aware
            msg = self.myAgent.newMessage()
            msg.setPerformative('inform')
            msg.setSender(AID.aid(to, ["xmpp://"+str(to)]))
            msg.setOntology("Presence")
            msg.setProtocol(typ)
            msg.setContent(str(self.msg))
            self.myAgent.postMessage(msg)

class RosterBehaviour(Behaviour.Behaviour):
    def _process(self):
        stanza = self._receive(True)
        if stanza is not None:
            self.DEBUG("ROSTER received:" + str(stanza), 'ok')
            for item in stanza.getTag('query').getTags('item'):
                jid = item.getAttr('jid')
                if item.getAttr('subscription') == 'remove':
                    if jid in self.myAgent._roster:
                        del self.myAgent.roster[jid]
                        continue
                elif jid not in self.myAgent._roster:
                    self.myAgent._roster[jid] = Contact(self.myAgent, jid)
                self.myAgent._roster[jid].setName(item.getAttr('name'))
                self.myAgent._roster[jid].setAsk(item.getAttr('ask'))
                self.myAgent._roster[jid].setSubscription(item.getAttr('subscription'))
                #self.myAgent._roster[jid]['groups'] = []
                #if 'resources' not in self.myAgent._roster[jid]:
                #    self.myAgent._roster[jid]['resources'] = {}
                for group in item.getTags('group'):
                    self.myAgent._roster[jid].addGroup(group.getData())
            self.myAgent._waitingForRoster = False


class Roster:
    """
    """
    def __init__(self, agent):
        self.myAgent = agent
        self.myAgent.jabber.getRoster()
        self.roster = self.myAgent.jabber.Roster
        self._acceptAllSubscriptions = False
        self._declineAllSubscriptions = False
        self._followbackAllSubscriptions = False

    def sendPresence(self, typ=None, priority=None, show=None, status=None):
        jid = self.myAgent.getName() + self.myAgent.resource
        self.myAgent.jabber.send(Presence(jid, typ=typ, priority=priority, show=show, status=status))

    def isAvailable(self, jid):
        item = self.getContact(jid)
        if item:
            return len(item['resources']) > 0
        return False

    def subscribe(self, jid):
        self.roster.Subscribe(jid)

    def unsubscribe(self,jid):
        self.roster.Unsubscribe(jid)

    def checkSubscription(self, jid):
        item = self.getContact(jid)
        if item and 'subscription' in item.keys():
                return item['subscription']
        return 'none'

    def acceptSubscription(self, jid):
        msg = Presence(to=jid, typ="subscribed")
        self.myAgent.send(msg)
        self.myAgent.DEBUG("I have accepted the " + str(jid) + "'s request of subscription to me")

    def declineSubscription(self, jid):
        msg = Presence(to=jid, typ="unsubscribed")
        self.myAgent.send(msg)
        self.myAgent.DEBUG("I have declined the " + str(jid) + "'s request of subscription to me")

    def acceptAllSubscriptions(self, accept=True):
        self._acceptAllSubscriptions = accept
        if accept:
            self._declineAllSubscriptions = False
        self.myAgent.DEBUG("Accept all subscription requests.", 'info')

    def declineAllSubscriptions(self, accept=True):
        self._declineAllSubscriptions = accept
        if accept:
            self._acceptAllSubscriptions = False
        self.myAgent.DEBUG("Decline all subscription requests.", 'info')

    def followbackAllSubscriptions(self, accept=True):
        self._followbackAllSubscriptions = accept
        self.myAgent.DEBUG("Followback all subscription requests.", 'info')

    def requestRoster(self, force=False):
        if force:
            self.roster.set = 0
        return self.roster.getRoster()

    def waitingRoster(self):
        return not self.roster.set

    def setName(self, name):
        self.roster.setItem(self.myAgent.JID, name)

    def setPriority(self, prio):
        self.myAgent.jabber.send(Presence(priority=prio))

    def setShow(self, show):
        self.myAgent.jabber.send(Presence(show=show))

    def setStatus(self, status):
        self.myAgent.jabber.send(Presence(status=status))

    #def addContact(self, jid, name=None, groups=[]):
    #    self.roster.setItem(jid, name, groups)

    def delContact(self, jid):
        self.roster.delItem(jid)

    def getContact(self, jid):
        return self.roster.getItem(jid)

    def getContacts(self):
        return self.roster.getItems()

    def getAsk(self, jid):
        return self.roster.getAsk(jid)

    def getGroups(self, jid):
        return self.roster.getGroups(jid)

    def getName(self, jid):
        return self.roster.getName(jid)

    def getPriority(self, jid):
        return self.roster.getPriority(jid)

    def getShow(self, jid):
        return self.roster.getShow(jid)

    def getStatus(self, jid):
        return self.roster.getStatus(jid)

    def getSubscription(self, jid):
        return self.roster.getSubscription(jid)

    def getResources(self, jid):
        return self.roster.getResources(jid)

    def addContactToGroup(self, jid, group):
        groups = self.getGroups(jid)
        if group not in groups:
            groups.append(group)
        self.roster.setItem(jid=jid, groups=groups)


