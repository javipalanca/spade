# -*- coding: utf-8 -*-
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
import Cookie
import string
import time

from threading import Thread

chars = string.ascii_letters + string.digits
sessionDict = {}  # dictionary mapping session id's to session objects


class HTTP_REDIRECTION(Exception):
    pass


class WUI(Thread):
    def __init__(self, owner):
        Thread.__init__(self)
        self.setName("WUI " + str(owner.getName()))
        self.owner = owner
        self.httpd = None
        self.port = 8009
        self.template_path = ""
        # Try to get SPADE's default template path
        tpath = os.path.realpath(pyratemp.__file__)  # /Users/foo/devel/trunk/spade
        tpath = tpath.rsplit(os.sep, 1)  # ["/Users/foo/devel/trunk", "spade"]
        self.spade_path = tpath[0]  # +os.sep+os.pardir
        #self.owner.DEBUG("SPADE path: " + self.spade_path,"warn")

        self.controllers = {}

        self.is_running = False

    def run(self):
        timeout = 5
        while self.httpd is None and timeout > 0:
            try:
                SocketServer.ThreadingTCPServer.allow_reuse_address = True
                self.httpd = SocketServer.ThreadingTCPServer(('', self.port), WUIHandler)
                self.httpd.owner = self
                self.httpd.timeout = 1
            except Exception:
                self.port = random.randint(20000, 30000)
            timeout -= 1
            time.sleep(1)

        if self.httpd is not None:
            self.owner.DEBUG("WebUserInterface serving at port " + str(self.port))
            self.registerController("error404", self.error404)
            self.registerController("error501", self.error501)
            self.registerController("error503", self.error503)

            self.notifyAMS()

            self.is_running = True
            self.httpd.serve_forever(poll_interval=0.5)
            self.owner.DEBUG("WebUserInterface(" + str(self.port) + ") finished", 'ok')
        else:
            self.owner.DEBUG("Could not set up WebUserInterface! at port " + str(self.port), 'err')

    def isRunning(self):
        return self.is_running

    def stop(self):
        self.is_running = False
        if self.httpd is not None:
            try:
                self.httpd.shutdown()
                self.httpd.server_close()
            except Exception, e:
                pass
            self.httpd = None

    def setPort(self, port):
        self.port = port

    def setTemplatePath(self, path):
        self.template_path = os.path.realpath(path)

    def registerController(self, name, controller):
        self.controllers[name] = controller

    def unregisterController(self, name):
        del self.controllers[name]

    def notifyAMS(self):
        """Notify AMS of current AWUI URL"""
        #return
        from spade.AMS import AmsAgentDescription
        aad = AmsAgentDescription()
        aid = self.owner.getAID()
        try:
            ip = socket.gethostbyname_ex(socket.gethostname())[2][0]
        except:
            ip = "127.0.0.1"
        aid.addAddress("awui://" + str(ip) + ":" + str(self.port))
        aad.setAID(aid)
        self.owner.modifyAgent(aad)

    #Controllers

    def error404(self):
        return "404.pyra", {"template": "404.pyra"}

    def error501(self):
        return "501.pyra", {"template": "501.pyra", "error": ""}

    def error503(self):
        return "503.pyra", {"page": "503.pyra"}


class SessionElement(object):
    """Arbitrary objects, referenced by the session id"""
    pass


def generateRandom(length):
    """Return a random string of specified length (used for session id's)"""
    return ''.join([random.choice(chars) for i in range(length)])


class WUIHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def log_message(format, *args):
        pass

    def Session(self):
        """Session management
        If the client has sent a cookie named sessionId, take its value and
        return the corresponding SessionElement objet, stored in
        sessionDict
        Otherwise create a new SessionElement objet and generate a random
        8-letters value sent back to the client as the value for a cookie
        called sessionId"""
        if "sessionId" in self.cookie:
            sessionId = self.cookie["sessionId"].value
        else:
            sessionId = generateRandom(8)
            self.cookie["sessionId"] = sessionId
        try:
            sessionObject = sessionDict[sessionId]
        except KeyError:
            sessionObject = SessionElement()
            sessionDict[sessionId] = sessionObject
        return sessionObject

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

        if page == "/":
            page = "/index"

        if page.startswith("/"):
            page = page[1:]

        try:
            req_vars = self.getVars("?" + self._POST_REQ)
        except:
            req_vars = self.getVars(request[1])

        s_vars = ""
        for k, v in req_vars.items():
            if k:
                v = str(v)
                if not v.startswith('"') and not v.startswith("'") and not v.startswith("["):
                    v = '"' + v + '"'
                s_vars += str(k) + "=" + v + ","
        if s_vars.endswith(","):
            s_vars = s_vars[:-1]

        #session management
        if 'cookie' in self.headers:
            self.cookie = Cookie.SimpleCookie(self.headers.getheader("cookie"))
        else:
            self.cookie = Cookie.SimpleCookie()

        # Switch page
        #if page.endswith("css"):
        if page.endswith(".css") or page.endswith(".png") or page.endswith(".html") or page.endswith(".js"):
            #self.copyfile(urllib.urlopen(self.path), self.wfile)
            if page.endswith(".js"):
                content_type = 'application/javascript'
            elif page.endswith(".css"):
                content_type = 'text/css'
            else:
                content_type = 'text/plain'
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

            except:
                self.server.owner.owner.DEBUG("Could not open file: " + page, "err")

            try:
                self.send_response(200)
                for morsel in self.cookie.values():
                    self.send_header('Set-Cookie', morsel.output(header='').lstrip())
                self.send_header('Content-type', content_type)
                self.end_headers()
                f = open(page, "r")
                self.copyfile(f, self.wfile)
                f.close()
            except:
                self.server.owner.owner.DEBUG(str(sys.exc_info()), "err")

        else:
            sess = self.Session()
            try:
                # Check wether controller exists
                # Get the first section of the URL path (e.g. the "admin" of "admin/foo/bar")
                eval("self.server.owner.controllers['" + str(page) + "']")
            except:
                # The controller doesn't exist
                _exception = sys.exc_info()
                if _exception[0]:
                    _err = ''.join(traceback.format_exception(_exception[0], _exception[1], _exception[2])).rstrip()
                template = "404.pyra"
                ret = {"template": page, "error": str(_err), "name": self.server.owner.owner.getName()}
                code = 404
            try:
                if not ret:
                    func = self.server.owner.controllers[str(page)]
                    #session object
                    sess.url = page
                    func.__self__.session = sess
                    template, ret = eval("func" + "(" + s_vars + ")")
                    code = 200
            except HTTP_REDIRECTION, url:
                self.send_response(302)
                for morsel in self.cookie.values():
                    self.send_header('Set-Cookie', morsel.output(header='').lstrip())
                self.send_header('Location', url)
                self.end_headers()
                self.wfile.write("")
                return

            except Exception, e:
                #No controller
                _exception = sys.exc_info()
                if _exception[0]:
                    _err = ''.join(traceback.format_exception(_exception[0], _exception[1], _exception[2])).rstrip()
                template = "501.pyra"
                ret = {"template": page, "error": str(_err), "name": self.server.owner.owner.getName()}
                code = 501

            #check if user is authenticated
            authenticated = False
            if hasattr(sess, "user_authenticated"):
                if sess.user_authenticated is True:
                    authenticated = True
            ret['authenticated'] = authenticated
            try:
                if os.path.exists(self.server.owner.template_path + os.sep + template):
                    t = pyratemp.Template(filename=self.server.owner.template_path + os.sep + template, data=ret)
                else:
                    #olddir = os.path.curdir
                    #os.chdir(self.server.spade_path)
                    t = pyratemp.Template(filename=self.server.owner.spade_path + os.sep + "templates" + os.sep + template, data=ret)
                    #print template, ret
                    #os.chdir(olddir)
            except pyratemp.TemplateSyntaxError, e:
                _exception = sys.exc_info()
                if _exception[0]:
                    _err = ''.join(traceback.format_exception(_exception[0], _exception[1], _exception[2])).rstrip()
                t = pyratemp.Template(filename=self.server.owner.spade_path + os.sep + "templates" + os.sep + "501.pyra", data={"template": template, "error": str(_err), "name": self.server.owner.owner.getName(), "authenticated":authenticated})
                code = 501
            except Exception, e:
                #No template
                _exception = sys.exc_info()
                if _exception[0]:
                    _err = ''.join(traceback.format_exception(_exception[0], _exception[1], _exception[2])).rstrip()
                #print "###", _err, "###"
                t = pyratemp.Template(filename=self.server.owner.spade_path + os.sep + "templates" + os.sep + "503.pyra", data={"page": template, "name": self.server.owner.owner.getName(), "authenticated":authenticated})
                code = 503
            try:
                result = t()
            except Exception, e:
                #Error in template
                _exception = sys.exc_info()
                if _exception[0]:
                    _err = ''.join(traceback.format_exception(_exception[0], _exception[1], _exception[2])).rstrip()
                t = pyratemp.Template(filename=self.server.owner.spade_path + os.sep + "templates" + os.sep + "501.pyra", data={"template": template, "error": str(_err), "name": self.server.owner.owner.getName(), "authenticated":authenticated})
                result = t()
                code = 501

            r = result.encode("ascii", 'xmlcharrefreplace')

            self.send_response(code)
            for morsel in self.cookie.values():
                self.send_header('Set-Cookie', morsel.output(header='').lstrip())
            self.end_headers()
            self.wfile.write(r)
