from turbogears import controllers, expose, flash, redirect
import sys
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
        import time
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
