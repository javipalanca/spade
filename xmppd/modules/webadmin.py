# -*- coding: utf-8 -*-
import SocketServer
import SimpleHTTPServer
import urllib
import copy
import thread
from threading import Thread
import time
import sys
import os
from spade import ACLMessage
from xmpp import *

WEB_ADMIN_PORT = 8008


class WebAdminHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
#class WebAdminHandler(CGIHTTPServer.CGIHTTPRequestHandler):

    _body_template = "<table><tr><td class=cabecera colspan=2>#TOP#</td></tr><tr><td class=lateral>#MENU_LEFT#</td><td>#PANEL_RIGHT#</td></tr><tr><td>#BOTTOM#</td></tr></table>"

    def header(self, title="SPADE WEB ADMIN"):
        try:
            os.stat("modules/web/webadmin.css")
            return "<html><head><link rel=stylesheet type='text/css' href='modules/web/webadmin.css'><title>" + title + "</title></head>"
        except:
            return "<html><head><link rel=stylesheet type='text/css' href='xmppd/modules/web/webadmin.css'><title>" + title + "</title></head>"

    def body(self, body=""):
        return "<body>" + str(body)  # + "</body>"

    def footer(self, foot=""):
        return foot + "</body>" + "</html>"

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
                print raw
                var = raw.split("=")
                if len(var) > 1:
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
        to = to.replace("%40", "@")
        to = to.replace("%2F", "/")
        stanza = Message(to=to, body=msg, frm=self.server.xmppd.servernames[0])
        print "CREATED STANZA: " + str(stanza)
        s = None
        s = self.server.xmppd.getsession(to)
        if s:
            print "SENDING MSG TO " + to
            s.enqueue(stanza)
        else:
            print "NO SESSION FOR MESSAGE"
        return

    def sendFIPAMsg(self, to, performative, content):
        msg = ACLMessage.ACLMessage()
        msg.addReceiver(to)
        msg.setPerformative(performative)
        msg.setContent(content)
        #self.myAgent.send(msg)

    def setPageTemplate(self):
        self._body = copy.copy(self._body_template)
        self._body = self._body.replace("#TOP#", "<h1>SPADE WEB ADMIN</h1>")
        self._body = self._body.replace("#MENU_LEFT#", '<a class=lateral href="/">Main</a><br/><a class=lateral href="/pref">Preferences</a><br/><a class=lateral href="/clients">Active Clients</a><br/><a class=lateral href="/plugins">Plugins</a>')
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
            vars = self.getVars("?" + self._POST_REQ)
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
        elif page == "/send":
            self.setPageTemplate()
            cp = """<table><tr><td>Send a Jabber message to agent """ + vars['to'] + """<br/>
            <FORM ACTION="/clients" METHOD="POST">
            <INPUT TYPE="text" NAME="msg"><BR/>
            <INPUT TYPE="hidden" NAME="to" VALUE='""" + vars['to'] + """'>
            <INPUT TYPE="hidden" NAME="jabber" VALUE="YES">
            <INPUT TYPE="submit" VALUE="Send">
            </FORM></td></tr>
            """
            cp = cp + """
            <tr><td>
            Send a FIPA message to agent """ + vars['to'] + """<br/>
            <FORM ACTION="/clients" METHOD="POST">
            <SELECT NAME="performative">
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
            <INPUT TYPE="text" NAME="content">Content<BR/>
            <INPUT TYPE="hidden" NAME="to" VALUE='""" + vars['to'] + """'>
            <INPUT TYPE="hidden" NAME="fipa" VALUE="YES">
            <INPUT TYPE="submit" VALUE="Send">
            </FORM>
            </td></tr>
            """
            self._body = self._body.replace("#MAINCP#", cp)
            self._body = self._body.replace("#BOTTOM#", '')
            self._content = self.header() + self.body(self._body) + self.footer("<h5>Designed by <a href='http://gti-ia.dsic.upv.es'>GTI-IA DSIC UPV</a></h5>")

        elif page == "/clients":
            # First of all, see if we need to send a message
            if "jabber" in vars:
                if "to" in vars and "msg" in vars:
                    # Yup, a message
                    self.sendMsg(vars["to"], vars["msg"])
            elif "fipa" in vars:
                self.sendFIPAMsg(vars["to"], vars["performative"], vars["content"])

            self.setPageTemplate()
            cp = """Below there is the list of the currently connected clients.<br/>
            <table><tr><th colspan=2>Active Connections</th></tr>"""
            i = 0
            # We are going to list all the current routes present in the server
            for cl in self.server.xmppd.routes.keys():
                # Now, for the presence information
                j = JID(str(cl)).getStripped()
                res = JID(str(cl)).getResource()
                try:
                    #print "J", j, "RES", res
                    pres_data = self.server.xmppd.Router._data[j]
                    #print "PRES_DATA: " + str(pres_data)
                    pres = pres_data[res]
                    #print "PRES: " + str(pres)
                except Exception, e:
                    # There was no presence information
                    #print "EXCEPCION EN LA PRESENCIA"
                    #print str(e)
                    pres = ""

                # Odd or even
                if i % 2 == 1:
                    cp = cp + """<tr><td class=impar>"""
                else:
                    cp = cp + """<tr><td class=par>"""
                cp = cp + """<a href='/send?to=""" + str(cl) + """'>""" + str(cl) + """</a></td><td>""" + simplexml.XMLescape(str(pres)) + """</td></tr>"""

                # Update the even/odd index
                i = i + 1

            cp = cp + """</table>"""
            self._body = self._body.replace("#MAINCP#", cp)
            self._body = self._body.replace("#BOTTOM#", '')
            self._content = self.header() + self.body(self._body) + self.footer("<h5>Designed by <a href='http://gti-ia.dsic.upv.es'>GTI-IA DSIC UPV</a></h5>")

        elif page == "/":
            self.setPageTemplate()
            cp = """Below are the jabber server settings. If you wish to know more about jabber servers, please visit <a href="http://www.jabber.org">this</a> link.<br>
                    <table><tr><td>
                    <table class=titulo><tr><td colspan=2>Server Configuration</td></tr></table>
                    <table class=linea><tr><td>Server name:</td><td align="right">#SERVERNAME#</td></tr></table>
                    <table class=linea><tr><td>System Platform:</td><td align="right">#PLATFORM#</td></tr></table>
                    <table class=linea><tr><td>Python Version:</td><td align="right">#PYTHONVERSION#</td></tr></table>
                    <table class=linea><tr><td>Time:</td><td align="right">#TIME#</td></tr></table>
                    </td></tr></table>
            """

            self._body = self._body.replace("#MAINCP#", cp)
            self._body = self._body.replace("#BOTTOM#", '')
            servernames = ""
            for sn in self.server.xmppd.servernames:
                servernames = servernames + sn + " "
            self._body = self._body.replace("#SERVERNAME#", servernames)
            self._body = self._body.replace("#PLATFORM#", sys.platform)
            self._body = self._body.replace("#PYTHONVERSION#", sys.version)
            self._body = self._body.replace("#TIME#", time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()))
            self._content = self.header() + self.body(self._body) + self.footer("<h5>Designed by <a href='http://gti-ia.dsic.upv.es'>GTI-IA DSIC UPV</a></h5>")
        else:
            self._content = self.header() + self.body() + self.footer()
        self.wfile.write(self._content)


class WebAdmin(PlugIn):
    NS = ''

    def plugin(self, server):
        self.server = server
        XMPPD_SERVER = server
        try:
            self.httpd = None
            self.httpd = SocketServer.ThreadingTCPServer(('', WEB_ADMIN_PORT), WebAdminHandler)
            # This connects xmmpd with the request handler and server
            self.httpd.xmppd = self.server
            self.httpd.server_name = "SPADE_WEB_ADMIN"
            self.httpd.server_port = str(WEB_ADMIN_PORT)
            self.DEBUG("WebAdmin serving at port " + str(WEB_ADMIN_PORT), "ok")
            #print "WebAdmin: Serving at port", WEB_ADMIN_PORT
            thread.start_new_thread(self.httpd.serve_forever, ())
            #self.httpd.serve_forever()
        except:
            self.DEBUG("WebAdmin Error: could not open port " + str(WEB_ADMIN_PORT), "error")
            #if self.httpd: del self.httpd

    def plugout(self):
        self.DEBUG("WebAdmin plugging out", "info")
        if self.httpd:
            del self.httpd


# Debug main code
if __name__ == "__main__":
    pass
