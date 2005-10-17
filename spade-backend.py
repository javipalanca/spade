#! python
# -*- coding: cp1252 -*-
import sys, ConfigParser
#import Platform,AMS
from spade import *

    

def runAgent(configfile, section, agentClass):
    jid = configfile.get(section,'JID')
    passwd = configfile.get(section,'Password')
    server = configfile.get(section,'Server')
    port = int(configfile.get(section,'Port'))
    agent = agentClass(jid, passwd, server, port)
    agent.start()
    


print "Starting SpadePlatform..."
configfile = ConfigParser.ConfigParser()
try:
    configfilename = '/etc/spade.ini'
    cffile = open(configfilename,'r')
except IOError:
    print "SPADE requires configuration file, please supply either spade.ini"
    sys.exit(1)
configfile.readfp(cffile)
cffile.close()

runAgent(configfile, "spade", Platform.SpadePlatform)
runAgent(configfile, "ams", AMS.AMS)
runAgent(configfile, "df", DF.DF)
