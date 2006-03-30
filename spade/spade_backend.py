#! python
# -*- coding: cp1252 -*-
import sys


from spade import ACLMessage
from spade import Agent
from spade import AMS
from spade import Behaviour
from spade import Envelope
from spade import Platform
from spade import ReceivedObject
from spade import ACLParser
from spade import AID
from spade import BasicFipaDateTime
from spade import DF
from spade import FIPAMessage
from spade import MessageReceiver
from spade import pyparsing
from spade import SL0Parser
from spade import XMLCodec
from spade import SpadeConfigParser 

    
class SpadeBackend:
	"""
	Runs the platform.
	Inits the platform components (AMS, DF, ...)
	"""

	def runAgent(self, config, section, agentClass):
		"""
		starts an agent
		"""
		#jid = configfile.get(section,'JID')
		passwd = config[section]['password']
		server = config["platform"]['hostname']
		port = int( config[section]['port'] )
		jid = section + "." + server
		agent = agentClass(jid, passwd, server, port)
		agent.start()
		return agent
    
	def __init__(self, configfilename="/etc/spade/spade.xml"):
		parser = SpadeConfigParser.ConfigParser()
		self.config = parser.parse(configfilename)

	def start(self):
		#TODO: this should be configurable
		#self.acc = self.runAgent(self.configfile, "acc", Platform.SpadePlatform)
		self.ams = self.runAgent(self.config, "ams", AMS.AMS)
		self.df = self.runAgent(self.config, "df", DF.DF)
		#self.simba = self.runAgent(self.configfile, "simba", SIMBA.SIMBA)

	def shutdown(self):
		if self.df: self.df.stop()
		if self.ams: self.ams.stop()
		#self.acc.stop()


if __name__ ==  "__main__":
	p = SpadeBackend()
	p.start()
