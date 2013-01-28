# -*- coding: utf-8 -*-
import types
import AID
try:
    import json
except ImportError:
    import simplejson as json 


class Envelope:
    """
    FIPA envelope
    """
    def __init__(self, to=None, _from=None, comments=None, aclRepresentation=None, payloadLength=None, payloadEncoding=None, date=None, encrypted=None, intendedReceiver=None, received=None, transportBehaviour=None, userDefinedProperties=None, jsonstring=None):

        self.to = list()
        if to is not None:
            for i in to:
                if isinstance(i, AID.aid):
                    self.to.append(i)  # aid
        self._from = None
        if _from is not None and isinstance(_from, AID.aid):
            self._from = _from  # aid

        if comments is not None:
            self.comments = comments  # str
        else:
            self.comments = None
        if aclRepresentation is not None:
            self.aclRepresentation = aclRepresentation  # str
        else:
            self.aclRepresentation = None
        if payloadLength is not None:
            self.payloadLength = payloadLength  # int
        else:
            self.payloadLength = None
        if payloadEncoding is not None:
            self.payloadEncoding = payloadEncoding  # str
        else:
            self.payloadEncoding = None
        if date is not None:
            self.date = date  # list(datetime)
        else:
            self.date = None
        if encrypted is not None:
            self.encrypted = encrypted  # list(str)
        else:
            self.encrypted = list()
        if intendedReceiver is not None:
            self.intendedReceiver = intendedReceiver  # list(aid)
        else:
            self.intendedReceiver = list()
        if received is not None:
            self.received = received  # list(ReceivedObject)
        else:
            self.received = None
        if transportBehaviour is not None:
            self.transportBehaviour = transportBehaviour  # list(?)
        else:
            self.transportBehaviour = list()
        if userDefinedProperties is not None:
            self.userDefinedProperties = userDefinedProperties  # list(properties)
        else:
            self.userDefinedProperties = list()

        if jsonstring:
            self.loadJSON(jsonstring)

    def getTo(self):
        return self.to

    def addTo(self, to):
        self.to.append(to)
        self.addIntendedReceiver(to)

    def getFrom(self):
        return self._from

    def setFrom(self, _from):
        self._from = _from

    def getComments(self):
        return self.comments

    def setComments(self, comments):
        self.comments = comments

    def getAclRepresentation(self):
        return self.aclRepresentation

    def setAclRepresentation(self, acl):
        self.aclRepresentation = acl

    def getPayloadLength(self):
        return self.payloadLength

    def setPayloadLength(self, pl):
        self.payloadLength = pl

    def getPayloadEncoding(self):
        return self.payloadEncoding

    def setPayloadEncoding(self, pe):
        self.payloadEncoding = pe

    def getDate(self):
        return self.date

    def setDate(self, date):
        self.date = date

    def getEncryted(self):
        return self.encrypted

    def setEncryted(self, encrypted):
        self.encrypted = encrypted

    def getIntendedReceiver(self):
        return self.intendedReceiver

    def addIntendedReceiver(self, intended):
        if not intended in self.intendedReceiver:
            self.intendedReceiver.append(intended)

    def getReceived(self):
        return self.received

    def setReceived(self, received):
        self.received = received

    def __str__(self):
        return self.asXML()

    def asXML(self):
        """
        returns a printable version of the envelope in XML
        """
        r = '<?xml version="1.0"?>' + "\n"
        r = r + "\t\t<envelope> \n"
        r = r + '\t\t\t<params index="1">' + "\n"
        r = r + "\t\t\t\t<to>\n"
        for aid in self.to:
            r = r + "\t\t\t\t\t<agent-identifier> \n"
            r = r + "\t\t\t\t\t\t<name>" + aid.getName() + "</name> \n"
            r = r + "\t\t\t\t\t\t<addresses>\n"
            for addr in aid.getAddresses():
                r = r + "\t\t\t\t\t\t\t<url>" + addr + "</url>\n"
            r = r + "\t\t\t\t\t\t</addresses> \n"
            r = r + "\t\t\t\t\t</agent-identifier>\n"
        r = r + "\t\t\t\t</to> \n"
        if self._from:
            r = r + "\t\t\t\t<from> \n"
            r = r + "\t\t\t\t\t<agent-identifier> \n"
            r = r + "\t\t\t\t\t\t<name>" + self._from.getName() + "</name> \n"
            r = r + "\t\t\t\t\t\t<addresses>\n"
            for addr in self._from.getAddresses():
                r = r + "\t\t\t\t\t\t\t<url>" + addr + "</url>\n"
            r = r + "\t\t\t\t\t\t</addresses> \n"
            r = r + "\t\t\t\t\t</agent-identifier> \n"
            r = r + "\t\t\t\t</from>\n"
        if self.aclRepresentation:
            r = r + "\t\t\t\t<acl-representation>" + self.aclRepresentation + "</acl-representation>\n"
        if self.payloadLength:
            r = r + "\t\t\t\t<payload-length>" + str(self.payloadLength) + "</payload-length>\n"
        if self.payloadEncoding:
            r = r + "\t\t\t\t<payload-encoding>" + self.payloadEncoding + "</payload-encoding>\n"
        if self.date:
            r = r + "\t\t\t\t<date>" + str(self.date) + "</date>\n"
        if self.intendedReceiver:
            r = r + "\t\t\t\t<intended-receiver>\n"
            for aid in self.intendedReceiver:
                r = r + "\t\t\t\t\t<agent-identifier> \n"
                r = r + "\t\t\t\t\t\t<name>" + aid.getName() + "</name> \n"
                r = r + "\t\t\t\t\t\t<addresses>\n"
                for addr in aid.getAddresses():
                    r = r + "\t\t\t\t\t\t\t<url>" + addr + "</url>\n"
                r = r + "\t\t\t\t\t\t</addresses> \n"
                r = r + "\t\t\t\t\t</agent-identifier>\n"
            r = r + "\t\t\t\t</intended-receiver> \n"
        if self.received:
            r = r + "\t\t\t\t<received>\n"
            if self.received.getBy():
                r = r + '\t\t\t\t\t<received-by value="' + self.received.getBy() + '"/>\n'
            if self.received.getDate():
                r = r + '\t\t\t\t\t<received-date value="' + str(self.received.getDate()) + '"/>\n'
            if self.received.getId():
                r = r + '\t\t\t\t\t<received-id value="' + self.received.getId() + '"/>\n'
            r = r + "\t\t\t\t</received>\n"

        r = r + "\t\t\t</params> \n"
        r = r + "\t\t</envelope>\n"

        return r

    def asJSON(self):
        """
        returns a printable version of the envelope in JSON
        """
        r = "{"
        r = r + '"to":['
        for aid in self.to:
            r = r + '{'
            r = r + '"name":"' + aid.getName() + '",'
            r = r + '"addresses":['
            for addr in aid.getAddresses():
                r = r + '"' + addr + '",'
            if r[-1:] == ",": r = r[:-1]
            r = r + "]"
            r = r + "},"
        if r[-1:] == ",": r = r[:-1]
        r = r + "],"
        if self._from:
            r = r + '"from":{'
            r = r + '"name":"' + self._from.getName() + '",'
            r = r + '"addresses":['
            for addr in self._from.getAddresses():
                r = r + '"' + addr + '",'
            if r[-1:] == ",": r = r[:-1]
            r = r + "]},"
        if self.aclRepresentation:
            r = r + '"acl-representation":"' + self.aclRepresentation + '",'
        if self.payloadLength:
            r = r + '"payload-length":"' + str(self.payloadLength) + '",'
        if self.payloadEncoding:
            r = r + '"payload-encoding":"' + self.payloadEncoding + '",'
        if self.date:
            r = r + '"date":"' + str(self.date) + '",'
        if self.intendedReceiver:
            r = r + '"intended-receiver":['
            for aid in self.intendedReceiver:
                r = r + "{"
                r = r + '"name":"' + aid.getName() + '",'
                r = r + '"addresses":['
                for addr in aid.getAddresses():
                    r = r + '"' + addr + '",'
                if r[-1:] == ",": r = r[:-1]
                r = r + "],"
                if r[-1:] == ",": r = r[:-1]
                r = r + "},"
            if r[-1:] == ",": r = r[:-1]
            r = r + "],"
        if self.received:
            r = r + '"received":{'
            if self.received.getBy():
                r = r + '"received-by":"' + self.received.getBy() + '",'
            if self.received.getDate():
                r = r + '"received-date":"' + str(self.received.getDate()) + '",'
            if self.received.getId():
                r = r + '"received-id":"' + self.received.getId() + '"'
            if r[-1:] == ",": r = r[:-1]
            r = r + "}"

        if r[-1:] == ",": r = r[:-1]
        r = r + "}"

        return r

    def loadJSON(self, jsonstring):
        """
        loads a JSON string in the envelope
        """
        r = json.loads(jsonstring)

        if "to" in r:
            for a in r["to"]:
                aid = AID.aid()
                aid.setName(a["name"])
                for addr in a["addresses"]:
                    aid.addAddress(addr)
                self.addTo(aid)
        if "from" in r:
            aid = AID.aid()
            aid.setName(r["from"]["name"])
            for addr in r["from"]["addresses"]:
                aid.addAddress(addr)
            self.setFrom(aid)

        if "acl-representation" in r:
            self.setAclRepresentation(r["acl-representation"])
        if "payload-length" in r:
            self.setPayloadLength(r["payload-length"])
        if "payload-encoding" in r:
            self.setPayloadEncoding(r["payload-encoding"])
        if "date" in r:
            self.setDate(r["date"])
        if "intended-receiver" in r:
            for ag in r["intended-receiver"]:
                aid = AID.aid()
                aid.setName(ag["name"])
                for addr in ag["addresses"]:
                    aid.addAddress(addr)
                self.addIntendedReceiver(aid)
