# -*- coding: utf-8 -*-
import AID
import random
import string
import cPickle as pickle
import content
from ACLParser import ACLxmlParser
import xml
import uuid
import json

FIPA_ACL_REP_STRING = "fipa.acl.rep.string.std"
FIPA_ACL_REP_JSON = "fipa.acl.rep.json.std"
FIPA_ACL_REP_XML = "fipa.acl.rep.xml.std"


class ACLMessage:
    """
    ACLMessage class stores a message using the ACL language
    """
    ACCEPT_PROPOSAL = 'accept-proposal'
    AGREE = 'agree'
    CANCEL = 'cancel'
    CFP = 'cfp'
    CALL_FOR_PROPOSAL = 'call-for-proposal'
    CONFIRM = 'confirm'
    DISCONFIRM = 'disconfirm'
    FAILURE = 'failure'
    INFORM = 'inform'
    NOT_UNDERSTOOD = 'not-understood'
    PROPOSE = 'propose'
    QUERY_IF = 'query-if'
    QUERY_REF = 'query-ref'
    REFUSE = 'refuse'
    REJECT_PROPOSAL = 'reject-proposal'
    REQUEST = 'request'
    REQUEST_WHEN = 'request-when'
    REQUEST_WHENEVER = 'request-whenever'
    SUBSCRIBE = 'subscribe'
    INFORM_IF = 'inform-if'
    PROXY = 'proxy'
    PROPAGATE = 'propagate'

    cid_base = str("".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(4)]))
    cid_autocount = 0

    def __init__(self, performative=None, jsonstring=None):
        self._attrs = {}
        #possible FIPA communicative acts
        self.commacts = ['accept-proposal', 'agree', 'cancel',
                         'cfp', 'call-for-proposal', 'confirm', 'disconfirm',
                         'failure', 'inform', 'not-understood',
                         'propose', 'query-if', 'query-ref',
                         'refuse', 'reject-proposal', 'request',
                         'request-when', 'request-whenever', 'subscribe',
                         'inform-if', 'proxy', 'propagate']

        """
        if performative and (performative.lower() in self.commacts):
            self.performative = performative.lower()
        else: self.performative = None
        """
        if performative:
            self._attrs["performative"] = performative.lower()
             # we do not check if is a fipa performative
             # any string is valid...
             # (performative.lower() in self.commacts):

        self.sender = None
        self.receivers = []
        self.content = None

        self._attrs["acl_representation"] = FIPA_ACL_REP_XML

        #self._attrs['id'] = str(ACLMessage.cid_base + str(ACLMessage.cid_autocount))
        #ACLMessage.cid_autocount += 1
        self._attrs['id'] = str(uuid.uuid4()).replace("-", "")

        #self.userDefProps = None

        if jsonstring:
            self.loadJSON(jsonstring)

    def reset(self):
        """
        resets the object
        its structures are set to its initial value
        """
        self.__init__()

    def setSender(self, sender):
        """
        set the sender (AID class)
        """
        self.sender = sender

    def getSender(self):
        """
        returns the sender (AID class)
        """
        return self.sender

    def addReceiver(self, recv):
        """
        adds a receiver to the list (AID class)
        """
        self.receivers.append(recv)

    def removeReceiver(self, recv):
        """
        removes a receiver from the list (AID class)
        """
        if recv in self.receivers:
            self.receivers.remove(recv)

    def resetReceivers(self):
        """
        clears the list of receivers
        """
        self.receivers = []

    def getReceivers(self):
        """
        returns the list of reveivers
        """
        return self.receivers

    def addReplyTo(self, re):
        """
        adds a 'reply to' to the list (AID class)
        """
        if isinstance(re, AID.aid):
            #self.reply_to.append(re)
            if 'reply_to' in self._attrs:
                self._attrs['reply_to'].append(re)
            else:
                self._attrs['reply_to'] = [re]

    def removeReplyTo(self, re):
        """
        removes a 'reply to' from the list (AID class)
        """
        try:
            self._attrs["reply_to"].remove(re)
        except:
            return False

        return True

    def getReplyTo(self):
        """
        returns a 'reply to' from the list (AID class)
        """
        try:
            return str(self._attrs["reply_to"])
        except:
            return []

    def setPerformative(self, p):
        """
        sets the message performative (string)
        must be in ACLMessage.commacts
        """
        # we do not check if is a fipa performative
        # any string is valid...
        #if p and (p.lower() in self.commacts):
        self._attrs["performative"] = p.lower()

    def getPerformative(self):
        """
        returns the message performative (string)
        """
        try:
            return str(self._attrs["performative"])
        except:
            return None

    def setContent(self, c):
        """
        sets the message content (string, bytestream, ...)
        """
        self.content = str(c)

    def setContentObject(self, co):
        """
        sets the message content in ContentObject format
        """
        self.content = co

    def getContent(self):
        """
        returns the message content
        """
        try:
            return self.content.asRDFXML()
        except:
            return str(self.content)

    def getContentObject(self):
        """
        returns the message content in ContentObject format, if possible
        """
        if "str" in str(type(self.content)):
            try:
                return content.RDFXML2CO(self.content)
            except:
                return None
        elif "ContentObject" in str(type(self.content)):
            return self.content
        else:
            return None

    def setReplyWith(self, rw):
        self._attrs["reply_with"] = str(rw)
        #self.reply_with = rw

    def getReplyWith(self):
        try:
            return str(self._attrs["reply_with"])
        except:
            return None

    def setInReplyTo(self, reply):
        self._attrs["in_reply_to"] = str(reply)

    def getInReplyTo(self):
        try:
            return str(self._attrs["in_reply_to"])
        except:
            return None

    def setEncoding(self, e):
        self._attrs["encoding"] = str(e)

    def getEncoding(self):
        try:
            return str(self._attrs["encoding"])
        except:
            return None

    def setLanguage(self, e):
        self._attrs["language"] = str(e)

    def getLanguage(self):
        try:
            return str(self._attrs["language"])
        except:
            return None

    def setAclRepresentation(self, e):
        self._attrs["acl_representation"] = str(e)

    def getAclRepresentation(self):
        try:
            return str(self._attrs["acl_representation"])
        except:
            return None

    def setOntology(self, e):
        self._attrs["ontology"] = str(e)

    def getOntology(self):
        try:
            return str(self._attrs["ontology"])
        except:
            return None

    def setReplyBy(self, e):
        self._attrs["reply_by"] = str(e)

    def getReplyBy(self):
        try:
            return str(self._attrs["reply_by"])
        except:
            return None

    def setProtocol(self, e):
        self._attrs["protocol"] = str(e)

    def getProtocol(self):
        try:
            return str(self._attrs["protocol"])
        except:
            return None

    def setConversationId(self, e):
        self._attrs["id"] = str(e)

    def getConversationId(self):
        try:
            return str(self._attrs["id"])
        except:
            return None

    def createReply(self):
        """
        Creates a reply for the message
        Duplicates all the message structures
        exchanges the 'from' AID with the 'to' AID
        """

        m = ACLMessage()

        m.setPerformative(self.getPerformative())
        #m.setSender(None)
        #m.receivers = []
        #m.reply_to = []
        #m.setContent(None)
        #m.setReplyBy(None)
        #m.setEncoding(None)
        if self.getLanguage():
            m.setLanguage(self.getLanguage())
        if self.getOntology():
            m.setOntology(self.getOntology())
        if self.getProtocol():
            m.setProtocol(self.getProtocol())
        if self.getConversationId():
            m.setConversationId(self.getConversationId())

        for i in self.getReplyTo():
            m.addReceiver(i)

        if not self.getReplyTo():
            m.addReceiver(self.sender)

        if self.getReplyWith():
            m.setInReplyTo(self.getReplyWith())

        #if self.getReplyWith() != None:
        #	m.setConversationId(str(self.getReplyWith()))

        return m

    def __str__(self):
        if self.getAclRepresentation() == FIPA_ACL_REP_JSON:
            return self.asJSON()
        elif self.getAclRepresentation() == FIPA_ACL_REP_STRING:
            return self.asString()
        elif self.getAclRepresentation() == FIPA_ACL_REP_XML:
            return self.asXML()
        else:
            return self.asXML()

    def asXML(self):
        p = ACLxmlParser()
        return p.encodeXML(self)

    def asString(self):
        """
        returns a printable version of the message in ACL string representation
        """

        p = '('

        p = p + str(self.getPerformative()) + '\n'
        if self.sender:
            p = p + ":sender " + str(self.sender) + "\n"

        if self.receivers:
            p = p + ":receiver\n (set\n"
            for i in self.receivers:
                p = p + str(i) + '\n'

            p = p + ")\n"
        if self.content:
            p = p + ':content "' + str(self.content) + '"\n'

        if self.getReplyWith():
            p = p + ":reply-with " + self.getReplyWith() + '\n'

        if self.getReplyBy():
            p = p + ":reply-by " + self.getReplyBy() + '\n'

        if self.getInReplyTo():
            p = p + ":in-reply-to " + self.getInReplyTo() + '\n'

        if self.getReplyTo():
            p = p + ":reply-to \n" + '(set\n'
            for i in self.getReplyTo():
                p = p + i + '\n'
            p = p + ")\n"

        if self.getLanguage():
            p = p + ":language " + self.getLanguage() + '\n'

        if self.getEncoding():
            p = p + ":encoding " + self.getEncoding() + '\n'

        if self.getOntology():
            p = p + ":ontology " + self.getOntology() + '\n'

        if self.getProtocol():
            p = p + ":protocol " + self.getProtocol() + '\n'

        if self.getConversationId():
            p = p + ":conversation-id " + self.getConversationId() + '\n'

        p = p + ")\n"

        return p

    def serialize(self):
        """
        returns a serialized version of the message
        """
        return pickle.dumps(self)

    def asHTML(self):
        """
        returns an HTML version of the message ready to be displayed at the WUI
        """
        s = '<table class="servicesT" cellspacing="0">'
        s += '<tr><td class="servHd">Performative</td><td class="servBodL">' + self.getPerformative() + '</td></tr>'
        if self.sender:
            sndr = self.sender.asXML()
            sndr = sndr.replace(">", "&gt;")
            sndr = sndr.replace("<", "&lt;")
            sndr = sndr.replace('"', "&quot;")
            s += '<tr><td class="servHd">Sender</td><td class="servBodL"><pre>' + sndr + '</pre></td></tr>'
        recvs = ""
        for r in self.receivers:
            escaped = r.asXML()
            escaped = escaped.replace(">", "&gt;")
            escaped = escaped.replace("<", "&lt;")
            escaped = escaped.replace('"', "&quot;")
            recvs += escaped + "<br />"
        s += '<tr><td class="servHd">Receivers</td><td class="servBodL"><pre>' + recvs + '</pre></td></tr>'
        if self.content:
            cont = self.getContent()
            try:
                # Try to beautify the content if it is XML
                x = xml.dom.minidom.parseString(cont)
                cont = x.toprettyxml()
            except:
                pass
            cont = cont.replace(">", "&gt;")
            cont = cont.replace("<", "&lt;")
            cont = cont.replace('"', "&quot;")
            s += '<tr><td class="servHd">Content</td><td class="servBodL"><pre>' + cont + '</pre></td></tr>'
        if self.getReplyWith():
            s += '<tr><td class="servHd">Reply With</td><td class="servBodL">' + str(self.getReplyWith()) + '</td></tr>'
        if self.getReplyBy():
            s += '<tr><td class="servHd">Reply By</td><td class="servBodL">' + str(self.getReplyBy()) + '</td></tr>'
        if self.getInReplyTo():
            s += '<tr><td class="servHd">In Reply To</td><td class="servBodL">' + str(self.getInReplyTo()) + '</td></tr>'
        if self.getReplyTo():
            s += '<tr><td class="servHd">Reply To</td><td class="servBodL">' + str(self.getReplyTo()) + '</td></tr>'
        if self.getLanguage():
            s += '<tr><td class="servHd">Language</td><td class="servBodL">' + str(self.getLanguage()) + '</td></tr>'
        if self.getEncoding():
            s += '<tr><td class="servHd">Encoding</td><td class="servBodL">' + str(self.getEncoding()) + '</td></tr>'
        if self.getOntology():
            s += '<tr><td class="servHd">Ontology</td><td class="servBodL">' + str(self.getOntology()) + '</td></tr>'
        if self.getProtocol():
            s += '<tr><td class="servHd">Protocol</td><td class="servBodL">' + str(self.getProtocol()) + '</td></tr>'
        if self.getConversationId():
            s += '<tr><td class="servHd">Conversation ID</td><td class="servBodL">' + str(self.getConversationId()) + '</td></tr>'
        s += '</table>'
        return s

    def asJSON(self):
        """
        returns a JSON version of the message
        """
        p = "{"

        p += '"performative":"' + str(self.getPerformative()) + '",'

        if self.sender:
            p += '"sender":' + self.sender.asJSON() + ","

        if self.receivers:
            p += '"receivers":['
            for i in self.receivers:
                p += i.asJSON() + ","
            if p[-1:] == ",":
                p = p[:-1]
            p += "],"

        if self.content:
            p = p + '"content":"' + str(self.content) + '",'

        if self.getReplyWith():
            p = p + '"reply-with":"' + str(self.getReplyWith()) + '",'

        if self.getReplyBy():
            p = p + '"reply-by":"' + self.getReplyBy() + '",'

        if self.getInReplyTo():
            p = p + '"in-reply-to":"' + self.getInReplyTo() + '",'

        if self.getReplyTo():
            p = p + '"reply-to":['
            for i in self.getReplyTo():
                p = p + i.asJSON() + ","
            if p[-1:] == ",":
                p = p[:-1]
            p += "],"

        if self.getLanguage():
            p = p + '"language":"' + self.getLanguage() + '",'

        if self.getEncoding():
            p = p + '"encoding":"' + self.getEncoding() + '",'

        if self.getOntology():
            p = p + '"ontology":"' + self.getOntology() + '",'

        if self.getProtocol():
            p = p + '"protocol":"' + self.getProtocol() + '",'

        if self.getConversationId():
            p = p + '"conversation-id":"' + self.getConversationId() + '",'

        if p[-1:] == ",":
            p = p[:-1]
        p = p + "}"

        return p

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