import xmlstream
import agent
import message


class Service:	
	def __init__(self, servicename, agent):
		self.servicename = servicename
		self.agent = agent
		
	def handle(self, msg = None, remoteservice = None):
		self.msg = msg
		pass
