# -*- coding: utf-8 -*-
import time
import ACLMessage
import AID
import MessageReceiver
import threading
import types
import copy
import xmpp
import re
import json


class BehaviourTemplate:
    """
    Template operators
    """

    def __init__(self, regex=False):
        self.regex = regex

    def match(self, message):
        return False

    def __and__(self, other):
        """Implementation of & operator"""
        return ANDTemplate(self, other)

    def __rand__(self, other):
        """Implementation of &= operator"""
        return (self & other)

    def __or__(self, other):
        """Implementation of | operator"""
        return ORTemplate(self, other)

    def __ror__(self, other):
        """Implementation of |= operator"""
        return (self | other)

    def __xor__(self, other):
        """Implementation of ^ operator"""
        return XORTemplate(self, other)

    def __rxor__(self, other):
        """Implementation of ^= operator"""
        return (self ^ other)

    def __invert__(self):
        """Implementation of ~ operator"""
        return NOTTemplate(self)


class ACLTemplate(BehaviourTemplate):
    """
    Template for message matching
    """
    def __init__(self, performative=None, jsonstring=None):
        self.performative = performative
        self.sender = None
        self.receivers = []
        self.reply_to = []
        self.content = None
        self.reply_with = None
        self.reply_by = None
        self.in_reply_to = None
        self.encoding = None
        self.language = None
        self.ontology = None
        self.protocol = None
        self.conversation_id = None
        #self.userDefProps = None

        if jsonstring!=None:
            self.loadJSON(jsonstring)

    def __str__(self):
        d = {"performative": self.performative, "sender": str(self.sender), "receivers": str(self.receivers), "reply_to": self.reply_to, "content": self.content, "reply_with": self.reply_with, "reply_by": self.reply_by, "in_reply_to": self.in_reply_to, "encoding": self.encoding, "language": self.language, "ontology": self.ontology, "protocol": self.protocol, "conversation_id": self.conversation_id}
        return str(dict((data for data in d.iteritems() if data[1])))

    def loadJSON(self, jsonstring):
        """
        loads a JSON string in the message
        """
        p = json.loads(jsonstring)

        if "performative" in p:
            self.setPerformative(p["performative"])

        if "sender" in p:
            s = AID.aid()
            s.loadJSON(p["sender"])
            self.setSender(s)

        if "receivers" in p:
            for i in p["receivers"]:
                s = AID.aid()
                s.loadJSON(i)
                self.addReceiver(s)

        if "content" in p:
            self.setContent(p["content"])

        if "reply-with" in p:
            self.setReplyWith(p["reply-with"])

        if "reply-by" in p:
            self.setReplyBy(p["reply-by"])

        if "in-reply-to" in p:
            self.setInReplyTo(p["in-reply-to"])

        if "reply-to" in p:
            for i in p["reply-to"]:
                s = AID.aid()
            s.loadJSON(i)
            self.addReplyTo(s)

        if "language" in p:
            self.setLanguage(p["language"])

        if "encoding" in p:
            self.setEncoding(p["encoding"])

        if "ontology" in p:
            self.setOntology(p['ontology'])

        if "protocol" in p:
            self.setProtocol(p['protocol'])

        if "conversation-id" in p:
            self.setConversationId(p["conversation-id"])


    def reset(self):
        self.__init__()

    def setSender(self, sender):
        self.sender = sender

    def getSender(self):
        return self.sender

    def addReceiver(self, recv):
        self.receivers.append(recv)

    def removeReceiver(self, recv):
        if recv in self.receivers:
            self.receivers.remove(recv)

    def getReceivers(self):
        return self.receivers

    def addReplyTo(self, re):
        if isinstance(re, AID.aid):
            self.reply_to.append(re)

    def removeReplyTo(self, re):
        if re in self.reply_to:
            self.reply_to.remove(re)

    def getReplyTo(self):
        return self.reply_to

    def setPerformative(self, p):
        self.performative = p

    def getPerformative(self):
        return self.performative

    def setContent(self, c):
        self.content = c

    def getContent(self):
        return self.content

    def setReplyWith(self, rw):
        self.reply_with = rw

    def getReplyWith(self):
        return self.reply_with

    def setInReplyTo(self, reply):
        self.in_reply_to = reply

    def getInReplyTo(self):
        return self.in_reply_to

    def setEncoding(self, e):
        self.encoding = e

    def getEncoding(self):
        return self.encoding

    def setLanguage(self, e):
        self.language = e

    def getLanguage(self):
        return self.language

    def setOntology(self, e):
        self.ontology = e

    def getOntology(self):
        return self.ontology

    def setReplyBy(self, e):
        self.reply_by = e

    def getReplyBy(self):
        return self.reply_by

    def setProtocol(self, e):
        self.protocol = e

    def getProtocol(self):
        return self.protocol

    def setConversationId(self, e):
        self.conversation_id = e

    def getConversationId(self):
        return self.conversation_id

    def match(self, message):
    #def acl_match(self, message):
        if message.__class__ != ACLMessage.ACLMessage:
            return False
        if (self.getPerformative() is not None):
            if (self.getPerformative() != message.getPerformative()):
                return False
        if (self.getConversationId() is not None):
            if (str(self.getConversationId()) != str(message.getConversationId())):
                return False
        if (self.sender is not None):
            if message.sender is not None:
                if not message.sender.match(self.sender):
                    return False
            else:
                return False
        if (self.receivers != []):
            for tr in self.receivers:
                found = False
                for mr in message.receivers:
                    if mr.match(tr):
                        found = True
                        break
                if not found:
                    return False
        if (self.getReplyTo() != []):
            if (self.getReplyTo() != message.getReplyTo()):
                return False
        if (self.content is not None):
            if (self.content != message.content):
                return False
        if (self.getReplyWith() is not None):
            if (self.getReplyWith() != message.getReplyWith()):
                return False
        if (self.getReplyBy() is not None):
            if (self.getReplyBy() != message.getReplyBy()):
                return False
        if (self.getInReplyTo() is not None):
            if (self.getInReplyTo() != message.getInReplyTo()):
                return False
        if (self.getEncoding() is not None):
            if (self.getEncoding() != message.getEncoding()):
                return False
        if (self.getLanguage() is not None):
            if (self.getLanguage() != message.getLanguage()):
                return False
        if (self.getOntology() is not None):
            if (self.getOntology() != message.getOntology()):
                return False
        if (self.getProtocol() is not None):
            if (self.getProtocol() != message.getProtocol()):
                return False
        return True


class NOTTemplate(BehaviourTemplate):
    def __init__(self, expr):
        self.expr = expr

    def match(self, message):
        return (not(self.expr.match(message)))


class ORTemplate(BehaviourTemplate):
    def __init__(self, expr1, expr2):
        self.expr1 = expr1
        self.expr2 = expr2

    def match(self, message):
        return (self.expr1.match(message) | self.expr2.match(message))


class ANDTemplate(BehaviourTemplate):
    def __init__(self, expr1, expr2):
        self.expr1 = expr1
        self.expr2 = expr2

    def match(self, message):
        return (self.expr1.match(message) & self.expr2.match(message))


class XORTemplate(BehaviourTemplate):
    def __init__(self, expr1, expr2):
        self.expr1 = expr1
        self.expr2 = expr2

    def match(self, message):
        return (self.expr1.match(message) ^ self.expr2.match(message))


'''
class PresenceTemplate(BehaviourTemplate):
    """
    Template for presence notifications
    """
    def __init__(self, frm=None, type=None, status=None, show=None, role=None, affiliation=None):
        self._frm, self._type, self._status, self._show, self._role, self._affiliation = frm,type,status,show,role,affiliation
'''


class MessageTemplate(BehaviourTemplate):
    def __init__(self, template, regex=False):
        # Discriminate Template class
        BehaviourTemplate.__init__(self, regex)
        self.template = copy.copy(template)
        if isinstance(template, ACLMessage.ACLMessage):
                self.template = ACLTemplate(jsonstring=template.asJSON())
                self.match = self.template.match
        elif "Message" in str(self.template.__class__) or "Presence" in str(self.template.__class__) or "Iq" in str(self.template.__class__) or "Node" in str(self.template.__class__):
                self.match = self.node_match
        else:  #isinstance(template, ACLTemplate):
                self.match = self.template.match
                # Default template option

    def __str__(self):
        return str(self.template)


    def node_match(self, other):
        """
        Function that matches a xmpp Node with another one
        """
        try:
            # Check types and classes
            if not isinstance(self.template, types.InstanceType):
                return False
            #if not issubclass(self.template.__class__, Node) and not issubclass(self.template.__class__, Protocol) and :
            if "Message" not in str(self.template.__class__) and "Presence" not in str(self.template.__class__) and "Iq" not in str(self.template.__class__) and "Node" not in str(self.template.__class__):
                return False

            if not isinstance(other, types.InstanceType):
                return False
            #if not issubclass(other.__class__ , Node):
            if "Message" not in str(other.__class__) and "Presence" not in str(other.__class__) and "Iq" not in str(other.__class__) and "Node" not in str(self.template.__class__):
                return False

            if self.template.name is not None:
                if self.template.name != other.name:
                    return False
            if self.template.attrs is not None and self.template.attrs != {}:
                for i, j in self.template.attrs.items():
                    if not self.regex:
                        if (i not in other.attrs.keys()) or (str(j) != str(other.attrs[i])):
                            return False
                    if not re.match(str(j), str(other.attrs[i])):
                        return False
            if self.template.data is not None and self.template.data != []:
                if self.template.data != other.data:
                    if not self.regex:
                        return False
                    if not re.match(str(self.template.data[0]), str(other.data[0])):
                        return False
            if self.template.namespace:
                if self.template.namespace != other.namespace:
                    return False

            for kid in self.template.kids:
                # Assemble a list of similar kids from the other node
                suspects = other.getTags(kid.getName())
                if not suspects:
                    return False
                value = False
                for s in suspects:
                    value = MessageTemplate(kid, regex=self.regex).node_match(s)
                    #value = self.node_match(kid, s)
                    if value is True:
                    # There is a match among the supects
                        break
                if not value:
                    # If we reach this point, there is no hope left . . . (no match among the suspects)
                    return False

        except Exception:
            return False
        # Arriving here means this is a perfect match

        return True

    def presence_match(self, message):  # frm=None, type=None, status=None, show=None):

        frm, type, status, show, role, affiliation = message.frm, message.type, message.status, message.show, message.role, message.affiliation

        #if self._frm    !=None and frm    != self._frm:    return False
        if self._type is not None and type != self._type:
            return False
        if self._status is not None and status != self._status:
            return False
        if self._show is not None and show != self._show:
            return False
        if self._role is not None and role != self._role:
            return False
        if self._affiliation is not None and affiliation != self._affiliation:
            return False

        if self._frm:
            if not xmpp.JID(self._frm).getResource():
                if self._frm != xmpp.JID(frm).getBareJID():
                    return False
            else:
                if self._frm != frm:
                    return False

        return True

    def message_match(self, msg):
        return self.node_match(msg)

    def iq_match(self, iq):
        return self.node_match(iq)

class Behaviour(MessageReceiver.MessageReceiver):
    def __init__(self):
        MessageReceiver.MessageReceiver.__init__(self)
        #self._running = False  # Not needed for now
        self.myParent = None
        self._forceKill = threading.Event()
        self._presenceHandlers = dict()

        self._exitcode = 0

    """
    def __getattr__(self, aname):
        return self.myAgent.__dict__[aname]

    def __setattr__(self, aname, value):
        # Base case: aname is defined locally
        if aname in self.__dict__:
            self.__dict__[aname] = value
        # Second case: aname is defined in "myAgent"
        elif "myAgent" in self.__dict__ and self.__dict__["myAgent"] and aname in self.myAgent.__dict__:
            setattr(self.myAgent, aname, value)
        # Third case: new local declaration
        else:
            self.__dict__[aname] = value
    """

    def __str__(self):
        return self.getName()

    def setParent(self, parent):
        self.myParent = parent

    def getParent(self):
        return self.myParent

    def setAgent(self, agent):
        """
        sets the agent which controls the behavior
        """
        self.myAgent = agent
        self.DEBUG = self.myAgent.DEBUG
        try:
            self.setName(str(self.myAgent.getName()) + " " + str(self.__class__.__name__))
        except:
            pass

    def getAgent(self):
        """
        returns the agent which controls the behavior
        """
        return self.myAgent

    def root(self):
        if (self.myParent is not None):
            return self.myParent.root()
        else:
            return self

    def done(self):
        """
        returns True if the behavior has finished
        else returns False
        """
        return False

    def _process(self):
        """
        main loop
        must be overridden
        """
        raise NotImplementedError

    def kill(self):
        """
        stops the behavior
        """
        try:
            self._forceKill.set()
            self.myAgent.DEBUG("Stopping Behavior " + str(self), "info")
        except:
            #Behavior is already dead
            self.myAgent.DEBUG("Behavior " + str(self) + " is already dead", "warn")

    def onStart(self):
        """
        this method runs when the behavior starts
        """
        pass

    def onEnd(self):
        """
        this method runs when the behavior stops
        """
        pass

    def exitCode(self):
        """
        returns the default exit code for the behavior
        """
        return self._exitcode

    def run(self):
        if not self.myAgent._running:
            # Get condition and wait for the other behaviours
            self.myAgent.behavioursGo.acquire()
            self.myAgent.behavioursGo.wait()
            self.myAgent.behavioursGo.release()

        """
        # Check wether this behaviour has already started
        if not self._running:
            self._running = True
        else:
            # The behaviour was already running, no need to run run (he he) twice
            return
        """
        self.onStart()
        try:
            while (not self.done()) and (not self._forceKill.isSet()):
                self._exitcode = self._process()
        except Exception, e:
            self.myAgent.DEBUG("Exception in Behaviour " + str(self) + ": " + str(e), "err")
        self.onEnd()
        #if issubclass(self.__class__, EventBehaviour):
        #    self.myAgent.removeBehaviour(self.__class__)
        #else:
        if not issubclass(self.__class__, EventBehaviour):
            self.myAgent.removeBehaviour(self)

        self.myAgent.DEBUG("Behavior " + str(self.getName()) + " finished.", "info")

    def registerPresenceHandler(self, template, handler):
        """
        DEPRECATED
        register a handler that will manage all incoming presence notifications matching the given presence template
        """
        self._presenceHandlers[handler] = template

    def managePresence(self, frm=None, type=None, status=None, show=None, role=None, affiliation=None):
        """
        DEPRECATED
        manage a FIPA-formed presence message
        """
        class struct:
            def __init__(self, frm, type, status, show, role, affiliation):
                self.frm, self.type, self.status, self.show, self.role, self.affiliation = frm, type, status, show, role, affiliation
        # Check every handler template to see which ones match
        for handler in self._presenceHandlers:
            t = self._presenceHandlers[handler]
            if t:
                if t.match(struct(frm, type, status, show, role, affiliation)):
                    handler(frm, type, status, show, role, affiliation)

    def setTemplate(self, template):
        """
        Set the message template for this behaviour
        """
        if self.myAgent:
            self.myAgent._behaviourList[self] = template


class OneShotBehaviour(Behaviour):
    """
    this behavior is only executed once
    """
    def __init__(self):
        Behaviour.__init__(self)
        self._firsttime = True

    def done(self):
        if self._firsttime is True:
            self._firsttime = False
            return False
        return True


class PeriodicBehaviour(Behaviour):
    """
    this behavior runs periodically with a period
    """
    def __init__(self, period, timestart=None):
        Behaviour.__init__(self)
        self._period = period
        if (timestart is None):
            self._nextActivation = time.time()
        else:
            self._nextActivation = timestart

    def getPeriod(self):
        return self._period

    def setPeriod(self, period):
        self._period = period

    def _process(self):
        if time.time() >= self._nextActivation:
            self._exitcode = self._onTick()
            while self._nextActivation <= time.time():
                self._nextActivation += self._period
        else:
            t = self._nextActivation - time.time()
            if t > 0:
                time.sleep(t)
        return self._exitcode

    def _onTick(self):
        """
        this method is executed every period
        must be overridden
        """
        raise NotImplementedError


class TimeOutBehaviour(PeriodicBehaviour):
    """
    this behavior is executed only once after a timeout
    """
    def __init__(self, timeout):
        PeriodicBehaviour.__init__(self, timeout, time.time() + timeout)
        self._stop = False

    def getTimeOut(self):
        return self.getPeriod()

    def stop(self):
        """
        cancels the programmed execution
        """
        self._stop = True

    def done(self):
        return self._stop

    def _onTick(self):
        if self._stop is False:
            self.timeOut()
        self.stop()

    def timeOut(self):
        """
        this method is executed after the timeout
        must be overridden
        """
        raise NotImplementedError


class FSMBehaviour(Behaviour):
    """
    this behavior is executed according to a Finite State Machine
    """
    def __init__(self):
        Behaviour.__init__(self)
        self._firstStateName = None
        self._lastStatesNames = []
        self._states = dict()
        self._transitions = dict()
        self._actualState = None
        self._lastexitcode = None
        self._destroy = False
        self._firsttime = True

    def setAgent(self, agent):
        """
        sets the parent agent
        """
        #self.setAgent(agent)
        Behaviour.setAgent(self, agent)
        for b in self._states:
            self._states[b].setAgent(agent)

    def registerState(self, behaviour, name):
        """
        registers a state with a behavior
        """
        if not issubclass(behaviour.__class__, OneShotBehaviour):
            print "WARNING! Registering not-OneShot as FSM state"
        behaviour.setParent(self)
        self._states[name] = behaviour
        self._transitions[name] = dict()
        behaviour._receive = self._receive
        behaviour.setTemplate = self.setTemplate
        behaviour._stateName = name

    def registerFirstState(self, behaviour, name):
        """
        sets the first state of the fsm
        """
        self.registerState(behaviour, name)
        self._firstStateName = name

    def registerLastState(self, behaviour, name):
        """
        sets the final state of the fsm
        """
        self.registerState(behaviour, name)
        self._lastStatesNames.append(name)

    def registerTransition(self, fromname, toname, event):
        """
        registers a transition between two states
        """
        self._transitions[fromname][event] = toname

    def getState(self, name):
        return self._states[name]

    #def onStart(self):
    #    self._actualState = self._firstStateName
    #    self._actualState.start()
    #    for b in self._states:
    #        self._states[b].start()
    #def onEnd(self):
    #    for b in self._states:
    #        self._states[b].kill()

    def exitCode(self):
        return self._lastexitcode

    def done(self):
        if self._actualState in self._lastStatesNames:
            if self._firsttime is True:
                # The first time "done" is called while in a final state, return False
                # The next time, return True
                self._firsttime = False
                return False
            else:
                return True
        else:
            return False

    def _transitionTo(self, newState):
        try:
            b = self._states[self._actualState]
            b.onEnd()
        except KeyError:
            pass
        self._actualState = newState
        try:
            b = self._states[self._actualState]
            b.onStart()
        except KeyError:
            pass

    def _process(self):
        if (self._actualState is None):
            self._transitionTo(self._firstStateName)
        #msg = self._receive(False)
        b = self._states[self._actualState]
        #if msg: buede .postMessage(msg)
        self._lastexitcode = b._process()
        if (b.done() or b._forceKill.isSet()):
            if not self._lastexitcode:
                self._lastexitcode = b.exitCode()
            self._transitionTo(self._transitions[b._stateName][self._lastexitcode])
            self._lastexitcode = None

    def getCurrentState(self):
        return self._states[self._actualState]


class EventBehaviour(OneShotBehaviour):
    """
    A behaviour that is executed in response to a certain event.
    The 'onetime' parameter in the constructor represents the
    re-usability of the behaviour. By default, an Event behaviour is
    re-instanced (and re-launched) every time a new event that matches
    the template arrives. This can be changed by setting 'onetime'
    to True, which renders the behaviour for one use only
    """
    def __init__(self, onetime=False):
        OneShotBehaviour.__init__(self)
        self.onetime = onetime


if __name__ == "__main__":
    class TestBehaviour(PeriodicBehaviour):
        def __init__(self, time):
            PeriodicBehaviour.__init__(self, time)

        def _onTick(self):
            print "Tick: " + str(time.time())

    a = TestBehaviour(5)
    a.start()
