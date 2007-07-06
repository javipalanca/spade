# encoding: utf-8
from turbogears import controllers, expose, flash, redirect
import sys
import time
try:
    from spade import *
except:
    sys.path.append("..")
    from spade import *
    
# from model import *
# import logging
# log = logging.getLogger("swi.controllers")

class Root(controllers.RootController):
    @expose(template="swi.templates.webadmin")
    def index(self):
        # log.debug("Happy TurboGears Controller Responding For Duty")
        #s = self.platform.acc.getName()
        #flash("Your application is now running "+s)
        #return dict(now=time.ctime())
        servername = self.platform.acc.getDomain()
        platform = self.platform.acc.getName()        
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
    def sendmessage(self, to, fipa, receivers, performative, sender, reply_to, reply_with, reply_by, in_reply_to, encoding, language, ontology, protocol, conversation_id, content):
        msg = self.platform.acc.newMessage()
        if type(receivers) == type([]):
            for recv in receivers:
                a = AID.aid(str(recv),["xmpp://"+str(recv)])
                msg.addReceiver(a)
        else:
            a = AID.aid(str(receivers),["xmpp://"+str(receivers)])
            msg.addReceiver(a)
        msg.setPerformative(performative)
        if sender:
            s = AID.aid(str(sender), ["xmpp://"+str(sender)])
            msg.setSender(s)
        if reply_to: msg.setReplyTo(reply_to)
        if reply_with: msg.setReplyWith(reply_with)
        if reply_by: msg.setReplyBy(reply_by)
        if in_reply_to: msg.setInReplyTo(in_reply_to)
        if encoding: msg.setEncoding(encoding)
        if language: msg.setLanguage(language)
        if ontology: msg.setOntology(ontology)
        if protocol: msg.setProtocol(protocol)
        if conversation_id: msg.setConversationId(conversation_id)
        msg.setContent(content)
        print "THE MESSAGE",str(msg)
        try:
            self.platform.acc.send(msg, "jabber")
            flash("ACL message successfully sent")
        except:
            flash("Error sending ACL message")
        raise redirect("/clients")
    
    @expose(template="swi.templates.services")
    def services(self):
        #flash("SERVICES PAGE")
        services=[]
        # Build a LIST of DADs
        for dad in self.platform.df.servicedb.values():
            services.append(dad)
        return dict(services=services)
        
    @expose()
    def deleteservice(self, service, owner):
        try:
            services = self.platform.df.servicedb[owner].getServices()
            for s in services:
                if service == s.getName():
                    services.remove(s)
                    flash("Service "+service+" deregistered correctly")
                    if len(services) <= 0:
                        del self.platform.df.servicedb[owner]
        except:
            flash("Could not deregister service "+service)
            
        raise redirect("/services")
                    
        
    @expose(template="swi.templates.orgs")
    def orgs(self):
        """"
        orgs=[]
        # Build a LIST of DADs
        for dad in self.platform.df.servicedb.values():
            for service in dad:
                if str(service.getType()).lower() == "organization":
                    members = self.platform.acc.getMembers()
                    orgs.append((dad,members))                
        return dict(orgs=orgs)
        """
        return dict()
    
    @expose(template="swi.templates.prefs")
    def prefs(self):
        return dict()
        
    @expose(template="swi.templates.plugins")
    def plugins(self):
        return dict()
    
    @expose()
    def restart(self,restart):
        self.platform.shutdown()
        time.sleep(5)
        self.platform.start()
        flash("Platform restarted")
        raise redirect("/")
        