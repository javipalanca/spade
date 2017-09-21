# -*- coding: utf-8 -*-
from . import AID

try:
    import json
except ImportError:
    import simplejson as json


class Envelope:
    """
    FIPA envelope
    """

    def __init__(self, to=None, _from=None, comments=None, acl_representation=None, payload_length=None,
                 payload_encoding=None, date=None, encrypted=None, intended_receiver=None, received=None,
                 transport_behaviour=None, user_defined_properties=None, jsonstring=None):

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
        if acl_representation is not None:
            self.acl_representation = acl_representation  # str
        else:
            self.acl_representation = None
        if payload_length is not None:
            self.payload_length = payload_length  # int
        else:
            self.payload_length = None
        if payload_encoding is not None:
            self.payload_encoding = payload_encoding  # str
        else:
            self.payload_encoding = None
        if date is not None:
            self.date = date  # list(datetime)
        else:
            self.date = None
        if encrypted is not None:
            self.encrypted = encrypted  # list(str)
        else:
            self.encrypted = list()
        if intended_receiver is not None:
            self.intended_receiver = intended_receiver  # list(aid)
        else:
            self.intended_receiver = list()
        if received is not None:
            self.received = received  # list(ReceivedObject)
        else:
            self.received = None
        if transport_behaviour is not None:
            self.transport_behaviour = transport_behaviour  # list(?)
        else:
            self.transport_behaviour = list()
        if user_defined_properties is not None:
            self.user_defined_properties = user_defined_properties  # list(properties)
        else:
            self.user_defined_properties = list()

        if jsonstring:
            self.read_json(jsonstring)

    def get_to(self):
        return self.to

    def add_to(self, to):
        self.to.append(to)
        self.add_intended_receiver(to)

    def get_from(self):
        return self._from

    def set_from(self, _from):
        self._from = _from

    def get_comments(self):
        return self.comments

    def set_comments(self, comments):
        self.comments = comments

    def get_acl_representation(self):
        return self.acl_representation

    def set_acl_representation(self, acl):
        self.acl_representation = acl

    def get_payload_length(self):
        return self.payload_length

    def set_payload_length(self, pl):
        self.payload_length = pl

    def get_payload_encoding(self):
        return self.payload_encoding

    def set_payload_encoding(self, pe):
        self.payload_encoding = pe

    def get_date(self):
        return self.date

    def set_date(self, date):
        self.date = date

    def get_encryted(self):
        return self.encrypted

    def set_encryted(self, encrypted):
        self.encrypted = encrypted

    def get_intended_receiver(self):
        return self.intended_receiver

    def add_intended_receiver(self, intended):
        if intended not in self.intended_receiver:
            self.intended_receiver.append(intended)

    def get_received(self):
        return self.received

    def set_received(self, received):
        self.received = received

    def __str__(self):
        return self.to_xml()

    def to_xml(self):
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
        if self.acl_representation:
            r = r + "\t\t\t\t<acl-representation>" + self.acl_representation + "</acl-representation>\n"
        if self.payload_length:
            r = r + "\t\t\t\t<payload-length>" + str(self.payload_length) + "</payload-length>\n"
        if self.payload_encoding:
            r = r + "\t\t\t\t<payload-encoding>" + self.payload_encoding + "</payload-encoding>\n"
        if self.date:
            r = r + "\t\t\t\t<date>" + str(self.date) + "</date>\n"
        if self.intended_receiver:
            r = r + "\t\t\t\t<intended-receiver>\n"
            for aid in self.intended_receiver:
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

    def to_json(self):
        """
        returns a printable version of the envelope in JSON
        """
        r = "{"
        r = r + '"to":['
        for aid in self.to:
            r = r + '{'
            r = r + '"name":"' + aid.get_name() + '",'
            r = r + '"addresses":['
            for addr in aid.get_addresses():
                r = r + '"' + addr + '",'
            if r[-1:] == ",":
                r = r[:-1]
            r = r + "]"
            r = r + "},"
        if r[-1:] == ",":
            r = r[:-1]
        r = r + "],"
        if self._from:
            r = r + '"from":{'
            r = r + '"name":"' + self._from.get_name() + '",'
            r = r + '"addresses":['
            for addr in self._from.get_addresses():
                r = r + '"' + addr + '",'
            if r[-1:] == ",":
                r = r[:-1]
            r = r + "]},"
        if self.acl_representation:
            r = r + '"acl-representation":"' + self.acl_representation + '",'
        if self.payload_length:
            r = r + '"payload-length":"' + str(self.payload_length) + '",'
        if self.payload_encoding:
            r = r + '"payload-encoding":"' + self.payload_encoding + '",'
        if self.date:
            r = r + '"date":"' + str(self.date) + '",'
        if self.intended_receiver:
            r = r + '"intended-receiver":['
            for aid in self.intended_receiver:
                r = r + "{"
                r = r + '"name":"' + aid.get_name() + '",'
                r = r + '"addresses":['
                for addr in aid.get_addresses():
                    r = r + '"' + addr + '",'
                if r[-1:] == ",":
                    r = r[:-1]
                r = r + "],"
                if r[-1:] == ",":
                    r = r[:-1]
                r = r + "},"
            if r[-1:] == ",":
                r = r[:-1]
            r = r + "],"
        if self.received:
            r = r + '"received":{'
            if self.received.getBy():
                r = r + '"received-by":"' + self.received.get_by() + '",'
            if self.received.getDate():
                r = r + '"received-date":"' + str(self.received.get_date()) + '",'
            if self.received.getId():
                r = r + '"received-id":"' + self.received.get_id() + '"'
            if r[-1:] == ",":
                r = r[:-1]
            r = r + "}"

        if r[-1:] == ",":
            r = r[:-1]
        r = r + "}"

        return r

    def read_json(self, jsonstring):
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
                self.add_to(aid)
        if "from" in r:
            aid = AID.aid()
            aid.setName(r["from"]["name"])
            for addr in r["from"]["addresses"]:
                aid.add_address(addr)
            self.set_from(aid)

        if "acl-representation" in r:
            self.set_acl_representation(r["acl-representation"])
        if "payload-length" in r:
            self.set_payload_length(r["payload-length"])
        if "payload-encoding" in r:
            self.set_payload_encoding(r["payload-encoding"])
        if "date" in r:
            self.set_date(r["date"])
        if "intended-receiver" in r:
            for ag in r["intended-receiver"]:
                aid = AID.aid()
                aid.setName(ag["name"])
                for addr in ag["addresses"]:
                    aid.addAddress(addr)
                self.add_intended_receiver(aid)
