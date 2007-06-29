from turbogears import controllers, expose, flash
# from model import *
# import logging
# log = logging.getLogger("swi.controllers")

class Root(controllers.RootController):
    @expose(template="swi.templates.webadmin")
    def index(self):
        import time
        # log.debug("Happy TurboGears Controller Responding For Duty")
        #s = self.platform.acc.getName()
        #flash("Your application is now running "+s)
        #return dict(now=time.ctime())
        servername = self.platform.acc.getDomain()
        platform = self.platform.acc.getName()
        import sys
        version = str(sys.version)
        the_time = str(time.ctime())
#        import os
#        ls = str(os.listdir("."))
        return dict(servername=servername, platform=platform, version=version, time=the_time)

    @expose(template="swi.templates.clients")
    def clients(self):
        return dict(agents=self.platform.ams.agentdb)
    
    @expose(template="swi.templates.message")
    def message(self,to=""):
        keys = self.platform.ams.agentdb.keys()
        if to in keys:
            return dict(to=to, keys=keys)
        else:
            return dict(to="", keys=keys)
    
    @expose()
    def sendmessage(self, *args, **kwargs):
        #print "### SEND KWARGS"
        #print kwargs
        return dict()
