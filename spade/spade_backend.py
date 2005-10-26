#! python
# -*- coding: cp1252 -*-
import sys, ConfigParser
#import Platform,AMS

#from spade import *

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

    
class SpadeBackend:
	"""
	Runs the platform.
	Inits the platform components (AMS, DF, ...)
	"""

	def runAgent(self, configfile, section, agentClass):
		"""
		starts an agent
		"""
		jid = configfile.get(section,'JID')
		passwd = configfile.get(section,'Password')
		server = configfile.get(section,'Server')
		port = int(configfile.get(section,'Port'))
		agent = agentClass(jid, passwd, server, port)
		#agent.setDaemon(True)
		agent.start()
		return agent
    
	def __init__(self, configfilename="/etc/spade/spade.ini"):
		print "SPADE started."
		self.configfile = ConfigParser.ConfigParser()
		try:
		    cffile = open(configfilename,'r')
		except IOError:
		    print "SPADE requires configuration file, please supply either spade.ini"
		    sys.exit(1)
		self.configfile.readfp(cffile)
		cffile.close()

	def start(self):
		self.runAgent(self.configfile, "spade", Platform.SpadePlatform)
		self.runAgent(self.configfile, "ams", AMS.AMS)
		self.runAgent(self.configfile, "df", DF.DF)
	

if __name__ ==  "__main__":
	p = SpadeBackend()
	p.start()
