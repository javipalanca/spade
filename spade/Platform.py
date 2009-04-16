from AMS import AmsAgentDescription
from DF import DfAgentDescription, ServiceDescription
import xmpp
import threading
import Agent
import Envelope
import FIPAMessage
import AID
import Behaviour
import os.path
import sys
import traceback
import SocketServer
import SimpleHTTPServer
import BaseHTTPServer
import time
import thread
import copy
import ACLMessage
import types
import ACLParser
import BasicFipaDateTime

#from swi import SWIHandler
import swi
from os.path import *

class PlatformRestart(Exception):
    def __init__(self): pass
    def __str__(self): return


class WebAdminHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    _body_template = "<table><tr><td class=cabecera colspan=2>#TOP#</td></tr><tr><td class=lateral>#MENU_LEFT#</td><td>#PANEL_RIGHT#</td></tr><tr><td>#BOTTOM#</td></tr></table>"

    def header(self, title="SPADE WEB ADMIN"):
        try:
            os.stat("modules/web/webadmin.css")
            return "<html><head><link rel=stylesheet type='text/css' href='modules/web/webadmin.css'><title>" + title + "</title></head>"
        except:
            return "<html><head><link rel=stylesheet type='text/css' href='xmppd/modules/web/webadmin.css'><title>" + title + "</title></head>"


    def body(self, body = ""):
        return "<body>" + str(body) # + "</body>"

    def footer(self, foot = ""):
        return foot+"</body>"+"</html>"

    def getPage(self, req):
        """
        Return the page name from a raw GET line
        """
        return req.split("?")[0]

    def getVars(self, req):
        """
        Return the variables and values from a raw GET or POST request line
        """
        d = dict()
        try:
            raw_vars = req.split("?")[1]
            print "RAW_VARS", raw_vars
            for raw in raw_vars.split("&"):
                #print raw
                var = raw.split("=")
                if len(var) > 1:
                    # Check if this is a multi-valued var
                    if var[0] in d.keys():
                        try:
                            # Try to append value to the list
                            d[var[0]].append(var[1])
                        except:
                            # Create a list with the current value and append the new one
                            d[var[0]] = [d[var[0]]]
                            d[var[0]].append(var[1])
                    else:
                        d[var[0]] = var[1]
                else:
                    d[var[0]] = ""
                print var
        except:
            pass

        return d

    def sendMsg(self, to, msg):
        """
        Send a message to a client
        """
        # Translate 'to' to proper address (convert @ and /)
#        to = to.replace("%40", "@")
#        to = to.replace("%2F", "/")
#        stanza = Message(to=to, body=msg, frm=self.server.xmppd.servernames[0])
#        print "CREATED STANZA: " + str(stanza)
#        s = None
#        s = self.server.xmppd.getsession(to)
#        if s:
#            print "SENDING MSG TO " + to
#            s.enqueue(stanza)
#        else:
#            print "NO SESSION FOR MESSAGE"
#        return
        return

    #def createFIPAMsg(self, to, performative, content):
    def createFIPAMsg(self, vars):
        msg = ACLMessage.ACLMessage()

        to_list = copy.copy(vars['receivers'])
        if to_list.__class__ != types.ListType:
            to_list = [to_list]
        for to in to_list:
            to = to.replace("%40", "@")
            to = to.replace("%2F", "/")
            receiver = AID.aid(name=to, addresses=["xmpp://"+to])
            msg.addReceiver(receiver)

        msg.setPerformative(vars['performative'])
        if vars['content']: msg.setContent(vars['content'])
        if vars['sender']:
            vars['sender'] = vars['sender'].replace("%40", "@")
            vars['sender'] = vars['sender'].replace("%2F", "/")
            msg.setSender(AID.aid(name=vars['sender'], addresses=["xmpp://"+vars['sender']]))
        if vars['reply-to']:
            vars['reply-to'] = vars['reply-to'].replace("%40", "@")
            vars['reply-to'] = vars['reply-to'].replace("%2F", "/")
            msg.addReplyTo(AID.aid(name=vars['reply-to'], addresses=["xmpp://"+vars['reply-to']]))
        if vars['reply-with']: msg.setReplyWith(vars['reply-with'])
        if vars['reply-by']: msg.setReplyBy(vars['reply-by'])
        if vars['in-reply-to']: msg.setInReplyTo(vars['in-reply-to'])
        if vars['encoding']: msg.setEncoding(vars['encoding'])
        if vars['language']: msg.setLanguage(vars['language'])
        if vars['ontology']: msg.setOntology(vars['ontology'])
        if vars['protocol']: msg.setProtocol(vars['protocol'])
        if vars['conversation-id']: msg.setConversationId(vars['conversation-id'])
        print "ACL MESSAGE: ", str(msg)
        return msg

    def setPageTemplate(self):
        self._body = copy.copy(self._body_template)
        self._body = self._body.replace("#TOP#", "<h1>SPADE WEB ADMIN</h1>")
        self._body = self._body.replace("#MENU_LEFT#", '<a class=lateral href="/">Main</a><br/><a class=lateral href="/pref">Preferences</a><br/><a class=lateral href="/clients">Agents</a><br/><a class=lateral href="/services">Services</a><br/><a class=lateral href="/orgs">Organizations</a><br/><a class=lateral href="/plugins">Plugins</a>')
        self._body = self._body.replace("#PANEL_RIGHT#", """<h2>MAIN CONTROL PANEL</h2><br>#MAINCP#""")


    def do_POST(self):
        print "POST"

        self._POST_REQ = ""
        try:
            length = int(self.headers.getheader('content-length'))
            self._POST_REQ = self.rfile.read(length)
        except:
            pass

        print "_POST_REQ:", self._POST_REQ

        self.do_GET()


    def do_GET(self):
        """
        GET petitions handler
        """
        #print "ENVIRON: ", str(os.environ)

        request = self.raw_requestline.split()
        page = self.getPage(request[1])
        try:
            vars = self.getVars("?"+self._POST_REQ)
        except:
            vars = self.getVars(request[1])
        print page, vars
        self._content = ""
        # Switch page
        if page.endswith("css"):
                #self.copyfile(urllib.urlopen(self.path), self.wfile)
            try:
                f = open(page[1:], "r")
                self.copyfile(f, self.wfile)
                f.close()
            except:
                print "Could not open file: ", page[1:]

        elif page == "/pref":
            self.setPageTemplate()
            cp = ""
            self._body = self._body.replace("#MAINCP#", cp)
            self._body = self._body.replace("#BOTTOM#", '')
            self._content = self.header() + self.body(self._body) + self.footer("<h5>Designed by <a href='http://gti-ia.dsic.upv.es'>GTI-IA DSIC UPV</a></h5>")

        elif page == "/send":
            self.setPageTemplate()
            cp = ""
#
#            cp = cp + """<table><tr><td>Send a Jabber message to agent """ + vars['to'] + """<br/>
#            <FORM ACTION="/clients" METHOD="POST">
#            <INPUT TYPE="text" NAME="msg"><BR/>
#            <INPUT TYPE="hidden" NAME="to" VALUE='"""+vars['to']+"""'>
#            <INPUT TYPE="hidden" NAME="jabber" VALUE="YES">
#            <INPUT TYPE="submit" VALUE="Send">
#            </FORM></td></tr>
#            """
            cp = cp + """
            <table><tr><td>
            Send a FIPA message to agent """ + vars['to'] + """<br/>
            <FORM ACTION="/clients" METHOD="POST">
            <div>
            """

            # Create the "Receivers" field with the agents present in the platform
            search = self.server.behav.getAgent().searchAgent(AmsAgentDescription())
            cp = cp + """
            <fieldset>
            <legend>Receivers</legend>
            <select name="receivers" multiple="multiple" size=""" + str(len(search)) + """>"""

            for cl in search:
                tmp = ""
                aname = str(cl['name']['agent-identifier']['name']).strip("[']")
                if aname == vars['to']:
                    selected = '''SELECTED="SELECTED"'''
                else:
                    selected = ""
                selected
                cp = cp + """<OPTION VALUE="""+aname+""" """+selected+""">"""+aname+"""</option>"""

            cp = cp + """
            </select>
            </fieldset>
            """

            cp = cp + """
            <fieldset>
            <legend>Header</legend>
            <table><tr><td>
            Performative: <SELECT NAME="performative">
            <OPTION VALUE="accept-proposal">Accept-Proposal</OPTION>
            <OPTION VALUE="agree">Agree</OPTION>
            <OPTION VALUE="cancel">Cancel</OPTION>
            <OPTION VALUE="cfp">CFP</OPTION>
            <OPTION VALUE="confirm">Confirm</OPTION>
            <OPTION VALUE="disconfirm">Disconfirm</OPTION>
            <OPTION VALUE="failure">Failure</OPTION>
            <OPTION VALUE="inform">Inform</OPTION>
            <OPTION VALUE="not-understood">Not-Understood</OPTION>
            <OPTION VALUE="propagate">Propagate</OPTION>
            <OPTION VALUE="propose">Propose</OPTION>
            <OPTION VALUE="proxy">Proxy</OPTION>
            <OPTION VALUE="query-if">Query-If</OPTION>
            <OPTION VALUE="query-ref">Query-Ref</OPTION>
            <OPTION VALUE="refuse">Refuse</OPTION>
            <OPTION VALUE="reject-proposal">Reject-Proposal</OPTION>
            <OPTION VALUE="request">Request</OPTION>
            <OPTION VALUE="request-when">Request-When</OPTION>
            <OPTION VALUE="request-whenever">Request-Whenever</OPTION>
            <OPTION VALUE="subscribe">Subscribe</OPTION>
            </SELECT>
            </td><td>
            Sender: <INPUT TYPE="text" NAME="sender">
            </td><td>
            Reply To: <INPUT TYPE="text" NAME="reply-to">
            </td></tr></table>
            </fieldset>

            <fieldset>
            <legend>Reply Options</legend>
            <table><tr><td>
            Reply With: <INPUT TYPE="text" NAME="reply-with">
            </td><td>
            Reply By: <INPUT TYPE="text" NAME="reply-by">
            </td><td>
            In Reply To: <INPUT TYPE="text" NAME="in-reply-to">
            </td></tr></table>
            </fieldset>

            <fieldset>
            <legend>Syntax Options</legend>
            <table><tr><td>
            Encoding: <INPUT TYPE="text" NAME="encoding">
            </td><td>
            Language: <INPUT TYPE="text" NAME="language">
            </td><td>
            Ontology: <INPUT TYPE="text" NAME="ontology">
            </td></tr></table>
            </fieldset>

            <fieldset>
            <legend>Conversation Options</legend>
            <table><tr><td>
            Protocol: <INPUT TYPE="text" NAME="protocol">
            </td><td>
            Conversation ID: <INPUT TYPE="text" NAME="conversation-id">
            </td></tr></table>
            </fieldset>

            <fieldset>
            <legend>Content</legend>
            <table><tr><td>
            <textarea name="content" rows="10" cols="100"></textarea><BR/>
            <INPUT TYPE="hidden" NAME="to" VALUE='"""+vars['to']+"""'>
            <INPUT TYPE="hidden" NAME="fipa" VALUE="YES">
            </td></tr></table>
            </fieldset>
            <INPUT TYPE="submit" VALUE="Send">
            </FORM>
            </td></tr>
            """
            self._body = self._body.replace("#MAINCP#", cp)
            self._body = self._body.replace("#BOTTOM#", '')
            self._content = self.header() + self.body(self._body) + self.footer("<h5>Designed by <a href='http://gti-ia.dsic.upv.es'>GTI-IA DSIC UPV</a></h5>")

        elif page == "/services":
            self.setPageTemplate()
            cp = ""

            #Check if we have to delete any service
            #cp = cp + str(vars) + "<br />"
            if vars.has_key("delete"):
                # Search for the DAD of the given service

                # USe that DAD for a deregister query
                vars['delete'] = vars['delete'].replace("%40", "@")
                vars['delete'] = vars['delete'].replace("%2F", "/")
                ag = AID.aid(vars['delete'])
                dad = DfAgentDescription()
                dad.setAID(ag)
                search = self.server.behav.getAgent().searchService(dad)
                #cp = cp + str(search) + "<br />"
                search = self.server.behav.getAgent().deregisterService(dad)

            cp = cp + """Below there is the list of the services currently registered in the platform.<br/>
            <table><tr><th>Service</th><th>Agent</th><th>Type</th></tr>"""
            search = self.server.behav.getAgent().searchService(DfAgentDescription())
            print str(search)
            #print str(search.keys())

            i = 0
            # We are going to list all the current routes present in the server
            #if str(search).strip():
            try:
                #for j in range(0,len(search)):
                for dfd in search:
                    aname = dfd.getAID().getName()
                    #entry = search[j][1] #[0]['df-agent-description']
                    #print str(entry.__class__)
                    #print "ENTRY:", str(entry)

                    #for e in entry['services']['set'].values():
                    for sd in dfd.getServices():
                        #print "SERVICE LIST:", str(e.asDict())
                        #sname = str(e['name']).strip("[']")
                        sname = sd.getName()
                        #print "SERVICE NAME:", sname
                        #print str(cl.__class__)
                        # Odd or even
                        if i%2 == 1:
                            cp = cp + """<tr><td class=impar>"""
                            par = "impar"
                        else:
                            cp = cp + """<tr><td class=par>"""
                            par = "par"
                        tmp = ""
                        #for field, v in cl.items():
                        #    tmp = tmp + str(field) + "###" + str(v) + "$$$"
                        #aname = str(entry['name']['agent-identifier']['name']).strip("[']")
                        cp = cp + sname + """</td><td class="""+par+""">"""  + aname + """</td>"""
                        type = sd.getType()
                        if not type:
                            type = "--"
                        #if "type" in e.keys():
                        #    type = str(e.type).strip("[']")
                        #else:
                        #    type = "--"
                        cp = cp + """<td class=""" + par + """>""" + type + """</td>"""
                        cp = cp + '''<td><form action="/services" method="POST"><input type="hidden" name="delete" value="''' + aname + '''"><input type="submit" value="Deregister"></form></td>'''
                        cp = cp + """</tr>"""

                        # Update the even/odd index
                        i = i + 1

            except Exception, e:
                print "EXCEPTION: ", str(e)

            cp = cp + """</table>"""
            self._body = self._body.replace("#MAINCP#", cp)
            self._body = self._body.replace("#BOTTOM#", '')
            self._content = self.header() + self.body(self._body) + self.footer("<h5>Designed by <a href='http://gti-ia.dsic.upv.es'>GTI-IA DSIC UPV</a></h5>")


        elif page == "/orgs":
            self.setPageTemplate()
            cp = """Below there is the list of the organizations currently registered in the platform.<br/>
            <table><tr><th>Name</th><th>Supervisor</th><th>Topology</th><th>Members</th></tr>"""
            dad = DfAgentDescription()
            ds = ServiceDescription()
            ds.setType("organization")
            dad.addService(ds)
            search = self.server.behav.getAgent().searchService(dad)
            print str(search)
            #print str(search.keys())

            i = 0
            # We are going to list all the current routes present in the server
            if str(search).strip():
                try:
                    for j in range(0,len(search)):
                        entry = search[j][1]
    #                    print "ENTRY:", str(entry)
    #                    print "ENTRY KEYS:", str(entry.keys())
    #                    print "ENTRY VALUES:", str(entry.values())
    #                    print "ENTRY.NAME:", str(entry.name.asDict())
                        for e in entry.services.set.values():
                            #print "SERVICE LIST:", str(e.asDict())
                            sname = str(e.asDict()['name']).strip("[']")
                            print "SERVICE NAME:", sname
                            #print str(cl.__class__)
                            # Odd or even
                            if i%2 == 1:
                                cp = cp + """<tr><td class=impar>"""
                                par = "impar"
                            else:
                                cp = cp + """<tr><td class=par>"""
                                par = "par"
                            tmp = ""
                            #for field, v in cl.items():
                            #    tmp = tmp + str(field) + "###" + str(v) + "$$$"
                            aname = str(entry['name']['agent-identifier']['name']).strip("[']")
                            cp = cp + sname + """</td><td class="""+par+""">"""  + aname + """</td>"""
                            if "properties" in e.keys():#entry.services.set["service-description"].properties.set.asDict().has_key('property'):
                                #type = str(entry.services.set["service-description"].properties.set.property.asDict()['value']).strip("[']")
                                type="%%"
                                for p in range(0,len(e.properties.set)):
                                    if str(e.properties.set[p][1].name).strip("[']")=="topology":
                                        type = str(e.properties.set[p][1].value).strip("[']")
                                        print "SERVICE TYPE " + str(type)
                            else:
                                type = "--"
                            cp = cp + """<td class="""+par+""">""" + str(type) + """</td>"""
                            # Get members of each organization
                            members = self.server.behav.getMembers(aname)
                            cp = cp + """<td><table>"""
                            for m in members:
                                cp = cp + "<tr><td>" + str(m) + "</td></tr>"
                            cp = cp + """</table></td></tr>"""

                            # Update the even/odd index
                            i = i + 1

                except Exception, e:
                    print "EXCEPTION: ", str(e)

            cp = cp + """</table>"""
            self._body = self._body.replace("#MAINCP#", cp)
            self._body = self._body.replace("#BOTTOM#", '')
            self._content = self.header() + self.body(self._body) + self.footer("<h5>Designed by <a href='http://gti-ia.dsic.upv.es'>GTI-IA DSIC UPV</a></h5>")


        elif page == "/clients":
            # First of all, see if we need to send a message
#            if vars.has_key("jabber"):
#                if vars.has_key("to") and vars.has_key("msg"):
#                    # Yup, a message
#                    self.sendMsg(vars["to"], vars["msg"])
            if vars.has_key("fipa"):
                print "SENDING FIPA MESSAGE: ", vars["to"], vars["performative"], vars["content"]
                #fmsg = self.createFIPAMsg(vars["to"], vars["performative"], vars["content"])
                fmsg = self.createFIPAMsg(vars)
                self.server.behav.myAgent.send(fmsg)
#                self.sendFIPAMsg(vars["to"], vars["performative"], vars["content"])

            self.setPageTemplate()
            cp = """Below there is the list of the agents currently connected to the platform.<br/>
            <table><tr><th>Agent</th><th>State</th><th>Ownership</th></tr>"""
            search = self.server.behav.getAgent().searchAgent(AmsAgentDescription())
            #print str(search)

            i = 0
            # We are going to list all the current routes present in the server
            for cl in search:
                print str(cl.__class__)
                # Odd or even
                if i%2 == 1:
                    cp = cp + """<tr><td class=impar>"""
                    par = "impar"
                else:
                    cp = cp + """<tr><td class=par>"""
                    par = "par"
                tmp = ""
                #for field, v in cl.items():
                #    tmp = tmp + str(field) + "###" + str(v) + "$$$"
                aname = str(cl['name']['agent-identifier']['name']).strip("[']")
                try:
                    state = str(cl['state'])
                except:
                    state = ""
                cp = cp + """<a href='/send?to="""+aname+"""'>""" + aname + """</a></td><td class="""+par+""">""" + state + """</td><td class="""+par+""">""" + str(cl['ownership']) + """</td></tr>"""

                # Update the even/odd index
                i = i + 1


            cp = cp + """</table>"""
            self._body = self._body.replace("#MAINCP#", cp)
            self._body = self._body.replace("#BOTTOM#", '')
            self._content = self.header() + self.body(self._body) + self.footer("<h5>Designed by <a href='http://gti-ia.dsic.upv.es'>GTI-IA DSIC UPV</a></h5>")

        elif page == "/":
            self.setPageTemplate()

            # Check if we have to restart the platform
            if vars.has_key("restart") and vars["restart"] == "true":
                #raise PlatformRestart
                self.server.behav.getAgent().stop()

            cp = ""
            cp = cp + """Below are the jabber server settings. If you wish to know more about jabber servers, please visit <a href="http://www.jabber.org">this</a> link.<br>
                    <table><tr><td>
                    <table class=titulo><tr><td colspan=2>Server Configuration</td></tr></table>
                    <table class=linea><tr><td>Agent Platform address:</td><td class=der>#SERVERNAME#</td></tr></table>
                    <table class=linea><tr><td>System Platform:</td><td class=der>#PLATFORM#</td></tr></table>
                    <table class=linea><tr><td>Python Version:</td><td class=der>#PYTHONVERSION#</td></tr></table>
                    <table class=linea><tr><td>Server Time:</td><td class=der>#TIME#</td></tr></table>
                    <table class=linea><tr><td>Restart Platform:</td><td class=der>#RESTART#</td></tr></table>
                    </td></tr></table>
            """

            self._body = self._body.replace("#MAINCP#", cp)
            self._body = self._body.replace("#BOTTOM#", '')
#            servernames = ""
#            for sn in self.server.xmppd.servernames:
#                servernames = servernames + sn + " "
            self._body = self._body.replace("#SERVERNAME#", self.server.behav.getAgent().getSpadePlatformJID())
            self._body = self._body.replace("#PLATFORM#", sys.platform)
            self._body = self._body.replace("#PYTHONVERSION#", sys.version)
            self._body = self._body.replace("#TIME#", time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()))
            self._body = self._body.replace("#RESTART#", '''<form action="/" method="POST"><input type="hidden" name="restart" value="true"><input type="submit" value="Restart"></form>''')
            self._content = self.header() + self.body(self._body) + self.footer("<h5>Designed by <a href='http://gti-ia.dsic.upv.es'>GTI-IA DSIC UPV</a></h5>")
        else:
            self._content = self.header() + self.body() + self.footer()
        self.wfile.write(self._content)



class SpadePlatform(Agent.PlatformAgent):
    
    class TGWebAdminBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, cfg=None):
            Behaviour.OneShotBehaviour.__init__(self)
            self.cfg = cfg

        def _process(self):
            import pkg_resources
            pkg_resources.require("TurboGears")
            from turbogears import update_config, start_server
            import cherrypy
            cherrypy.lowercase_api = True

            if self.cfg:
                update_config(configfile=self.cfg, modulename="swi.config")
            elif exists(join(dirname(__file__), "setup.py")):
                update_config(configfile="dev.cfg",modulename="swi.config")
            else:
                update_config(configfile="prod.cfg",modulename="swi.config")

            from swi.controllers import Root

            #start_server(Root())


    class WebAdminBehaviour(Behaviour.Behaviour):

        def __init__(self):
            Behaviour.Behaviour.__init__(self)
            self.WEB_ADMIN_PORT = 8008

            #self.server = server
            #XMPPD_SERVER = server

        def onStart(self):
            self.httpd = None
            while not self.httpd:
                try:
                    self.httpd = SocketServer.ThreadingTCPServer(('', self.WEB_ADMIN_PORT), WebAdminHandler)
                    # This connects xmmpd with the request handler and server
                    self.httpd.behav = self
                    #print "WebAdmin: Serving at port", WEB_ADMIN_PORT
                    #thread.start_new_thread(self.httpd.serve_forever, ())
                    print "WebAdmin serving at port "+str(self.WEB_ADMIN_PORT)
                    #self.httpd.serve_forever()
                except:
                    print "WebAdmin Error: could not open port "+str(self.WEB_ADMIN_PORT)
                    time.sleep(5)
                    #if self.httpd: del self.httpd

        def _process(self):
                self.httpd.handle_request()

        def onEnd(self):
                del self.httpd


    class SWIBehaviour(Behaviour.Behaviour):

        def __init__(self):
            Behaviour.Behaviour.__init__(self)
            self.WEB_ADMIN_PORT = 8008

        def onStart(self):
            self.httpd = None
            while not self.httpd:
                try:
                    #self.httpd = SocketServer.ThreadingTCPServer(('', self.WEB_ADMIN_PORT), swi.SWIHandler)
                    self.httpd = BaseHTTPServer.HTTPServer(('', self.WEB_ADMIN_PORT), swi.SWIHandler)
                    # This connects xmmpd with the request handler and server
                    self.httpd.behav = self
                    print "WebAdmin serving at port "+str(self.WEB_ADMIN_PORT)
                except:
                    print "WebAdmin Error: could not open port "+str(self.WEB_ADMIN_PORT)
                    time.sleep(5)

        def _process(self):
            self.httpd.handle_request()

        def onEnd(self):
            del self.httpd

    class RouteBehaviour(Behaviour.Behaviour):
        
        def __init__(self):
            Behaviour.Behaviour.__init__(self)
            
        def _process(self):
            msg = self._receive(True)
            if (msg != None):
                print ">>> SPADE Platform Received a message: " + str(msg)
                if msg.getSender() == self.myAgent.getAID():
                    # Prevent self-loopholes
                    print "###ACC LOOP HOLE"
                    return

                to_list = msg.getReceivers()
                d = {}
                for to in to_list:
                    if not to.getAddresses()[0] in d:
                        d[to.getAddresses()[0]]=list()
                    d[to.getAddresses()[0]].append(to)
                for k,v in d.items():
                    newmsg = msg
                    newmsg.to = v
                    try:
                        protocol, receiver_URI = k.split("://")
                    except:
                        print ">>> Malformed Agent Address URI: " + str(k)
                        break

                    # Check if one of our MTPs handles this protocol
                    #switch(protocol)
                    if protocol in self.myAgent.mtps.keys():
                        print ">>> Message through protocol", str(protocol)
                        #ap = ACLParser.ACLxmlParser()
                        #payload = ap.encodeXML(newmsg)
                        payload = str(newmsg)

                        envelope = Envelope.Envelope()
                        envelope.setFrom(newmsg.getSender())
                        for i in newmsg.getReceivers():
                            envelope.addTo(i)
                        envelope.setAclRepresentation("fipa.acl.rep.string.std")  # Always the same?
                        envelope.setPayloadLength(len(payload))
                        envelope.setPayloadEncoding("US-ASCII")
                        envelope.setDate(BasicFipaDateTime.BasicFipaDateTime())
                        self.myAgent.mtps[protocol].send(envelope, payload)
                    else:
                        # Default case: it's an XMPP message
                        print ">>> Message through protocol XMPP"
                        platform = self.myAgent.getSpadePlatformJID().split(".",1)[1]
                        if not platform in receiver_URI:
                            # Outside platform
                            print ">>> Message for another platform"
                            self.myAgent.send(newmsg, "jabber")
                        else:
                            # THIS platform
                            print ">>> Message for current platform"
                            for recv in v:
                                #self.myAgent._sendTo(newmsg, recv.getName(), "jabber")
                                self.myAgent.send(newmsg, "jabber")

                    """
                    if k[7:] != self.myAgent.getSpadePlatformJID():
                        self.myAgent._sendTo(newmsg, k[7:])
                    else:
                        for recv in v:
                            self.myAgent._sendTo(newmsg, recv.getName())
                    # Reenviamos el msg a todos los destinatarios
                    # Tambien deberiamos comprobar el protocolo y usar una pasarela en el caso de que sea necesario.
                    #print "Message to", to.getName(), "... Posting!"
                    """
            else:
                print "ACC::dying... it shouldn't happen"

    def __init__(self, node, password, server, port, config=None):
        Agent.PlatformAgent.__init__(self, node, password, server, port, config=config, debug=[])

    def _setup(self):
        self.setDefaultBehaviour(self.RouteBehaviour())
        #self.addBehaviour(self.TGWebAdminBehaviour())
        #self.addBehaviour(self.WebAdminBehaviour())
        self.addBehaviour(self.SWIBehaviour())
        #swi.SWIHandler.platform = self
        # Load MTPs
        self.mtps = {}
        for name,mtp in self.config.acc.mtp.items():
        #self.mtps[mtp.protocol] = mtp.instance(name)
            try:
                 mtp_path = "."+os.sep+"spade"+os.sep+"mtp"
                 if os.path.exists(mtp_path):
                      sys.path.append(mtp_path)
                 else:
                    # This path should come from the config file . . .
                      mtp_path = os.sep+"usr"+os.sep+"share"+os.sep+"spade"+os.sep+"mtp"
                      sys.path.append(mtp_path)

                 mod = __import__(name)
                 self.mtps[mtp['protocol']] = mod.INSTANCE(name,self.config,self)

            except Exception, e:
                print "EXCEPTION IMPORTING MTPS: ",str(e)
                _exception = sys.exc_info()
                if _exception[0]:
                     msg='\n'+''.join(traceback.format_exception(_exception[0], _exception[1], _exception[2])).rstrip()
                     print msg

    def takeDown(self):
        for k,mtp in self.mtps.items():
	    try:
                mtp.stop()
		del self.mtps[k]
            except:
                pass


    def getMembers(self,aname):
        msg = ACLMessage.ACLMessage()
        msg.setOntology("spade:x:organization")
        template = Behaviour.ACLTemplate()
        template.setConversationId(msg.getConversationId())
        t = Behaviour.MessageTemplate(template)
        b = self.GetMembersBehav()
        b.msg = msg
        b.aname = aname
        self.addBehaviour(b,t)
        b.join()
        return b.result

    class GetMembersBehav(Behaviour.OneShotBehaviour):
        def _process(self):
            self.result = []
	    self.msg.addReceiver(AID.aid(self.aname, addresses=["xmpp://"+self.aname]))
	    self.msg.setContent("MEMBERS")
	    self.myAgent.send(self.msg)
	    rep = None
	    rep = self._receive(True, 20)
	    if rep:
	        print "The members list arrived"
	        self.result = rep.getContent().split(",")


"""
class FipperPlatform(threading.Thread):
    def __init__(self, params=dict()):
        threading.Thread.__init__(self)
        self.__params = params
        self.__mts = MTS(params)

        try:
            mtp_list = params["mtps"]
            for mtp in mtp_list:
                self.__mts.addMTP(mtp)
        except KeyError:
            pass

    def getMTS(self):
        return self.__mts

    def run(self):
        pass




class MTS:

    def __init__(self, params=dict()):
        self.__platformagents = dict()

    def addAgent(self, agent):
        aid = agent.getAID()
        self.__platformagents[aid] = agent

    def addMTP(self, mtp):
        pass


    def dispatch(self, msg):
        print "Dispatching msg..."
        envelope = msg.getEnvelope()
        to_list = envelope.getTo()
        #for to in to_list:
    #    print to

        for to in to_list:
            if to in self.__platformagents:
                print "Agend finded! Posting..."
                self.__platformagents[to].postMessage(msg)



class MTP:
    def getName(self):
        raise NotImplemented

    def getSupportedProtocols(self):
        raise NotImplemented

    def activate(self, dispatcher, params):
        raise NotImplemented

    def deactivate(self):
        raise NotImplemented

    def deliver(self, addr, envelope, payload):
        raise NotImplemented

"""


