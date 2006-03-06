from xmpp import *

class accPlugIn(PlugIn):
	NS='jabber:x:fipa'
        #NS=''
        def do(self, uno, dos):
                print "####################################"
                print "####################################"
                print "####################################"
                print "DO THE KUNG FU " + str(uno) + " " + str(dos)
                print "####################################"
                print "####################################"
                print "####################################"

        def plugin(self,server):
                self._data = {}
                #server.Dispatcher.RegisterNamespaceHandler(NS_CLIENT,self.routerHandler)
                #server.Dispatcher.RegisterNamespaceHandler(NS_SERVER,self.routerHandler)
                #server.Dispatcher.RegisterHandler('polla',self.do)
		print "#################"
		print "ACC PLUGIN LOADED"
		print "#################"

