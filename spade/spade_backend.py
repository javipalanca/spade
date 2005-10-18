#! python
# -*- coding: cp1252 -*-
import sys, ConfigParser
#import Platform,AMS
from spade import *

    
class SpadeBackend:

	def runAgent(self, configfile, section, agentClass):
	    jid = configfile.get(section,'JID')
	    passwd = configfile.get(section,'Password')
	    server = configfile.get(section,'Server')
	    port = int(configfile.get(section,'Port'))
	    agent = agentClass(jid, passwd, server, port)
	    agent.start()
    

	def __init__(self, configfilename="/etc/spade/spade.ini"):
		print "SPADE started."
		configfile = ConfigParser.ConfigParser()
		try:
		    cffile = open(configfilename,'r')
		except IOError:
		    print "SPADE requires configuration file, please supply either spade.ini"
		    sys.exit(1)
		configfile.readfp(cffile)
		cffile.close()

	def start(self):
		runAgent(configfile, "spade", Platform.SpadePlatform)
		runAgent(configfile, "ams", AMS.AMS)
		runAgent(configfile, "df", DF.DF)

if __name__ ==  "__main__":
	p = SpadeBackend()
	p.start()
