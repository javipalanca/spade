
from spade import SpadeConfigParser

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

	def send(self, envelope, payload, to=None):
		raise NotImplemented


PROTOCOL = None  #This must be overriden
INSTANCE = None  #This must be overriden

