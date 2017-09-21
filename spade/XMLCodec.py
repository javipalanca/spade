# -*- coding: utf-8 -*-
import xml.sax
from xml.sax import handler
from .BasicFipaDateTime import BasicFipaDateTime
from .AID import aid
from .ReceivedObject import ReceivedObject
from . import Envelope


class XMLCodec(handler.ContentHandler):
    """
    XML Parser
    """

    def __init__(self):

        super().__init__()
        self.ToTag = False
        self.aidTag = ""

        # Constants
        self.ENVELOPE_TAG = "envelope"
        self.PARAMS_TAG = "params"
        self.INDEX = "index"
        self.INDEX_ATTR = ' index="'
        self.TO_TAG = "to"
        self.AID_TAG = "agent-identifier"
        self.AID_NAME = "name"
        self.AID_ADDRESSES = "addresses"
        self.AID_ADDRESS = "url"
        self.FROM_TAG = "from"
        self.COMMENTS_TAG = "comments"
        self.REPRESENTATION_TAG = "acl-representation"
        self.LENGTH_TAG = "payload-length"
        self.ENCODING_TAG = "payload-encoding"
        self.DATE_TAG = "date"
        # self.ENCRYPTED_TAG = "encrypted"
        self.INTENDED_TAG = "intended-receiver"
        self.RECEIVED_TAG = "received"
        self.RECEIVED_DATE = "received-date"
        self.RECEIVED_BY = "received-by"
        self.RECEIVED_FROM = "received-from"
        self.RECEIVED_ID = "received-id"
        self.RECEIVED_VIA = "received-via"
        self.RECEIVED_ATTR = "value"
        self.PROP_TAG = "user-defined"
        self.PROP_ATTR = "href"
        self.PROP_ATTR_TYPE = "type"
        self.PROP_STRING_TYPE = "string"
        self.PROP_BYTE_TYPE = "byte-array"
        self.PROP_SER_TYPE = "serialized"
        self.OT = "<"
        self.ET = "</"
        self.CT = ">"
        self.NULL = ""

    #   ***************************************************
    #   *               Encoding methods                  *
    #   ***************************************************

    """ Encode the information of Agent, Tags To and From """

    def encode_aid(self, agentid):

        if not isinstance(agentid, aid):
            return ""

        sb = self.OT + self.AID_TAG + self.CT
        sb = sb + self.encode_tag(self.AID_NAME, agentid.get_name())
        sb = sb + self.OT + self.AID_ADDRESSES + self.CT

        addresses = agentid.get_addresses()
        for addr in addresses:
            sb = sb + self.encode_tag(self.AID_ADDRESS, addr)

        sb = sb + self.ET + self.AID_ADDRESSES + self.CT
        sb = sb + self.ET + self.AID_TAG + self.CT

        return sb

    """
      This does the following:
      < tag >
         content
      </ tag >
    """

    def encode_tag(self, tag, content):
        sb = self.OT + tag + self.CT
        sb = sb + content
        sb = sb + self.ET + tag + self.CT

        return sb

    """
    A user-defined property (String name, Object value) is encoded the following way:
    <user-defined href="name" type="type">value</user-defined>
    """

    def encode_oneline_tag(self, tag1, tag2, value):
        sb = self.OT + tag1 + " "
        sb = sb + tag2 + '="' + value + '"/>'

        return sb

    def encode_xml(self, env):
        """
        General Encoding of the envelope
        """

        # Create the message XML
        sb = self.OT + self.ENVELOPE_TAG + self.CT
        sb = sb + self.OT + self.PARAMS_TAG + self.INDEX_ATTR + "1" + '"' + self.CT

        # Create tag TO
        tos = env.get_to()
        for agentid in tos:
            sb = sb + self.OT + self.TO_TAG + self.CT
            sb = sb + self.encode_aid(agentid)
            sb = sb + self.ET + self.TO_TAG + self.CT

        # Create tag from
        if env.getFrom() is not None:
            sb = sb + self.OT + self.FROM_TAG + self.CT
            sb = sb + self.encode_aid(env.get_from())
            sb = sb + self.ET + self.FROM_TAG + self.CT

        # Create tag comments
        if env.get_comments() is not None and len(env.get_comments()) > 0:
            sb = sb + self.encode_tag(self.COMMENTS_TAG, env.get_comments())

        # Create tag acl-representation
        if env.get_acl_representation() is not None:
            sb = sb + self.encode_tag(self.REPRESENTATION_TAG, env.get_acl_representation())

            # Create tag payload-length
            if env.get_payload_length() is not None:
                sb = sb + self.encode_tag(self.LENGTH_TAG, str(env.get_payload_length()))

        # Create tag payload-encoding
        if env.get_payload_encoding() is not None and len(env.get_payload_encoding()) > 0:
            sb = sb + self.encode_tag(self.ENCODING_TAG, env.get_payload_encoding())

        # Create tag date
        # Create object BasicFipaDateTime
        if env.get_date() is not None:
            date = BasicFipaDateTime()
            date.from_string(str(env.get_date()))
            sb = sb + self.encode_tag(self.DATE_TAG, str(date))

        # Create tag encrypted (NL: not sure it is still in FIPA)
        """
        for i in env.getEncrypted():
            sb = sb + self.encodeTag( self.ENCRYPTED_TAG, str(i) )
        """

        # Create tag intended-receiver
        for i in env.get_intended_receiver():
            sb = sb + self.OT + self.INTENDED_TAG + self.CT
            sb = sb + self.encode_aid(i)
            sb = sb + self.ET + self.INTENDED_TAG + self.CT

        """
        #Create tags for user properties
        for (i=env.getAllProperties();i.hasNext();) {
            encodeProp(sb,(Property)i.next());
        """

        # Create tag received
        ro = env.get_received()
        if ro is not None:
            # Create tag received
            sb = sb + self.OT + self.RECEIVED_TAG + self.CT
            # Date
            value = BasicFipaDateTime(ro.get_date())
            if value is not None:
                sb = sb + self.encode_oneline_tag(self.RECEIVED_DATE, self.RECEIVED_ATTR, str(value))
            # By
            value = ro.get_by()
            if value is not None:
                sb = sb + self.encode_oneline_tag(self.RECEIVED_BY, self.RECEIVED_ATTR, value)
            # From
            value = ro.get_from()
            if value is not None:
                sb = sb + self.encode_oneline_tag(self.RECEIVED_FROM, self.RECEIVED_ATTR, value)
            # Id
            value = ro.get_id()
            if value is not None:
                sb = sb + self.encode_oneline_tag(self.RECEIVED_ID, self.RECEIVED_ATTR, value)
            # Via
            value = ro.get_via()
            if value is not None:
                sb = sb + self.encode_oneline_tag(self.RECEIVED_VIA, self.RECEIVED_ATTR, value)

            sb = sb + self.ET + self.RECEIVED_TAG + self.CT

        sb = sb + self.ET + self.PARAMS_TAG + self.CT
        sb = sb + self.ET + self.ENVELOPE_TAG + self.CT

        return sb

    """
     ***************************************************
     *               Decoding methods                  *
     ***************************************************
    """

    # This method is called when start the document XML
    def startDocument(self):
        self.env = Envelope.Envelope()

    # This method is called at the end of parsing */
    def endDocument(self):
        pass
        # Put the ro object in to envelope
        # env.setReceived(ro)

    # This method is called when jmp event of begin element.*/
    # def startElement(self, uri, localName, rawName, attributes):
    def startElement(self, localname, attributes):

        # Detection of the begin of to or from tags
        self.accumulator = ""

        if self.TO_TAG.lower() == localname.lower():
            self.aid = aid()
            self.aidTag = self.TO_TAG
            # self.env.addTo(aid)

        elif self.FROM_TAG.lower() == localname.lower():
            self.aid = aid()
            self.aidTag = self.FROM_TAG
            # self.env.setFrom(aid)

        elif self.INTENDED_TAG.lower() == localname.lower():
            self.aid = aid()
            self.aidTag = self.INTENDED_TAG
            # self.env.addIntendedReceiver(self.aid)

        elif self.RECEIVED_TAG.lower() == localname.lower():
            self.env.set_received(ReceivedObject())

        elif self.RECEIVED_BY.lower() == localname.lower():
            self.env.received.set_by(attributes.getValue(self.RECEIVED_ATTR))

        elif self.RECEIVED_FROM.lower() == localname.lower():
            self.env.received.set_from(attributes.getValue(self.RECEIVED_ATTR))

        elif self.RECEIVED_DATE.lower() == localname.lower():
            self.env.received.set_date(BasicFipaDateTime(str(attributes.getValue(self.RECEIVED_ATTR))))

        elif self.RECEIVED_ID.lower() == localname.lower():
            self.env.received.set_id(attributes.getValue(self.RECEIVED_ATTR))

        elif self.RECEIVED_VIA.lower() == localname.lower():
            self.env.received.set_via(attributes.getValue(self.RECEIVED_ATTR))

        """
        elif self.PROP_TAG.lower() == localName.lower():
            prop = Property()
            env.addProperties(prop)
            prop.setName(attributes.getValue(self.PROP_ATTR))
            propType = attributes.getValue(self.PROP_ATTR_TYPE)
        """

    # This method is called the end of element
    # def endElement(self, namespaceURL, localName, qname):
    def endElement(self, localname):

        # Capture the value the attributes of class
        if self.AID_NAME.lower() == localname.lower():
            self.aid.set_name(self.accumulator)

        elif self.AID_ADDRESS.lower() == localname.lower():
            self.aid.add_address(self.accumulator)

        elif self.TO_TAG.lower() == localname.lower():
            self.aidTag = ""

        elif self.FROM_TAG.lower() == localname.lower():
            self.aidTag = ""

        elif self.INTENDED_TAG.lower() == localname.lower():
            self.aidTag = ""

        elif self.AID_TAG.lower() == localname.lower():
            if self.aidTag == self.TO_TAG:
                self.env.add_to(self.aid)
            elif self.aidTag == self.FROM_TAG:
                self.env.set_from(self.aid)
            elif self.aidTag == self.INTENDED_TAG:
                self.env.add_intended_receiver(self.aid)

        elif self.COMMENTS_TAG.lower() == localname.lower():
            self.env.set_comments(self.accumulator)

        elif self.REPRESENTATION_TAG.lower() == localname.lower():
            self.env.set_acl_representation(self.accumulator)

        elif self.LENGTH_TAG.lower() == localname.lower():
            self.env.set_payload_length(int(self.accumulator))
            """
            if(logger.isLoggable(Logger.WARNING))
                logger.log(Logger.FINE,"Length: "+env.getPayloadLength());
            """

        elif self.ENCODING_TAG.lower() == localname.lower():
            self.env.set_payload_encoding(self.accumulator)

        elif self.DATE_TAG.lower() == localname.lower():
            bfdt = BasicFipaDateTime()
            bfdt.from_string(str(self.accumulator))
            self.env.set_date(bfdt)

        """
        elif self.PROP_TAG.lower() == localName.lower():
            decodeProp(accumulator, prop);
        """
        """
        #Not sure it is still in FIPA
        elif self.ENCRYPTED_TAG.lower() == localName.low():
            self.env.addEncrypted(accumulator)
        """

    # This method is called when exist characters in the elements
    def characters(self, buff):
        self.accumulator = self.accumulator + buff

    # Main method #
    def parse(self, _in):
        """
        parses the xml input
        """
        xml.sax.parseString(_in, self)
        return self.env
