# -*- coding: utf-8 -*-
import spade.Behaviour
import spade.AID
from xmpp.protocol import Presence
import time

class ContactNotInGroup(Exception): pass
class ContactInGroup(Exception): pass

class PresenceBehaviour(spade.Behaviour.EventBehaviour):
    def _process(self):
        self.msg = self._receive(False)
        if self.msg is not None:
            typ = self.msg.getType()
            to = self.msg.getFrom()
            if typ == "":
                typ = "available"
            self.DEBUG("Presence msg received:" + str(self.msg), 'ok')
            #print self.myAgent.getName() + "--> Presence msg received:" + str(self.msg)
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
                self.DEBUG(str(self.msg.getFrom()) + " is now available.", 'ok', 'presence')
            elif typ == "unavailable":
                self.myAgent.roster.roster.PresenceHandler(dis=None, pres=self.msg)
                self.DEBUG(str(self.msg.getFrom()) + " is now unavailable.", 'ok', 'presence')

            else:
                self.myAgent.roster.roster.PresenceHandler(dis=None, pres=self.msg)

            #Send and ACLMessage with the presence information to be aware
            msg = self.myAgent.newMessage()
            msg.setPerformative('inform')
            msg.setSender(spade.AID.aid(to, ["xmpp://" + str(to)]))
            msg.setOntology("Presence")
            msg.setProtocol(typ)
            msg.setContent(str(self.msg))
            self.myAgent.postMessage(msg)


class Roster:
    """
    This class manages the social aspect of the agents.
    It provides the necessary methods to ask for contacts,
    ask for contacts status, subscriptions, etc.
    """
    def __init__(self, agent):
        self.myAgent = agent
        self.roster = self.myAgent.jabber.getRoster()  # self.myAgent.jabber.Roster
        self._acceptAllSubscriptions = False
        self._declineAllSubscriptions = False
        self._followbackAllSubscriptions = False

    def sendPresence(self, typ=None, priority=None, show=None, status=None):
        '''
        Updates your presence to all your contacts
        typ - your presence type (available, unavailable,...) default='available'
        priority - the priority of the resource you are connected from
        show - The message shown to your contacts
        status - a brief description of your status
        '''
        jid = self.myAgent.getName() + self.myAgent.resource
        self.myAgent.jabber.send(Presence(jid, typ=typ, priority=priority, show=show, status=status))

    def isAvailable(self, jid):
        '''
        return True if a contact is available
        Otherwise return False
        jid - is teh JabberID of the contact, not the AID (user@server/optionalresource)
        '''
        item = self.getContact(jid)
        if item:
            return len(item['resources']) > 0
        return False

    def subscribe(self, jid):
        '''
        Ask for a friendship subscription to another agent
        The forementioned agent may accept or refuse the subscription
        by means of the methods acceptSubscription and declineSubscription
        '''
        self.roster.Subscribe(jid)

    def unsubscribe(self, jid):
        '''
        Unsubscribe from an agent
        There is no need of confirmation by the forementioned agent
        '''
        self.roster.Unsubscribe(jid)

    def checkSubscription(self, jid):
        '''
        Returns the subscription status of agent 'jid':
        'none' - there is no subscription with the agent
        'from' - you are subscribed to its notifications
        'to' - the agent is subscribed to your notifications
        'both' - both agents are subscribed to their corresponding notifications
        '''
        item = self.getContact(jid)
        if item and 'subscription' in item.keys():
            return item['subscription']
        return 'none'

    def acceptSubscription(self, jid):
        '''
        Accepts the subscription request from 'jid'
        '''
        msg = Presence(to=jid, typ="subscribed")
        self.myAgent.send(msg)
        self.myAgent.DEBUG("I have accepted the " + str(jid) + "'s request of subscription to me")

    def declineSubscription(self, jid):
        '''
        Declines the subscription request from 'jid'
        '''
        msg = Presence(to=jid, typ="unsubscribed")
        self.myAgent.send(msg)
        self.myAgent.DEBUG("I have declined the " + str(jid) + "'s request of subscription to me")

    def acceptAllSubscriptions(self, accept=True):
        '''
        Accepts all future incoming subscription requests from any agent if accept==True
        '''
        self._acceptAllSubscriptions = accept
        if accept:
            self._declineAllSubscriptions = False
        self.myAgent.DEBUG("Accept all subscription requests.", 'info')

    def declineAllSubscriptions(self, accept=True):
        '''
        Declines all future incoming subscription requests from any agent if accept==True
        '''
        self._declineAllSubscriptions = accept
        if accept:
            self._acceptAllSubscriptions = False
        self.myAgent.DEBUG("Decline all subscription requests.", 'info')

    def followbackAllSubscriptions(self, accept=True):
        '''
        Answers all future incoming subscription requests from any agent
        with a subcribe request if accept==True
        This not affects to the acceptance or declination of the incoming request
        '''
        self._followbackAllSubscriptions = accept
        self.myAgent.DEBUG("Followback all subscription requests.", 'info')

    def requestRoster(self, force=False):
        self.roster.Request(force)
        #self.myAgent.DEBUG("Received roster: " + str(self.roster._data), 'ok')

    def getRoster(self):
        return self.roster

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

    def getContact(self, jid):
        '''
        Returns a dict containing the presence information of contact 'jid'
        '''
        return self.roster.getItem(jid)

    def deleteContact(self, jid):
        self.roster.delItem(jid)

    def getContacts(self):
        '''
        returns a list of your contacts with their presence information
        '''
        return self.roster.getItems()

    def getAsk(self, jid):
        return self.roster.getAsk(jid)

    def getGroups(self, jid):
        if self.getContact(jid):
            return self.roster.getGroups(jid)
        else:
            return []

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
        if not groups:
            groups = list()
        if group not in groups:
            groups.append(group)
        self.roster.setItem(jid=jid, groups=groups)
        counter = 20
        while group not in self.getGroups(jid) and counter > 0:
            time.sleep(0.5)
            counter -= 1
        if group not in self.getGroups(jid):
            raise ContactNotInGroup

    def delContactFromGroup(self, jid, group):
        groups = self.getGroups(jid)
        if group in groups:
            groups.remove(group)
            self.roster.setItem(jid=jid, groups=groups)

        counter = 20
        while group in self.getGroups(jid) and counter > 0:
            time.sleep(0.5)
            counter -= 1
        if group in self.getGroups(jid):
            raise ContactInGroup

    def isContactInGroup(self, jid, group):
        return group in self.getGroups(jid)

    def getContactsInGroup(self, group):
        result = list()
        for jid in self.getContacts():
            groups = self.getGroups(jid)
            if groups and group in groups:
                result.append(jid)
        return result

    def sendToGroup(self, msg, group):
        if isinstance(msg, spade.ACLMessage.ACLMessage):
            for jid in self.getContactsInGroup(group):
                msg.addReceiver(spade.AID.aid(jid, ['xmpp://' + str(jid)]))
            self.myAgent.send(msg)
        else:
            for jid in self.getContactsInGroup(group):
                msg.setTo(jid)
                self.myAgent.send(msg)
