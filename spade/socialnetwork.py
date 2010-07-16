import Behaviour
import AID
from xmpp import *

class PresenceBehaviour(Behaviour.EventBehaviour):
    def _process(self):
        self.msg = self._receive(False)
        if self.msg != None:
            if self.msg.getType() == "subscribe":
                # Subscribe petition
                # Answer YES
                rep = Presence(to=self.msg.getFrom())
                rep.setType("subscribed")
                self.myAgent.send(rep)
                self.DEBUG( str(self.msg.getFrom())  + " subscribes to me")
                rep.setType("subscribe")
                self.myAgent.send(rep)
            if self.msg.getType() == "subscribed":
                if self.msg.getFrom() == self.myAgent.getAMS().getName():
                    # Subscription confirmation from AMS
                    self.DEBUG( "Agent: " + str(self.myAgent.getAID().getName()) + " registered correctly (inform)","ok")
                else:
                    self.DEBUG(str(self.msg.getFrom()) + "has subscribed me")
            elif self.msg.getType() == "unsubscribed":
                # Unsubscription from AMS
                if self.msg.getFrom() == self.myAgent.getAMS().getName():
                    self.DEBUG("There was an error registering in the AMS: " + str(self.getAID().getName()),"err")
                else:
                    self.DEBUG(str(self.msg.getFrom()) + " has unsubscribed me")
            elif self.msg.getType() in ["available", ""]:
                self.myAgent.setSocialItem(self.msg.getFrom(), "available")
            elif self.msg.getType() == "unavailable":
                self.myAgent.setSocialItem(self.msg.getFrom(), "unavailable")

            #self.myAgent.getSocialNetwork()


class RosterBehaviour(Behaviour.EventBehaviour):
    def _process(self):
        stanza = self._receive(False)
        if stanza != None:
            for item in stanza.getTag('query').getTags('item'):
                jid=item.getAttr('jid')
                if item.getAttr('subscription')=='remove':
                    if self.myAgent._roster.has_key(jid): del self.myAgent.roster[jid]
                elif not self.myAgent._roster.has_key(jid): self.myAgent._roster[jid]={}
                self.myAgent._roster[jid]['name']=item.getAttr('name')
                self.myAgent._roster[jid]['ask']=item.getAttr('ask')
                self.myAgent._roster[jid]['subscription']=item.getAttr('subscription')
                self.myAgent._roster[jid]['groups']=[]
                if not self.myAgent._roster[jid].has_key('resources'): self.myAgent._roster[jid]['resources']={}
                for group in item.getTags('group'): self.myAgent._roster[jid]['groups'].append(group.getData())
            self.myAgent._waitingForRoster = False

class SocialItem:
    """
    A member of an agent's Social Network
    AID, presence & subscription
    """
    def __init__(self, agent, jid, presence=''):
        self.myAgent = agent
        self._jid = jid
        self._presence = presence

        # Generate AID
        self._aid = AID.aid(name=jid, addresses=["xmpp://"+str(jid)])

        # Get subscription from roster
        roster = agent._roster
        if roster.has_key(jid):
            if roster[jid].has_key("subscription"):
                self._subscription = roster[jid]["subscription"]
            else:
                self._subscription = "none"
        else:
            self._subscription = "none"

    def setPresence(self, presence):
        self._presence = presence

    def getPresence(self):
        return self._presence

    def subscribe(self):
        self.myAgent.jabber.Roster.Subscribe(self._jid)

