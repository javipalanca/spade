from xmpp import *
from spade import *
from spade.ACLMessage import *

class accPlugIn(PlugIn):
	#NS='jabber:x:fipa'
        NS=''
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
                #server.Dispatcher.RegisterNamespaceHandler(NS_SERVER,self.routerHandler)
                #server.Dispatcher.RegisterHandler('polla',self.do)
		#print "#################"
		#print "ACC PLUGIN LOADED"
		#print "#################"

	def getRealTo(self, msg):
		"""
		return the real JID of the receiver of a "jabber:x:fipa" message
		"""
		envxml=None
            	payload=mess.getBody()
            	children = mess.getChildren()
            	for child in children:
                	if (child.getNamespace() == "jabber:x:fipa") or (child.getNamespace() == u"jabber:x:fipa"):
                    		envxml = child.getData()
            	if (envxml != None):
                	xc = XMLCodec.XMLCodec()
                	envelope = xc.parse(str(envxml))

                	if   str(envelope.getAclRepresentation()).lower() == "fipa.acl.rep.string.std":
                        	ac = ACLParser.ACLParser()
                	elif str(envelope.getAclRepresentation()).lower() == "fipa.acl.rep.xml.std":
                        	ac = ACLParser.ACLxmlParser()
                	else:
                        	print "NO TENGO PARSER!"
	
		self.DEBUG(">> ACC: getRealTo = " + str(envelope.getReceivers()), "info")
		return envelope.getReceivers()

