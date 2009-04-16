import SimpleHTTPServer
import pyratemp

class SWIHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    
    def __init__(self, request, client_address, server):

        SWIHandler.templates = dict()
        SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(self, request, client_address, server)

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
                #print var
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

	    #print "_POST_REQ:", self._POST_REQ

	    self.do_GET()


    def do_GET(self):
        """
        GET petitions handler
        """
        #print "DO_GET"

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
	        
        print page, vars
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
            print "Executing "+page
            template, ret = eval("self."+str(page)+"("+s_vars+")")
                
            if template in SWIHandler.templates.keys():
                t = SWIHandler.templates[template]
            else:
                try:
                    print "lloking for template ",template
                    t = pyratemp.Template(filename="templates/"+template)
                    SWIHandler.templates[template]=t
                except:
                        print "NO TEMPLATE"
                        return ""
                
                
            args=""
            for k,v in ret.items():
                args+= str(k) + "=" + str(v)+","
            if args.endswith(","): args = args[:-1]
            
            result = eval(str(t)+"("+args+")")
                
            r = result.encode("ascii", 'xmlcharrefreplace')
            
            self.wfile.write(r)

    #Controllers
    
    def index(self):
        import sys
        import time
        servername = self.platform.getDomain()
        platform = self.platform.getName()        
        version = str(sys.version)
        the_time = str(time.ctime())
        return "webadmin.pyra", dict(servername=servername, platform=platform, version=version, time=the_time)