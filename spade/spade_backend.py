#! python
# -*- coding: utf-8 -*-

from spade import AMS
from spade import Platform
from spade import DF
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
        port = int(config[section]['port'])
        jid = section + "." + server
        if not "adminpasswd" in config.keys():
            config["adminpasswd"] = None
        if section == "acc":
            agent = agentClass(jid, passwd, server, port, config=config)
        else:
            agent = agentClass(jid, passwd, server, port)
        agent.setAdminPasswd(config["adminpasswd"])
        agent.start()
        return agent

    def __init__(self, xmpp_server, configfilename="spade.xml", debug=False):
        parser = SpadeConfigParser.ConfigParser()
        self.config = parser.parse(configfilename)
        self.ams = None
        self.df = None
        self.acc = None
        self.alive = True  # Alive flag
        self._debug_flag = debug
        self.server = xmpp_server

    def start(self):
        #TODO: this should be configurable
        self.acc = self.runAgent(self.config, "acc", Platform.SpadePlatform)
        if self._debug_flag:
            self.acc.setDebugToScreen()
        self.acc.setXMPPServer(self.server)
        self.ams = self.runAgent(self.config, "ams", AMS.AMS)
        self.ams.DEBUG = self.acc.DEBUG
        #self.ams.setDebugToScreen()
        self.df = self.runAgent(self.config, "df", DF.DF)
        self.df.DEBUG = self.acc.DEBUG
        #self.df.setDebugToScreen()
        #self.simba = self.runAgent(self.configfile, "simba", SIMBA.SIMBA)

    def shutdown(self):
        if self.df:
            self.df.stop()
            #del self.df
            self.DEBUG("DF agent terminated.")
        if self.ams:
            self.ams.stop()
            #del self.ams
            self.DEBUG("AMS agent terminated.")
        if self.acc:
            self.acc.stop()
            self.DEBUG("ACC agent terminated.")
            #del self.acc

    def DEBUG(self, component="", msg="", typ=""):
        self.acc.DEBUG(msg, typ, component)

if __name__ == "__main__":
    p = SpadeBackend()
    p.start()
