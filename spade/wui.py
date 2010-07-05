# encoding: UTF-8
import traceback
import SocketServer
import SimpleHTTPServer
import BaseHTTPServer
import pyratemp
import os
import sys
import traceback
import urllib
import time
import random
import socket

from threading import Thread

class WUI(Thread):
    def __init__(self, owner):
        Thread.__init__(self)
        self.owner = owner
        self.httpd = None
        self.port = 8009
        self.template_path = "" 
        # Try to get SPADE's default template path
        tpath = os.path.realpath(pyratemp.__file__)  # /Users/foo/devel/trunk/spade
        tpath = tpath.rsplit(os.sep,1)  # ["/Users/foo/devel/trunk", "spade"]
        self.spade_path = tpath[0]+os.sep+os.pardir
        #self.owner.DEBUG("SPADE path: " + self.spade_path,"warn")
        
        self.controllers = {}
        
        self.is_running = False
        
        
    def run(self):

        while not self.httpd:
             try:
                 self.httpd = SocketServer.ThreadingTCPServer(('', self.port), WUIHandler)
                 self.httpd.owner = self
                 self.httpd.timeout = 1
                 #print "WebUserInterface serving at port "+str(self.port)
                 self.notifyAMS()
             except:
                 self.port = random.randint(1024,65536)
                 
        self.owner.DEBUG("WebUserInterface serving at port "+str(self.port))
        self.registerController("error404", self.error404)
        self.registerController("error501", self.error501)
        self.registerController("error503", self.error503)

        self.is_running = True
        while self.isRunning():
            self.httpd.handle_request()

    def isRunning(self):
        return self.is_running
        
    def stop(self):
        self.is_running = False
        
    def setPort(self, port):
        self.port = port
        
    def setTemplatePath(self,path):
        self.template_path = os.path.realpath(path)
        
    def registerController(self, name, controller):
        self.controllers[name] = controller
            
    def unregisterController(self, name):
        del self.controllers[name]
    
    def notifyAMS(self):
        """Notify AMS of current AWUI URL"""
        msg = self.owner.newMessage()
        msg.setSender(self.owner.getAID())
        msg.setPerformative("request")
        msg.setLanguage("rdf")
        msg.setOntology("fipa-agent-management")  # Pretend to be a FIPA message
        co = self.owner.newContentObject()
        co.addNamespace("http://spade2.googlecode.com", "spade")
        co["spade:action"] = "register_awui"
        co["spade:argument"] = str(socket.gethostbyname(socket.gethostname()))+":"+str(self.port)
        msg.setContentObject(co)
        msg.addReceiver(self.owner.getAMS())
        self.owner.send(msg)
            
    #Controllers

    def error404(self):
        return "404.pyra", {"template":"404.pyra"}
    def error501(self):
        return "501.pyra", {"template":"501.pyra", "error":""}
    def error503(self):
        return "503.pyra", {"page":"503.pyra"}

class WUIHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    
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
            for raw in raw_vars.split("&"):
                #print raw
                var = raw.split("=")
                if len(var) > 1:
                    # Check if this is a multi-valued var
                    if var[0] in d.keys():
                        try:
                            # Try to append value to the list
                            d[var[0]].append(urllib.unquote_plus(var[1]))
                        except:
                            # Create a list with the current value and append the new one
                            d[var[0]] = [d[var[0]]]
                            d[var[0]].append(urllib.unquote_plus(var[1]))
                    else:
                        d[urllib.unquote_plus(var[0])] = urllib.unquote_plus(var[1])
                else:
                    d[urllib.unquote_plus(var[0])] = ""
        except:
            pass

        return d

    def do_POST(self):

        self._POST_REQ = ""
        try:
            length = int(self.headers.getheader('content-length'))
            self._POST_REQ = self.rfile.read(length)
        except:
            pass

        self.do_GET()


    def do_GET(self):
        """
        GET petitions handler
        """

        ret = None
        request = self.raw_requestline.split()
        page = self.getPage(request[1])

        if page == "/": page = "/index"

        if page.startswith("/"): page = page [1:]

        try:
            vars = self.getVars("?"+self._POST_REQ)
        except:
            vars = self.getVars(request[1])
        
        s_vars=""
        for k,v in vars.items():
            if k:
                v = str(v)
                if not v.startswith('"') and not v.startswith("'") and not v.startswith("["):
                    v = '"'+ v +'"'
                s_vars+= str(k) + "=" + v +","
        if s_vars.endswith(","): s_vars = s_vars[:-1]
            
        # Switch page
        #if page.endswith("css"):
        if page.endswith(".css") or page.endswith(".png") or page.endswith(".html") or page.endswith(".js"):
            #self.copyfile(urllib.urlopen(self.path), self.wfile)
            try:
                if os.path.exists(self.server.owner.template_path + os.sep + page):
                    page = self.server.owner.template_path + os.sep + page
                elif os.path.exists(self.server.owner.spade_path + os.sep + "templates" + os.sep + page):
                    page = self.server.owner.spade_path + os.sep + "templates" + os.sep + page
                elif page.startswith("doc") and os.path.exists(self.server.owner.spade_path + os.sep + page):
                    # For serving the SPADE API docs from the WUI
                    page = self.server.owner.spade_path + os.sep + page
                else:
                    raise Exception
                f = open(page, "r")
                self.copyfile(f, self.wfile)
                f.close()
            except:
                self.server.owner.owner.DEBUG("Could not open file: "+ page, "err")
        
        else:
            try:
                # Check wether controller exists
                # Get the first section of the URL path (e.g. the "admin" of "admin/foo/bar")
                eval("self.server.owner.controllers['"+str(page)+"']")
            except:
                # The controller doesn't exist
                _exception = sys.exc_info()
                if _exception[0]:
                    _err = ''.join(traceback.format_exception(_exception[0], _exception[1], _exception[2])).rstrip()
                template = "404.pyra"
                ret = {"template":page, "error":str(_err),"name":self.server.owner.owner.getName()}
            try:
                if not ret:
                    func = self.server.owner.controllers[str(page)]                    
                    template, ret = eval("func"+"("+s_vars+")")
            except Exception, e:
                #No controller
                _exception = sys.exc_info()
                if _exception[0]:
                    _err = ''.join(traceback.format_exception(_exception[0], _exception[1], _exception[2])).rstrip()
                template = "501.pyra"
                ret = {"template":page, "error":str(_err)}
            
            try:
                if os.path.exists(self.server.owner.template_path+os.sep+template):
                    t = pyratemp.Template(filename=self.server.owner.template_path+os.sep+template, data=ret)
                else:
                    olddir = os.path.curdir
                    #os.chdir(self.server.spade_path)
                    t = pyratemp.Template(filename=self.server.owner.spade_path+os.sep+"templates"+os.sep+template, data=ret)
                    #os.chdir(olddir)
            except pyratemp.TemplateSyntaxError, e:
                _exception = sys.exc_info()
                if _exception[0]:
                    _err = ''.join(traceback.format_exception(_exception[0], _exception[1], _exception[2])).rstrip()
                t = pyratemp.Template(filename=self.server.owner.spade_path+os.sep+"templates"+os.sep+"501.pyra", data={"template":template, "error":str(_err),"name":self.server.owner.owner.getName()})
            except Exception, e:
                #No template
                _exception = sys.exc_info()
                if _exception[0]:
                    _err = ''.join(traceback.format_exception(_exception[0], _exception[1], _exception[2])).rstrip()
                #print "###", _err, "###"
                t = pyratemp.Template(filename=self.server.owner.spade_path+os.sep+"templates"+os.sep+"503.pyra", data={"page":template,"name":self.server.owner.owner.getName()})
            try:
                result = t()
            except Exception, e:
                #Error in template
                _exception = sys.exc_info()
                if _exception[0]:
                    _err = ''.join(traceback.format_exception(_exception[0], _exception[1], _exception[2])).rstrip()
                t = pyratemp.Template(filename=self.server.owner.spade_path+os.sep+"templates"+os.sep+"501.pyra", data={"template":template, "error":str(_err),"name":self.server.owner.owner.getName()})
                result = t()
                
            r = result.encode("ascii", 'xmlcharrefreplace')
            
            self.wfile.write(r)






