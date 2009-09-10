# encoding: UTF-8
import traceback
import SocketServer
import SimpleHTTPServer
import BaseHTTPServer
import pyratemp
import os
import sys
import traceback
from AMS import AmsAgentDescription
import DF

import urllib
import time
import random

from threading import Thread

class WUI(Thread):
    def __init__(self, owner):
        Thread.__init__(self)
        self.httpd = None
        self.port = 8009
        self.owner = owner
        self.controllers = {}
        
        self.is_running = False
        
    def run(self):

        while not self.httpd:
             try:
                 self.httpd = SocketServer.ThreadingTCPServer(('', self.port), WUIHandler)
                 self.httpd.owner = self
                 #self.httpd.controllers = self.controllers
                 print "WebUserInterface serving at port "+str(self.port)
             except:
                 self.port = random.randint(1024,65536)
                 #print "WebUserInterface Error: could not open port "+str(self.port)
                 #time.sleep(5)
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
        
    def registerController(self, name, controller):
        #if self.httpd:
        #self.httpd.controllers[controller.func_name] = controller
        #else:
        self.controllers[name] = controller
            
    def unregisterController(self, name):
        #if self.httpd:
        #   del self.httpd.controllers[controller.func_name]
        #else:
        del self.controllers[name]
            
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
                            d[var[0]].append(var[1])
                        except:
                            # Create a list with the current value and append the new one
                            d[var[0]] = [d[var[0]]]
                            d[var[0]].append(var[1])
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
            s_vars+= str(k) + "=" + str(v)+","
        if s_vars.endswith(","): s_vars = s_vars[:-1]
            
        # Switch page
        #if page.endswith("css"):
        if "." in page:
            #self.copyfile(urllib.urlopen(self.path), self.wfile)
            try:
                f = open(page, "r")
                self.copyfile(f, self.wfile)
                f.close()
            except:
                print "Could not open file: ", page
    
        else:
            try:
                # Check wether controller exists
                eval("self.server.owner.controllers['"+str(page)+"']")
            except:
                # The controller doesn't exist
                _exception = sys.exc_info()
                if _exception[0]:
                    _err = ''.join(traceback.format_exception(_exception[0], _exception[1], _exception[2])).rstrip()
                template = "404.pyra"
                ret = {"template":page, "error":str(_err)}
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
                t = pyratemp.Template(filename="templates"+os.sep+template, data=ret)
            except Exception, e:
                #No template
                _exception = sys.exc_info()
                if _exception[0]:
                    _err = ''.join(traceback.format_exception(_exception[0], _exception[1], _exception[2])).rstrip()
                t = pyratemp.Template(filename="templates"+os.sep+"503.pyra", data={"page":template})
            try:
                result = t()
            except Exception, e:
                #Error in template
                _exception = sys.exc_info()
                if _exception[0]:
                    _err = ''.join(traceback.format_exception(_exception[0], _exception[1], _exception[2])).rstrip()
                t = pyratemp.Template(filename="templates"+os.sep+"501.pyra", data={"template":template, "error":str(_err)})
                result = t()
                
            r = result.encode("ascii", 'xmlcharrefreplace')
            
            self.wfile.write(r)






