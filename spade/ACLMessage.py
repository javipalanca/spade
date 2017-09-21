# -*- coding: utf-8 -*-
import random
import string
import pickle

from .utils import deprecated
from . import content
from . import AID
from .ACLParser import ACLxmlParser
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

    cid_base = str(
        "".join([string.ascii_letters[int(random.randint(0, len(string.ascii_letters) - 1))] for a in range(4)]))
    cid_autocount = 0

    def __init__(self, performative=None, jsonstring=None):
        self._attrs = {}
        # possible FIPA communicative acts
        self.commacts = ['accept-proposal', 'agree', 'cancel',
                         'cfp', 'call-for-proposal', 'confirm', 'disconfirm',
                         'failure', 'inform', 'not-understood',
                         'propose', 'query-if', 'query-ref',
                         'refuse', 'reject-proposal', 'request',
                         'request-when', 'request-whenever', 'subscribe',
                         'inform-if', 'proxy', 'propagate']

        if performative:
            self._attrs["performative"] = performative.lower()
            # we do not check if is a fipa performative
            # any string is valid...
            # (performative.lower() in self.commacts):

        self.sender = None
        self.receivers = []
        self.content = None

        self._attrs["acl_representation"] = FIPA_ACL_REP_XML

        self._attrs['id'] = str(uuid.uuid4()).replace("-", "")

        if jsonstring:
            self.read_json(jsonstring)

    def reset(self):
        """
        resets the object
        its structures are set to its initial value
        """
        self.__init__()

    def set_sender(self, sender):
        """
        set the sender (AID class)
        """
        self.sender = sender

    setSender = deprecated(set_sender, "setSender")

    def get_sender(self):
        """
        returns the sender (AID class)
        """
        return self.sender

    getSender = deprecated(get_sender, "getSender")

    def add_receiver(self, recv):
        """
        adds a receiver to the list (AID class)
        """
        self.receivers.append(recv)

    addReceiver = deprecated(add_receiver, "addReceiver")

    def remove_receiver(self, recv):
        """
        removes a receiver from the list (AID class)
        """
        if recv in self.receivers:
            self.receivers.remove(recv)

    removeReceiver = deprecated(remove_receiver, "removeReceiver")

    def reset_receivers(self):
        """
        clears the list of receivers
        """
        self.receivers = []

    resetReceivers = deprecated(reset_receivers, "resetReceivers")

    def get_receivers(self):
        """
        returns the list of reveivers
        """
        return self.receivers

    getReceivers = deprecated(get_receivers, "getReceivers")

    def add_reply_to(self, re):
        """
        adds a 'reply to' to the list (AID class)
        """
        if isinstance(re, AID.aid):
            # self.reply_to.append(re)
            if 'reply_to' in self._attrs:
                self._attrs['reply_to'].append(re)
            else:
                self._attrs['reply_to'] = [re]

    addReplyTo = deprecated(add_reply_to, "addReplyTo")

    def remove_reply_to(self, re):
        """
        removes a 'reply to' from the list (AID class)
        """
        try:
            self._attrs["reply_to"].remove(re)
        except:
            return False

        return True

    removeReplyTo = deprecated(remove_reply_to, "removeReplyTo")

    def get_reply_to(self):
        """
        returns a 'reply to' from the list (AID class)
        """
        try:
            return str(self._attrs["reply_to"])
        except:
            return []

    getReplyTo = deprecated(get_reply_to, "getReplyTo")

    def set_performative(self, p):
        """
        sets the message performative (string)
        must be in ACLMessage.commacts
        """
        # we do not check if is a fipa performative
        # any string is valid...
        # if p and (p.lower() in self.commacts):
        self._attrs["performative"] = p.lower()

    setPerformative = deprecated(set_performative, "setPerformative")

    def get_performative(self):
        """
        returns the message performative (string)
        """
        try:
            return str(self._attrs["performative"])
        except:
            return None

    getPerformative = deprecated(get_performative, "getPerformative")

    def set_content(self, c):
        """
        sets the message content (string, bytestream, ...)
        """
        self.content = str(c)

    setContent = deprecated(set_content, "setContent")

    def set_content_object(self, co):
        """
        sets the message content in ContentObject format
        """
        self.content = co

    setContentObject = deprecated(set_content_object, "setContentObject")

    def get_content(self):
        """
        returns the message content
        """
        try:
            return self.content.asRDFXML()
        except:
            return str(self.content)

    getContent = deprecated(get_content, "getContent")

    def get_content_object(self):
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

    getContentObject = deprecated(get_content_object, "getContentObject")

    def set_reply_with(self, rw):
        self._attrs["reply_with"] = str(rw)

    setReplyWith = deprecated(set_reply_with, "setReplyWith")

    def get_reply_with(self):
        try:
            return str(self._attrs["reply_with"])
        except:
            return None

    getReplyWith = deprecated(get_reply_with, "getReplyWith")

    def set_in_reply_to(self, reply):
        self._attrs["in_reply_to"] = str(reply)

    setInReplyTo = deprecated(set_in_reply_to, "setInReplyTo")

    def get_in_reply_to(self):
        try:
            return str(self._attrs["in_reply_to"])
        except:
            return None

    getInReplyTo = deprecated(get_in_reply_to, "getInReplyTo")

    def set_encoding(self, e):
        self._attrs["encoding"] = str(e)

    setEncoding = deprecated(set_encoding, "setEncoding")

    def get_encoding(self):
        try:
            return str(self._attrs["encoding"])
        except:
            return None

    getEncoding = deprecated(get_encoding, "getEncoding")

    def set_language(self, e):
        self._attrs["language"] = str(e)

    setLanguage = deprecated(set_language, "setLanguage")

    def get_language(self):
        try:
            return str(self._attrs["language"])
        except:
            return None

    getLanguage = deprecated(get_language, "getLanguage")

    def set_acl_representation(self, e):
        self._attrs["acl_representation"] = str(e)

    setAclRepresentation = deprecated(set_acl_representation, "setAclRepresentation")

    def get_acl_representation(self):
        try:
            return str(self._attrs["acl_representation"])
        except:
            return None

    getAclRepresentation = deprecated(get_acl_representation, "getAclRepresentation")

    def set_ontology(self, e):
        self._attrs["ontology"] = str(e)

    setOntology = deprecated(set_ontology, "setOntology")

    def get_ontology(self):
        try:
            return str(self._attrs["ontology"])
        except:
            return None

    getOntology = deprecated(get_ontology, "getOntology")

    def set_reply_by(self, e):
        self._attrs["reply_by"] = str(e)

    setReplyBy = deprecated(set_reply_by, "setReplyBy")

    def get_reply_by(self):
        try:
            return str(self._attrs["reply_by"])
        except:
            return None

    getReplyBy = deprecated(get_reply_by, "getReplyBy")

    def set_protocol(self, e):
        self._attrs["protocol"] = str(e)

    setProtocol = deprecated(set_protocol, "setProtocol")

    def get_protocol(self):
        try:
            return str(self._attrs["protocol"])
        except:
            return None

    getProtocol = deprecated(get_protocol, "getProtocol")

    def set_conversation_id(self, e):
        self._attrs["id"] = str(e)

    setConversationId = deprecated(set_conversation_id, "setConversationId")

    def get_conversation_id(self):
        try:
            return str(self._attrs["id"])
        except:
            return None

    getConversationId = deprecated(get_conversation_id, "getConversationId")

    def create_reply(self):
        """
        Creates a reply for the message
        Duplicates all the message structures
        exchanges the 'from' AID with the 'to' AID
        """

        m = ACLMessage()

        m.set_performative(self.get_performative())
        if self.get_language():
            m.set_language(self.get_language())
        if self.get_ontology():
            m.set_ontology(self.get_ontology())
        if self.get_protocol():
            m.set_protocol(self.get_protocol())
        if self.get_conversation_id():
            m.set_conversation_id(self.get_conversation_id())

        for i in self.get_reply_to():
            m.add_receiver(i)

        if not self.get_reply_to():
            m.add_receiver(self.sender)

        if self.get_reply_with():
            m.set_in_reply_to(self.get_reply_with())

        return m

    createReply = deprecated(create_reply, "createReply")

    def __str__(self):
        if self.get_acl_representation() == FIPA_ACL_REP_JSON:
            return self.asJSON()
        elif self.get_acl_representation() == FIPA_ACL_REP_STRING:
            return self.asString()
        elif self.get_acl_representation() == FIPA_ACL_REP_XML:
            return self.asXML()
        else:
            return self.asXML()

    def to_xml(self):
        p = ACLxmlParser()
        return p.encode_xml(self)

    asXML = deprecated(to_xml, "asXML")

    def to_string(self):
        """
        returns a printable version of the message in ACL string representation
        """

        p = '('

        p = p + str(self.get_performative()) + '\n'
        if self.sender:
            p = p + ":sender " + str(self.sender) + "\n"

        if self.receivers:
            p = p + ":receiver\n (set\n"
            for i in self.receivers:
                p = p + str(i) + '\n'

            p = p + ")\n"
        if self.content:
            p = p + ':content "' + str(self.content) + '"\n'

        if self.get_reply_with():
            p = p + ":reply-with " + self.get_reply_with() + '\n'

        if self.get_reply_by():
            p = p + ":reply-by " + self.get_reply_by() + '\n'

        if self.get_in_reply_to():
            p = p + ":in-reply-to " + self.get_in_reply_to() + '\n'

        if self.get_reply_to():
            p = p + ":reply-to \n" + '(set\n'
            for i in self.get_reply_to():
                p = p + i + '\n'
            p = p + ")\n"

        if self.get_language():
            p = p + ":language " + self.get_language() + '\n'

        if self.get_encoding():
            p = p + ":encoding " + self.get_encoding() + '\n'

        if self.get_ontology():
            p = p + ":ontology " + self.get_ontology() + '\n'

        if self.get_protocol():
            p = p + ":protocol " + self.get_protocol() + '\n'

        if self.get_conversation_id():
            p = p + ":conversation-id " + self.get_conversation_id() + '\n'

        p = p + ")\n"

        return p

    asString = deprecated(to_string, "asString")

    def serialize(self):
        """
        returns a serialized version of the message
        """
        return pickle.dumps(self)

    def to_html(self):
        """
        returns an HTML version of the message ready to be displayed at the WUI
        """
        s = '<table class="servicesT" cellspacing="0">'
        s += '<tr><td class="servHd">Performative</td><td class="servBodL">' + self.getPerformative() + '</td></tr>'
        if self.sender:
            sndr = self.sender.to_xml()
            sndr = sndr.replace(">", "&gt;")
            sndr = sndr.replace("<", "&lt;")
            sndr = sndr.replace('"', "&quot;")
            s += '<tr><td class="servHd">Sender</td><td class="servBodL"><pre>' + sndr + '</pre></td></tr>'
        recvs = ""
        for r in self.receivers:
            escaped = r.to_xml()
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
        if self.get_reply_with():
            s += '<tr><td class="servHd">Reply With</td><td class="servBodL">' + str(self.get_reply_with()) + '</td></tr>'
        if self.get_reply_by():
            s += '<tr><td class="servHd">Reply By</td><td class="servBodL">' + str(self.get_reply_by()) + '</td></tr>'
        if self.get_in_reply_to():
            s += '<tr><td class="servHd">In Reply To</td><td class="servBodL">' + str(
                self.get_in_reply_to()) + '</td></tr>'
        if self.get_reply_to():
            s += '<tr><td class="servHd">Reply To</td><td class="servBodL">' + str(self.get_reply_to()) + '</td></tr>'
        if self.get_language():
            s += '<tr><td class="servHd">Language</td><td class="servBodL">' + str(self.get_language()) + '</td></tr>'
        if self.get_encoding():
            s += '<tr><td class="servHd">Encoding</td><td class="servBodL">' + str(self.get_encoding()) + '</td></tr>'
        if self.get_ontology():
            s += '<tr><td class="servHd">Ontology</td><td class="servBodL">' + str(self.get_ontology()) + '</td></tr>'
        if self.get_protocol():
            s += '<tr><td class="servHd">Protocol</td><td class="servBodL">' + str(self.get_protocol()) + '</td></tr>'
        if self.get_conversation_id():
            s += '<tr><td class="servHd">Conversation ID</td><td class="servBodL">' + str(
                self.get_conversation_id()) + '</td></tr>'
        s += '</table>'
        return s

    asHTML = deprecated(to_html, "asHTML")

    def to_json(self):
        """
        returns a JSON version of the message
        """
        p = "{"

        p += '"performative":"' + str(self.get_performative()) + '",'

        if self.sender:
            p += '"sender":' + self.sender.to_json() + ","

        if self.receivers:
            p += '"receivers":['
            for i in self.receivers:
                p += i.to_json() + ","
            if p[-1:] == ",":
                p = p[:-1]
            p += "],"

        if self.content:
            p = p + '"content":"' + str(self.content) + '",'

        if self.get_reply_with():
            p = p + '"reply-with":"' + str(self.get_reply_with()) + '",'

        if self.get_reply_by():
            p = p + '"reply-by":"' + self.get_reply_by() + '",'

        if self.get_in_reply_to():
            p = p + '"in-reply-to":"' + self.get_in_reply_to() + '",'

        if self.get_reply_to():
            p = p + '"reply-to":['
            for i in self.get_reply_to():
                p = p + i.to_json() + ","
            if p[-1:] == ",":
                p = p[:-1]
            p += "],"

        if self.get_language():
            p = p + '"language":"' + self.get_language() + '",'

        if self.get_encoding():
            p = p + '"encoding":"' + self.get_encoding() + '",'

        if self.get_ontology():
            p = p + '"ontology":"' + self.get_ontology() + '",'

        if self.get_protocol():
            p = p + '"protocol":"' + self.get_protocol() + '",'

        if self.get_conversation_id():
            p = p + '"conversation-id":"' + self.get_conversation_id() + '",'

        if p[-1:] == ",":
            p = p[:-1]
        p = p + "}"

        return p

    asJSON = deprecated(to_json, "asJSON")

    def read_json(self, jsonstring):
        """
        loads a JSON string in the message
        """
        p = json.loads(jsonstring)

        if "performative" in p:
            self.set_performative(p["performative"])

        if "sender" in p:
            s = AID.aid()
            s.read_json(p["sender"])
            self.set_sender(s)

        if "receivers" in p:
            for i in p["receivers"]:
                s = AID.aid()
                s.read_json(i)
                self.add_receiver(s)

        if "content" in p:
            self.set_content(p["content"])

        if "reply-with" in p:
            self.set_reply_with(p["reply-with"])

        if "reply-by" in p:
            self.set_reply_by(p["reply-by"])

        if "in-reply-to" in p:
            self.set_in_reply_to(p["in-reply-to"])

        if "reply-to" in p:
            for i in p["reply-to"]:
                s = AID.aid()
            s.read_json(i)
            self.add_reply_to(s)

        if "language" in p:
            self.set_language(p["language"])

        if "encoding" in p:
            self.set_encoding(p["encoding"])

        if "ontology" in p:
            self.set_ontology(p['ontology'])

        if "protocol" in p:
            self.set_protocol(p['protocol'])

        if "conversation-id" in p:
            self.set_conversation_id(p["conversation-id"])

    loadJSON = deprecated(read_json, "loadJSON")