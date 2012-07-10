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
        if not "adminpasswd" in config.keys(): config["adminpasswd"]=None
        if section == "acc":
            agent = agentClass(jid, passwd, server, port, config=config)
        else:
            agent = agentClass(jid, passwd, server, port)
            agent.setAdminPasswd(config["adminpasswd"])
        agent.start()
        return agent
    
    def __init__(self, configfilename="/etc/spade/spade.xml"):
        parser = SpadeConfigParser.ConfigParser()
        self.config = parser.parse(configfilename)
        self.ams=None
        self.df =None
        self.acc=None     
        self.alive = True  # Alive flag

    def start(self):
        #TODO: this should be configurable
        self.acc = self.runAgent(self.config, "acc", Platform.SpadePlatform)
        #self.acc._debug=True
        self.ams = self.runAgent(self.config, "ams", AMS.AMS)
        #self.ams.DEBUG = self.acc.DEBUG
        self.df = self.runAgent(self.config, "df", DF.DF)
        #self.df.DEBUG = self.acc.DEBUG
        #self.simba = self.runAgent(self.configfile, "simba", SIMBA.SIMBA)        

    def shutdown(self):
        if self.df:
		    self.df.stop()
		    #del self.df
        if self.ams: 
		    self.ams.stop()
		    #del self.ams
        if self.acc:
		    self.acc.stop()
		    #del self.acc
		    
    def DEBUG(self,component="",msg="",typ=""):
	    self.acc.DEBUG(msg,typ,component)

if __name__ ==  "__main__":
	p = SpadeBackend()
	p.start()
