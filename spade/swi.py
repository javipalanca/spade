# encoding: UTF-8
import SimpleHTTPServer
import pyratemp
import os
import sys
import traceback
from AMS import AmsAgentDescription
import DF

class SWIHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    
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
                        d[var[0]] = var[1]
                else:
                    d[var[0]] = ""
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
                eval("self."+str(page))
            except:
                # The controller doesn't exist
                template = "404.pyra"
                ret = {"template":page}
            try:
                if not ret:
                    template, ret = eval("self."+str(page)+"("+s_vars+")")
            except Exception, e:
                #No controller
                _exception = sys.exc_info()
                if _exception[0]:
                    _err = ''.join(traceback.format_exception(_exception[0], _exception[1], _exception[2])).rstrip()
                template = "501.pyra"
                ret = {"template":page, "error":str(_err)}
            
            try:
                t = pyratemp.Template(filename="templates"+os.sep+template, data=ret)
            except:
                #No template
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

    #Controllers
    
    def error404(self):
        return "404.pyra", {"template":"404.pyra"}
    def error501(self):
        return "501.pyra", {"template":"501.pyra", "error":""}
    def error503(self):
        return "503.pyra", {"page":"503.pyra"}

    def index(self):
        import sys
        import time
        servername = self.platform.getDomain()
        platform = self.platform.getName()        
        version = str(sys.version)
        the_time = str(time.ctime())
        return "webadmin_indigo.pyra", dict(servername=servername, platform=platform, version=version, time=the_time)

    def webadmin_indigo(self):
        import sys
        import time
        servername = self.platform.getDomain()
        platform = self.platform.getName()        
        version = str(sys.version)
        the_time = str(time.ctime())
        return "webadmin_indigo.pyra", dict(servername=servername, platform=platform, version=version, time=the_time)

    def agents(self):
        import sys
        import time
        servername = self.platform.getDomain()
        platform = self.platform.getName()        
        version = str(sys.version)
        the_time = str(time.ctime())
        search = self.server.behav.getAgent().searchAgent(AmsAgentDescription())
        for agent in search:
            if not agent.has_key("fipa:state"):
                agent["fipa:state"] = ""
        return "agents.pyra", dict(servername=servername, platform=platform, version=version, time=the_time, agents=search)
        
    def services(self):
        import sys
        import time
        servername = self.platform.getDomain()
        platform = self.platform.getName()        
        version = str(sys.version)
        the_time = str(time.ctime())
        search = self.server.behav.getAgent().searchService(DF.DfAgentDescription())
        #for service in search:
        #   if not agent.has_key("fipa:state"):
        #        agent["fipa:state"] = ""
        # Create a service-indexed dictionary of services, not an agent-indexed one
        servs = {}
        idn = 0
        for dad in search:
            for service in dad.getServices():
                if service.getType() not in servs.keys():
                    servs[service.getType()] = {}
                servs[service.getType()][idn] = {}
                servs[service.getType()][idn]["name"] = str(service.getName())
                servs[service.getType()][idn]["provider"] = str(dad.getAID().getName())
                servs[service.getType()][idn]["addresses"] = ""
                for address in dad.getAID().getAddresses():
                    servs[service.getType()][idn]["addresses"] += str(address)+" "
                idn += 1
        print servs
        return "services.pyra", dict(servername=servername, platform=platform, version=version, time=the_time, services=servs)

    def sendmessage(self):#, to):
        import sys
        import time
        servername = self.platform.getDomain()
        platform = self.platform.getName()        
        version = str(sys.version)
        the_time = str(time.ctime())

        search = self.server.behav.getAgent().searchAgent(AmsAgentDescription())
        agents = []
        for agent in search:
            agents.append(agent.getAID().getName())

        return "message.pyra", dict(servername=servername, platform=platform, version=version, time=the_time, keys=agents)


