
from spade import SpadeConfigParser

#CONFIGFILE = "/etc/spade/spade.xml"

PROTOCOL = None  #This must be overriden
INSTANCE = None  #This must be overriden


class MTP:

	def __init__(self, name, config):

		#parser = SpadeConfigParser.ConfifParser()
		#self.config = parser.parse(CONFIGFILE)

		self.name = name
		self.config = config

		self.protocol = self.config.acc[name].protocol
		#self.instance = self.config.acc[name].instance

		self.__setup()

	def __setup(self):
		pass
		#other parameters must be overloaded

	def send(self, envelope, payload, to=None):
		pass

