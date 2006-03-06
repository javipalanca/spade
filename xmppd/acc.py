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

	def getRealTo(self, mess):
		"""
		return the real JID of the receiver of a "jabber:x:fipa" message
		"""
		self.DEBUG("ACC PLUGIN: received " + str(mess), "info")
		envxml=None
            	payload=mess.getBody()
            	children = mess.getChildren()
		self.DEBUG("ACC PLUGIN: analyzing message", "info")
            	for child in children:
                	if (child.getNamespace() == "jabber:x:fipa") or (child.getNamespace() == u"jabber:x:fipa"):
                    		envxml = child.getData()
            	if (envxml != None):
			self.DEBUG("ACC PLUGIN: found envelope", "info")
                	xc = XMLCodec.XMLCodec()
                	envelope = xc.parse(str(envxml))
			self.DEBUG("ACC PLUGIN: envelope decoded", "info")

                	if   str(envelope.getAclRepresentation()).lower() == "fipa.acl.rep.string.std":
                        	ac = ACLParser.ACLParser()
                	elif str(envelope.getAclRepresentation()).lower() == "fipa.acl.rep.xml.std":
                        	ac = ACLParser.ACLxmlParser()
                	else:
                        	self.DEBUG("ACC PLUGIN: NO PARSER!", "info")

		ACLmsg = ac.parse(str(payload))	
		self.DEBUG("ACC PLUGIN: getRealTo = " + str(ACLmsg.getReceivers()), "info")
		receiver_names = []
		for item in ACLmsg.getReceivers():
			receiver_names.append(str(item.getName()))
		return receiver_names

