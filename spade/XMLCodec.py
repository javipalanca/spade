# -*- coding: utf-8 -*-
import xml.sax
from xml.sax import handler
from BasicFipaDateTime import *
from AID import *
from ReceivedObject import ReceivedObject
import Envelope


class XMLCodec(handler.ContentHandler):
    """
    XML Parser
    """
    def __init__(self):
        #self.parser = xmlreader.IncrementalParser()
        #self.parser.setContentHandler(self)
        #self.parser.setErrorHandler(self)

        self.ToTag = False

        #Constants
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
        #self.ENCRYPTED_TAG = "encrypted"
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
    def encodeAid(self, agentid):

        if not isinstance(agentid, aid):
            return ""

        sb = self.OT + self.AID_TAG + self.CT
        sb = sb + self.encodeTag(self.AID_NAME, agentid.getName())
        sb = sb + self.OT + self.AID_ADDRESSES + self.CT

        addresses = agentid.getAddresses()
        for addr in addresses:
            sb = sb + self.encodeTag(self.AID_ADDRESS, addr)

        sb = sb + self.ET + self.AID_ADDRESSES + self.CT
        sb = sb + self.ET + self.AID_TAG + self.CT

        return sb

    """
      This does the following:
      < tag >
         content
      </ tag >
    """
    def encodeTag(self, tag, content):
        sb = self.OT + tag + self.CT
        sb = sb + content
        sb = sb + self.ET + tag + self.CT

        return sb

    """
    A user-defined property (String name, Object value) is encoded the following way:
    <user-defined href="name" type="type">value</user-defined>
    """

    def encodeOneLineTag(self, tag1, tag2, value):
        sb = self.OT + tag1 + " "
        sb = sb + tag2 + '="' + value + '"/>'

        return sb

    def encodeXML(self, env):
        """
        General Encoding of the envelope
        """

        #Create the message XML
        sb = self.OT + self.ENVELOPE_TAG + self.CT
        sb = sb + self.OT + self.PARAMS_TAG + self.INDEX_ATTR + "1" + '"' + self.CT

        #Create tag TO
        tos = env.getTo()
        for agentid in tos:
            sb = sb + self.OT + self.TO_TAG + self.CT
            sb = sb + self.encodeAid(agentid)
            sb = sb + self.ET + self.TO_TAG + self.CT

        #Create tag from
        if env.getFrom() is not None:
            sb = sb + self.OT + self.FROM_TAG + self.CT
            sb = sb + self.encodeAid(env.getFrom())
            sb = sb + self.ET + self.FROM_TAG + self.CT

        #Create tag comments
        if env.getComments() is not None and len(env.getComments()) > 0:
            sb = sb + self.encodeTag(self.COMMENTS_TAG, env.getComments())

        #Create tag acl-representation
        if env.getAclRepresentation() is not None:
            sb = sb + self.encodeTag(self.REPRESENTATION_TAG, env.getAclRepresentation())

        #Create tag payload-length
            if env.getPayloadLength() is not None:
                sb = sb + self.encodeTag(self.LENGTH_TAG, str(env.getPayloadLength()))

        #Create tag payload-encoding
        if env.getPayloadEncoding() is not None and len(env.getPayloadEncoding()) > 0:
            sb = sb + self.encodeTag(self.ENCODING_TAG, env.getPayloadEncoding())

        #Create tag date
        #Create object BasicFipaDateTime
        if env.getDate() is not None:
            date = BasicFipaDateTime()
            date.fromString(str(env.getDate()))
            sb = sb + self.encodeTag(self.DATE_TAG, str(date))

        #Create tag encrypted (NL: not sure it is still in FIPA)
        """
        for i in env.getEncrypted():
            sb = sb + self.encodeTag( self.ENCRYPTED_TAG, str(i) )
        """

        #Create tag intended-receiver
        for i in env.getIntendedReceiver():
            sb = sb + self.OT + self.INTENDED_TAG + self.CT
            sb = sb + self.encodeAid(i)
            sb = sb + self.ET + self.INTENDED_TAG + self.CT

        """
        #Create tags for user properties
        for (i=env.getAllProperties();i.hasNext();) {
            encodeProp(sb,(Property)i.next());
        """

        #Create tag received
        ro = env.getReceived()
        if ro is not None:
            #Create tag received
            sb = sb + self.OT + self.RECEIVED_TAG + self.CT
            #Date
            value = BasicFipaDateTime(ro.getDate())
            if value is not None:
                sb = sb + self.encodeOneLineTag(self.RECEIVED_DATE, self.RECEIVED_ATTR, str(value))
            #By
            value = ro.getBy()
            if value is not None:
                sb = sb + self.encodeOneLineTag(self.RECEIVED_BY, self.RECEIVED_ATTR, value)
            #From
            value = ro.getFrom()
            if value is not None:
                sb = sb + self.encodeOneLineTag(self.RECEIVED_FROM, self.RECEIVED_ATTR, value)
            #Id
            value = ro.getId()
            if value is not None:
                sb = sb + self.encodeOneLineTag(self.RECEIVED_ID, self.RECEIVED_ATTR, value)
            #Via
            value = ro.getVia()
            if value is not None:
                sb = sb + self.encodeOneLineTag(self.RECEIVED_VIA, self.RECEIVED_ATTR, value)

            sb = sb + self.ET + self.RECEIVED_TAG + self.CT

        sb = sb + self.ET + self.PARAMS_TAG + self.CT
        sb = sb + self.ET + self.ENVELOPE_TAG + self.CT

        return sb

    """
     ***************************************************
     *               Decoding methods                  *
     ***************************************************
    """

    #This method is called when start the document XML
    def startDocument(self):
        self.env = Envelope.Envelope()

    #This method is called at the end of parsing */
    def endDocument(self):
        pass
        #Put the ro object in to envelope
        #env.setReceived(ro)

    #This method is called when jmp event of begin element.*/
    #def startElement(self, uri, localName, rawName, attributes):
    def startElement(self, localName, attributes):

        #Detection of the begin of to or from tags
        self.accumulator = ""

        if self.TO_TAG.lower() == localName.lower():
            self.aid = aid()
            self.aidTag = self.TO_TAG
            #self.env.addTo(aid)

        elif self.FROM_TAG.lower() == localName.lower():
            self.aid = aid()
            self.aidTag = self.FROM_TAG
            #self.env.setFrom(aid)

        elif self.INTENDED_TAG.lower() == localName.lower():
            self.aid = aid()
            self.aidTag = self.INTENDED_TAG
            #self.env.addIntendedReceiver(self.aid)

        elif self.RECEIVED_TAG.lower() == localName.lower():
            self.env.setReceived(ReceivedObject())

        elif self.RECEIVED_BY.lower() == localName.lower():
            self.env.received.setBy(attributes.getValue(self.RECEIVED_ATTR))

        elif self.RECEIVED_FROM.lower() == localName.lower():
            self.env.received.setFrom(attributes.getValue(self.RECEIVED_ATTR))

        elif self.RECEIVED_DATE.lower() == localName.lower():
            self.env.received.setDate(BasicFipaDateTime(str(attributes.getValue(self.RECEIVED_ATTR))))

        elif self.RECEIVED_ID.lower() == localName.lower():
            self.env.received.setId(attributes.getValue(self.RECEIVED_ATTR))

        elif self.RECEIVED_VIA.lower() == localName.lower():
            self.env.received.setVia(attributes.getValue(self.RECEIVED_ATTR))

        """
        elif self.PROP_TAG.lower() == localName.lower():
            prop = Property()
            env.addProperties(prop)
            prop.setName(attributes.getValue(self.PROP_ATTR))
            propType = attributes.getValue(self.PROP_ATTR_TYPE)
        """

    #This method is called the end of element
    #def endElement(self, namespaceURL, localName, qname):
    def endElement(self, localName):

        #Capture the value the attributes of class
        if self.AID_NAME.lower() == localName.lower():
            self.aid.setName(self.accumulator)

        elif self.AID_ADDRESS.lower() == localName.lower():
            self.aid.addAddress(self.accumulator)

        elif self.TO_TAG.lower() == localName.lower():
            self.aidTag = ""

        elif self.FROM_TAG.lower() == localName.lower():
            self.aidTag = ""

        elif self.INTENDED_TAG.lower() == localName.lower():
            self.aidTag = ""

        elif self.AID_TAG.lower() == localName.lower():
            if self.aidTag == self.TO_TAG:
                self.env.addTo(self.aid)
            elif self.aidTag == self.FROM_TAG:
                self.env.setFrom(self.aid)
            elif self.aidTag == self.INTENDED_TAG:
                self.env.addIntendedReceiver(self.aid)

        elif self.COMMENTS_TAG.lower() == localName.lower():
            self.env.setComments(self.accumulator)

        elif self.REPRESENTATION_TAG.lower() == localName.lower():
            self.env.setAclRepresentation(self.accumulator)

        elif self.LENGTH_TAG.lower() == localName.lower():
            self.env.setPayloadLength(long(self.accumulator))
            """
            if(logger.isLoggable(Logger.WARNING))
                logger.log(Logger.FINE,"Length: "+env.getPayloadLength());
            """

        elif self.ENCODING_TAG.lower() == localName.lower():
            self.env.setPayloadEncoding(self.accumulator)

        elif self.DATE_TAG.lower() == localName.lower():
            bfdt = BasicFipaDateTime()
            bfdt.fromString(str(self.accumulator))
            self.env.setDate(bfdt)

        """
        elif self.PROP_TAG.lower() == localName.lower():
            decodeProp(accumulator, prop);
        """
        """
        #Not sure it is still in FIPA
        elif self.ENCRYPTED_TAG.lower() == localName.low():
            self.env.addEncrypted(accumulator)
        """

    #This method is called when exist characters in the elements
    def characters(self, buff):
        self.accumulator = self.accumulator + buff

    # Main method #
    def parse(self, _in):
        """
        parses the xml input
        """
        xml.sax.parseString(_in, self)
        return self.env
