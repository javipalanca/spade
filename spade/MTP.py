
from spade import SpadeConfigParser
from spade import XMLCodec
from xmpp import *

class MTP:

	def __init__(self, name, config, acc):

		#parser = SpadeConfigParser.ConfifParser()
		#self.config = parser.parse(CONFIGFILE)

		self.name = name
		self.config = config
		self.acc = acc

		self.protocol = self.config.acc[name].protocol
		#self.instance = self.config.acc[name].instance

		self.setup()

	def setup(self):
		raise NotImplemented

	# Envelope = Envelope Class
	# Payload = raw text
	def send(self, envelope, payload):
		raise NotImplemented


	def dispatch(self, envelope, payload):

		xc = XMLCodec.XMLCodec()
		envxml = xc.encodeXML(envelope)

		xenv = protocol.Node('jabber:x:fipa x')
		xenv['content-type']='fipa.mts.env.rep.xml.std'
		xenv.addData(envxml)

		for to in envelope.getTo():

			stanza = protocol.Message(to.getName(),payload, xmlns="")
			stanza.addChild(node=xenv)

			s=None
			s = self.acc._router._owner.getsession(to.getName())
			if s:
				s.enqueue(stanza)
		


PROTOCOL = None  #This must be overriden
INSTANCE = None  #This must be overriden

