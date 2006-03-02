# -*- coding: cp1252 -*-
import sys
import xmpp
import threading
import thread
import Queue
import time
import MessageReceiver
import AID
import XMLCodec
import ACLParser
import Envelope
import ACLMessage
import BasicFipaDateTime
import Behaviour
import SL0Parser
#from AMS import AmsAgentDescription

# Taken from xmpp debug
color_none         = chr(27) + "[0m"
color_black        = chr(27) + "[30m"
color_red          = chr(27) + "[31m"
color_green        = chr(27) + "[32m"
color_brown        = chr(27) + "[33m"
color_blue         = chr(27) + "[34m"
color_magenta      = chr(27) + "[35m"
color_cyan         = chr(27) + "[36m"
color_light_gray   = chr(27) + "[37m"
color_dark_gray    = chr(27) + "[30;1m"
color_bright_red   = chr(27) + "[31;1m"
color_bright_green = chr(27) + "[32;1m"
color_yellow       = chr(27) + "[33;1m"
color_bright_blue  = chr(27) + "[34;1m"
color_purple       = chr(27) + "[35;1m"
color_bright_cyan  = chr(27) + "[36;1m"
color_white        = chr(27) + "[37;1m"


class AbstractAgent(MessageReceiver.MessageReceiver):
    """
    Abstract Agent
    only for heritance
    Child classes: PlatformAgent, Agent
    """
    
    def __init__(self, agentjid, serverplatform):
	"""
	inits an agent with a JID (user@server) and a platform JID (acc.platformserver)
	"""
        MessageReceiver.MessageReceiver.__init__(self)
        self._aid = AID.aid(name=agentjid, addresses=[ "xmpp://acc."+serverplatform ])
        self._jabber = None
        self._serverplatform = serverplatform
        self._defaultbehaviour = None
        self._behaviourList = dict()
        self._alive = True
	self._forceKill = threading.Event()
	self._forceKill.clear()

	self.setName(str(agentjid))


    def _jabber_messageCB(self, conn, mess):
	"""
	message callback
	read the message envelope and post the message to the agent
	"""
        if (mess.getError() == None):
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

		#print str(payload)
                ACLmsg = ac.parse(str(payload))
	        content = ACLmsg.getContent()
        	comillas_esc = '"'
	        barrainv_esc = '\\'
	        mtmp1 = comillas_esc.join(content.split('\\"'))
        	mtmp2 = barrainv_esc.join(mtmp1.split('\\\\'))
	        payload_esc = mtmp2
		ACLmsg.setContent(payload_esc)

                self.postMessage(ACLmsg)
            else:
                self._other_messageCB(conn,mess)

	    return True


    def _other_messageCB(self, conn, mess):
	"""
	non jabber:x:fipa chat messages callback
	"""
	#print "NON-FIPA MESSAGE RECEIVED: " + str(mess)
        pass

    
    def getAID(self):
	"""
	returns AID
	"""
        return self._aid

    def getAMS(self):
	"""
	returns the AMS aid
	"""
        return AID.aid(name="ams." + self._serverplatform, addresses=[ "xmpp://acc."+self._serverplatform ])

    def getDF(self):
	"""
	returns the DF aid
	"""
        return AID.aid(name="df." + self._serverplatform, addresses=[ "xmpp://acc."+self._serverplatform ])

    def getSpadePlatformJID(self):
	"""
	returns the SPADE JID (string)
	"""
        return "acc." + self._serverplatform
    
    def send(self, ACLmsg):
	"""
	sends an ACLMessage
	"""
        self._sendTo(ACLmsg, self.getSpadePlatformJID())

    def _sendTo(self, ACLmsg, tojid):
	"""
	sends an ACLMessage to a specific JabberID
	"""
        if (ACLmsg.getSender() == None):
            ACLmsg.setSender(self.getAID())

        content = ACLmsg.getContent()
        comillas_esc = '\\"'
        barrainv_esc = '\\\\'
        mtmp1 = barrainv_esc.join(content.split('\\'))
        mtmp2 = comillas_esc.join(mtmp1.split('"'))
        payload_esc = mtmp2
        ACLmsg.setContent(payload_esc)
        
	ap = ACLParser.ACLxmlParser();
        payload = ap.encodeXML(ACLmsg)
        
        envelope = Envelope.Envelope()
        envelope.setFrom(ACLmsg.getSender())
        for i in ACLmsg.getReceivers():
            envelope.addTo(i)
        envelope.setAclRepresentation("fipa.acl.rep.xml.std")
        envelope.setPayloadLength(len(payload))
        envelope.setPayloadEncoding("US-ASCII")
        envelope.setDate(BasicFipaDateTime.BasicFipaDateTime())

        
        xc = XMLCodec.XMLCodec()
        envxml = xc.encodeXML(envelope)

        xenv = xmpp.protocol.Node('jabber:x:fipa x')
        xenv['content-type']='fipa.mts.env.rep.xml.std'
        xenv.addData(envxml)
        
        jabber_msg = xmpp.protocol.Message(tojid,payload, xmlns="")
        jabber_msg.addChild(node=xenv)
        jabber_msg["from"]=self.getAID().getName()
        self.jabber.send(jabber_msg)
        #jabber_msg.setNamespace("jabber:component:accept")
        #print str(jabber_msg.getNamespace())
        #print str(jabber_msg.getAttrs())
        #print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
        #print jabber_msg
        #print "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
        
 


    
    def kill(self):
	"""
	kills the agent
	"""
        #self._alive = False
	self._forceKill.set()

   
    def forceKill(self):
            return self._forceKill.isSet()
        
    def _setup(self):
	"""
	setup agent method. configures the agent
	must be overridden
        """
        pass

    def takeDown(self):
	"""
	stops the agent
	must be overridden
        """
        pass

    def shutdown(self):

	print "apagando agente " + self.getAID().getName()
	self.jabber_process.kill()

	#Stop the Behaviours
        for b in self._behaviourList:
            self.removeBehaviour(b)
        if (self._defaultbehaviour != None):
            self._defaultbehaviour.kill()
        #DeInit the Agent
        self.takeDown()

	self.kill()

    def run(self):
	"""
	periodic agent execution
	"""
        #Init The agent
        self._setup()
        #Start the Behaviours
        if (self._defaultbehaviour != None):
            self._defaultbehaviour.start()
        #Main Loop
        while not self.forceKill():
        	try:
               		#Check for queued messages
	                proc = False
        	        msg = self._receive(block=True, timeout=2)
	                if (msg != None):
        	            for b in self._behaviourList:
                	        t = self._behaviourList[b]
                        	if (t != None):
	                            if (t.match(msg) == True):
        	                        b.postMessage(msg)
                	                #if (b.done() == True):
                        	        #    self.removeBehaviour(b)
	                                proc = True
        	                        break
                	    if (proc == False):
                        	if (self._defaultbehaviour != None):
	                       		self._defaultbehaviour.postMessage(msg)
	        except:
		    #print "AGENT IS NOT ALIVE!!!!!" + str(self)
	            self.shutdown()

	self.shutdown()
            
    def start_and_wait(self):
	"""
	starts the agent and remains until the agent finishes
	"""

	self.start()

	while not self.forceKill():
		try:
			time.sleep(1)
		except:
			self.shutdown()

        
    def setDefaultBehaviour(self, behaviour):
	"""
	sets a Behavior as Default
	"""
        self._defaultbehaviour = behaviour
        behaviour.setAgent(self)

    def getDefaultBehaviour(self):
	"""
	returns the default behavior
	"""
        return self._defaultbehaviour

    def addBehaviour(self, behaviour, template=None):
	"""
	adds a new behavior to the agent
	"""
        self._behaviourList[behaviour] = template
        behaviour.setAgent(self)
        behaviour.start()

    def removeBehaviour(self, behaviour):
	"""
	removes a behavior from the agent
	"""
        behaviour.kill()
        try:
            self._behaviourList.pop(behaviour)
        except KeyError:
	    #print "removeBehaviour: KeyError"
            pass

    class SearchAgentBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, msg, AAD, debug = False):
            Behaviour.OneShotBehaviour.__init__(self)
            self.AAD = AAD
            self.debug = debug
            self.result = None
            self.finished = False
            self._msg = msg

        def _process(self):
            p = SL0Parser.SL0Parser()
            self._msg.addReceiver( self.myAgent.getAMS() )
            self._msg.setPerformative('request')
            self._msg.setLanguage('fipa-sl0')
            self._msg.setProtocol('fipa-request')
            self._msg.setOntology('FIPA-Agent-Management')
            
            content = "((action "
            content += str(self.myAgent.getAID())
            content += "(search "+ str(self.AAD) +")"
            content +=" ))"
            
            self._msg.setContent(content)
            self.myAgent.send(self._msg)
            msg = self._receive(True,10)
            if msg == None or str(msg.getPerformative()) != 'agree':
                print "There was an error searching the Agent. (not agree)"
                if self.debug:
                    print str(msg)
                self.finished = True
                return None
            msg = self._receive(True,20)
            if msg == None or msg.getPerformative() != 'inform':
                print "There was an error searching the Agent. (not inform)"
                if self.debug:
                    print str(msg)
                self.finished = True
                return None
            else:
                content = p.parse(msg.getContent())
                if self.debug:
                    print str(msg)
                self.result = [] #content.result.set
		for i in content.result.set:
			#self.result.append(AmsAgentDescription(i)) #TODO: no puedo importar AMS :(
			#print str(i[1])
			self.result.append(i[1])
            self.finished = True

    def searchAgent(self, AAD, debug=False):
	"""
	searches an agent in the AMS
	the search template is an AmsAgentDescription class
	"""
        msg = ACLMessage.ACLMessage()
        template = Behaviour.ACLTemplate()
        template.setConversationId(msg.getConversationId())
        t = Behaviour.MessageTemplate(template)
        b = AbstractAgent.SearchAgentBehaviour(msg, AAD, debug)
        
        self.addBehaviour(b,t)
        b.join()
        return b.result
        
    
    class ModifyAgentBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, AAD, debug = False):
            Behaviour.OneShotBehaviour.__init__(self)
            self.AAD = AAD
            self.debug = debug
            self.result = None
            self.finished = False
            self._msg = ACLMessage()

        def _process(self):
            p = SL0Parser.SL0Parser()
            self._msg.addReceiver( self.myAgent.getAMS() )
            self._msg.setPerformative('request')
            self._msg.setLanguage('fipa-sl0')
            self._msg.setProtocol('fipa-request')
            self._msg.setOntology('FIPA-Agent-Management')
            
            content = "((action "
            content += str(self.myAgent.getAID())
            content += "(modify "+ str(self.AAD) + ")"
            content +=" ))"

            self._msg.setContent(content)
            	
            self.myAgent.send(self._msg)

            msg = self._receive(True,20)
            if msg == None or msg.getPerformative() != 'agree':
                print "There was an error modifying the Agent. (not agree)"
                if self.debug:
                    print str(msg)
                self.result = False
                return -1
            msg = self._receive(True,20)
            if msg == None or msg.getPerformative() != 'inform':
                print "There was an error modifying the Agent. (not inform)"
                if self.debug:
                    print str(msg)
                self.result = False
                return -1
            self.result = True
            return 1

    def modifyAgent(self, AAD, debug=False):
	"""
	modifies the AmsAgentDescription of an agent in the AMS
	"""
        template = Behaviour.ACLTemplate()
        template.setConversationId(msg.getConversationId())
        t = Behaviour.MessageTemplate(template)
        b = AbstractAgent.ModifyAgentBehaviour(msg, AAD, debug)
        
        self.addBehaviour(b,t)
        b.join()
        return b.result


    class getPlatformInfoBehaviour(Behaviour.OneShotBehaviour):
        def __init__(self, msg, debug = False):
            Behaviour.OneShotBehaviour.__init__(self)
            self._msg = msg
            self.debug = debug
            self.result = None
            self.finished = False

	def _process(self):
		msg = self._msg
		msg.addReceiver( self.myAgent.getAMS() )
		msg.setPerformative('request')
		msg.setLanguage('fipa-sl0')
		msg.setProtocol('fipa-request')
		msg.setOntology('FIPA-Agent-Management')
				
		content = "((action "
		content += str(self.myAgent.getAID())
		content += "(get-description platform)"
		content +=" ))"

		msg.setContent(content)
		
		self.myAgent.send(msg)

		msg = self._receive(True,20)
		if msg == None or msg.getPerformative() != 'agree':
			print "There was an error modifying the Agent. (not agree)"
			if self.debug:
				print str(msg)
			return -1
		msg = self._receive(True,20)
		if msg == None or msg.getPerformative() != 'inform':
			print "There was an error modifying the Agent. (not inform)"
			if self.debug:
				print str(msg)
			return -1

		self.result = msg.getContent()

    def getPlatformInfo(self, debug=False):
	"""
	returns the Plarform Info
	"""
	msg = ACLMessage.ACLMessage()
        template = Behaviour.ACLTemplate()
        template.setConversationId(msg.getConversationId())
        t = Behaviour.MessageTemplate(template)
        b = AbstractAgent.getPlatformInfoBehaviour(msg, debug)
        
        self.addBehaviour(b,t)
        b.join()
        return b.result
	

	##################################
    
    class registerServiceBehaviour(Behaviour.OneShotBehaviour):	    
    	def __init__(self, msg, DAD, debug = False):
            Behaviour.OneShotBehaviour.__init__(self)
            self._msg = msg
	    self.DAD = DAD
            self.debug = debug
            self.result = None
            self.finished = False

	def _process(self):
		self._msg.addReceiver( self.myAgent.getDF() )
		self._msg.setPerformative('request')
		self._msg.setLanguage('fipa-sl0')
		self._msg.setProtocol('fipa-request')
		self._msg.setOntology('FIPA-Agent-Management')
				
		content = "((action "
		content += str(self.myAgent.getAID())
		content += "(register " + str(self.DAD) + ")"
		content +=" ))"

		self._msg.setContent(content)
		
		self.myAgent.send(self._msg)

		msg = self._receive(True,20)
		if msg == None or msg.getPerformative() != 'agree':
			print "There was an error registering the Service. (not agree)"
			if self.debug:
				print str(msg)
			self.result = False
			return
		msg = self._receive(True,20)
		if msg == None or msg.getPerformative() != 'inform':
			print "There was an error registering the Service. (not inform)"
			if self.debug:
				print str(msg)
			self.result = False
			return
	
		if self.debug:
			print str(msg)
		self.result = True

    def registerService(self, DAD, debug=False):
	"""
	registers a service in the DF
	the service template is a DfAgentDescriptor
	"""
	msg = ACLMessage.ACLMessage()
        template = Behaviour.ACLTemplate()
        template.setConversationId(msg.getConversationId())
        t = Behaviour.MessageTemplate(template)
        b = AbstractAgent.registerServiceBehaviour(msg=msg, DAD=DAD, debug=debug)
        
        self.addBehaviour(b,t)
        b.join()
        return b.result 
  
    class deregisterServiceBehaviour(Behaviour.OneShotBehaviour):
	def __init__(self, msg, DAD, debug=False):
            Behaviour.OneShotBehaviour.__init__(self)
            self._msg = msg
	    self.DAD = DAD
            self.debug = debug
            self.result = None
            self.finished = False

	def _process(self):
		self._msg.addReceiver( self.myAgent.getDF() )
		self._msg.setPerformative('request')
		self._msg.setLanguage('fipa-sl0')
		self._msg.setProtocol('fipa-request')
		self._msg.setOntology('FIPA-Agent-Management')
				
		content = "((action "
		content += str(self.myAgent.getAID())
		content += "(deregister " + str(self.DAD) + ")"
		content +=" ))"

		self._msg.setContent(content)
		
		self.myAgent.send(self._msg)

		msg = self._receive(True,20)
		if msg == None or msg.getPerformative() != 'agree':
			print "There was an error deregistering the Service. (not agree)"
			if self.debug:
				print str(msg)
			self.result = False
			return
		msg = self._receive(True,20)
		if msg == None or msg.getPerformative() != 'inform':
			print "There was an error deregistering the Service. (not inform)"
			if self.debug:
				print str(msg)
			self.result = False
			return
	
		if self.debug:
			print str(msg)
		self.result = True
		return

    def deregisterService(self, DAD, debug=False):
	"""
	deregisters a service in the DF
	the service template is a DfAgentDescriptor
	"""
	msg = ACLMessage.ACLMessage()
        template = Behaviour.ACLTemplate()
        template.setConversationId(msg.getConversationId())
        t = Behaviour.MessageTemplate(template)
        b = AbstractAgent.deregisterServiceBehaviour(msg, DAD, debug)
        
        self.addBehaviour(b,t)
        b.join()
        return b.result 
  
    class searchServiceBehaviour(Behaviour.OneShotBehaviour):

	def __init__(self, msg, DAD, debug=False):
            Behaviour.OneShotBehaviour.__init__(self)
            self._msg = msg
	    self.DAD = DAD
            self.debug = debug
            self.result = None
            self.finished = False


	def _process(self):	

		self._msg.addReceiver( self.myAgent.getDF() )
		self._msg.setPerformative('request')
		self._msg.setLanguage('fipa-sl0')
		self._msg.setProtocol('fipa-request')
		self._msg.setOntology('FIPA-Agent-Management')
				
		content = "((action "
		content += str(self.myAgent.getAID())
		content += "(search "+ str(self.DAD) +")"
		content +=" ))"
	
		self._msg.setContent(content)

		self.myAgent.send(self._msg)
	
		msg = self._receive(True,20)
		if msg == None or msg.getPerformative() != 'agree':
			print "There was an error searching the Agent. (not agree)"
			if self.debug:
				print str(msg)
			return
		msg = self._receive(True,20)
		if msg == None or msg.getPerformative() != 'inform':
			print "There was an error searching the Agent. (not inform)"
			if self.debug:
				print str(msg)
			return
	
		else:
			try:
				p = SL0Parser.SL0Parser()
				content = p.parse(msg.getContent())
				if self.debug:
					print str(msg)
				self.result = content.result.set#[0]#.asList()

			except:
				return
    def searchService(self, DAD, debug=False):
	"""
	search a service in the DF
	the service template is a DfAgentDescriptor
	"""
	msg = ACLMessage.ACLMessage()
        template = Behaviour.ACLTemplate()
        template.setConversationId(msg.getConversationId())
        t = Behaviour.MessageTemplate(template)
        b = AbstractAgent.searchServiceBehaviour(msg, DAD, debug)
        
        self.addBehaviour(b,t)
        b.join()
        return b.result 
  

    class modifyServiceBehaviour(Behaviour.OneShotBehaviour):
	def __init__(self, msg, DAD, debug=False):
            Behaviour.OneShotBehaviour.__init__(self)
            self._msg = msg
	    self.DAD = DAD
            self.debug = debug
            self.result = None

	def _process(self):

		#p = SL0Parser.SL0Parser()
	
		self._msg = ACLMessage.ACLMessage()
		self._msg.addReceiver( self.myAgent.getDF() )
		self._msg.setPerformative('request')
		self._msg.setLanguage('fipa-sl0')
		self._msg.setProtocol('fipa-request')
		self._msg.setOntology('FIPA-Agent-Management')
				
		content = "((action "
		content += str(self.myAgent.getAID())
		content += "(modify "+ str(self.DAD) + ")"
		content +=" ))"

		self._msg.setContent(content)
		
		self.myAgent.send(self._msg)

		msg = self._receive(True,20)
		if msg == None or msg.getPerformative() != 'agree':
			print "There was an error modifying the Service. (not agree)"
			if self.debug:
				print str(msg)
			self.result=False
			return
		msg = self._receive(True,20)
		if msg == None or msg.getPerformative() != 'inform':
			print "There was an error modifying the Service. (not inform)"
			if self.debug:
				print str(msg)
			self.result = False
			return

		self.result = True
		return
    def modifyService(self, DAD, debug=False):
	"""
	modifies a service in the DF
	the service template is a DfAgentDescriptor
	"""
	msg = ACLMessage.ACLMessage()
        template = Behaviour.ACLTemplate()
        template.setConversationId(msg.getConversationId())
        t = Behaviour.MessageTemplate(template)
        b = AbstractAgent.modifyServiceBehaviour(msg, DAD, debug)
        
        self.addBehaviour(b,t)
        b.join()
        return b.result 


	##################################

# Changed to be a 'daemonic' python Thread
class jabberProcess(threading.Thread):

	def __init__(self, socket):
		self.jabber = socket
		#self._alive = True
		self._forceKill = threading.Event()
		self._forceKill.clear()
		threading.Thread.__init__(self)
		self.setDaemon(True)
		
	def kill(self):
		try:
			self._forceKill.set()
		except:
			#Agent is already dead
			pass

	def forceKill(self):
		return self._forceKill.isSet()

	def run(self):
		"""
		periodic jabber update
		"""
		while not self.forceKill():
		    try:
		            self.jabber.Process(0.4)
		    except:
			    #print ">>> EXCEPTION IN PERIODIC JABBER UPDATE"
			    pass

		

class PlatformAgent(AbstractAgent):
    """
    A PlatformAgent is a SPADE component.
    Examples: AMS, DF, ACC, ...
    """
    def __init__(self, node, password, server="localhost", port=5347, debug = []):
        AbstractAgent.__init__(self, node, server)
	self.debug = debug
        self.jabber = xmpp.Component(server, port, self.debug)
        self._register(password)

    def _register(self, password, autoregister=True):
	"""
	registers the agent in the Jabber server
	"""

        jid = xmpp.protocol.JID(self._aid.getName())
        name = jid.getNode()

        #TODO: Que pasa si no conectamos? Hay que controlarlo!!!
	self.jabber.connect()
        

        if (self.jabber.auth(name,password,"spade") == None):
                raise NotImplementedError

        #print "auth ok", name
        self.jabber.RegisterHandler('message',self._jabber_messageCB)

	self.jabber_process = jabberProcess(self.jabber)
	self.jabber_process.start()
        #thread.start_new_thread(self._jabber_process, tuple())

class Agent(AbstractAgent):
    """
    This is the main class which may be inherited to build a SPADE agent
    """
    def __init__(self, agentjid, password, port=5222, debug=[]):
        jid = xmpp.protocol.JID(agentjid)
        self.server = jid.getDomain()
	self.port = port
	self.debug = debug
        AbstractAgent.__init__(self, agentjid, self.server)
        self.jabber = xmpp.Client(self.server, self.port, self.debug)
        self._register(password)
        self.jabber.sendInitPresence()

    def _register(self, password, autoregister=True):
	"""
	registers the agent in the Jabber server
	"""

        jid = xmpp.protocol.JID(self._aid.getName())
        name = jid.getNode()

        #TODO: Que pasa si no conectamos? Hay que controlarlo!!!
        self.jabber.connect()
        

        #TODO:  Que pasa si no nos identificamos? Hay que controlarlo!!!
        #       Registrarse automaticamente o algo..
        if (self.jabber.auth(name,password,"spade") == None):
            #raise NotImplementedError
	    
	    if (autoregister == True):
                xmpp.features.getRegInfo(self.jabber,jid.getDomain())
                xmpp.features.register(self.jabber,jid.getDomain(),\
		{'username':name, 'password':str(password)})

		#self.jabber.reconnectAndReauth()
		self.jabber.disconnect()
		del self.jabber
        	self.jabber = xmpp.Client(self.server, self.port, self.debug)
		self.jabber.connect()

                if (self.jabber.auth(name,password,"spade") == None):
                    raise NotImplementedError
            else:
                raise NotImplementedError
	    
        self.jabber.RegisterHandler('message',self._jabber_messageCB)

        #thread.start_new_thread(self._jabber_process, tuple())
	self.jabber_process = jabberProcess(self.jabber)
	self.jabber_process.start()
        
	if not self.__register_in_AMS():
		print "Agent " + str(self.getAID().getName()) + " dying ..."
		sys.exit(-1)

    def shutdown(self):
        if not self.__deregister_from_AMS():
		print "Agent " + str(self.getAID().getName()) + " dying without deregistering itself ..."
	AbstractAgent.shutdown(self)


    def run(self):
	"""
	Main loop of the agent
	"""
	try:
		AbstractAgent.run(self)
	finally:
		AbstractAgent.shutdown(self)


    def __register_in_AMS(self, state='active', ownership=None, debug=False):

	self._msg = ACLMessage.ACLMessage()
	self._msg.addReceiver( self.getAMS() )
	self._msg.setPerformative('request')
	self._msg.setLanguage('fipa-sl0')
	self._msg.setProtocol('fipa-request')
	self._msg.setOntology('FIPA-Agent-Management')
				
	content = "((action "
	content += str(self.getAID())
	content += "(register (ams-agent-description "
	content += ":name " + str(self.getAID())
	content += ":state "+state
	if ownership:
		content += ":ownership " + ownership
	content +=" ) ) ))"

	self._msg.setContent(content)
		
	self.send(self._msg)

	# We expect the initial answer from the AMS
	print "going to receive"
	msg = self._receive(True,20)
	if (msg != None) and (str(msg.getPerformative()) == 'refuse'):
		print color_red + "There was an error initiating the register of agent: " + color_yellow + str(self.getAID().getName()) + color_red + " (refuse)" + color_none
		return False
	elif (msg != None) and (str(msg.getPerformative()) == 'agree'):
		print color_green + "Agent: " + color_yellow + str(self.getAID().getName()) + color_green + " initiating registering process (agree)" + color_none
	else:
		# There was no answer from the AMS or it answered something weird, so error
		print color_red + "There was an error initiating the register of agent: " + color_yellow + str(self.getAID().getName()) + color_none
		return False
			
	# Now we expect the real informative answer from the AMS
	msg = self._receive(True,20)
	if (msg != None) and (msg.getPerformative() == 'failure'):
		print color_red + "There was an error with the register of agent: " + color_yellow + str(self.getAID().getName()) + color_red + " (failure)" + color_none
		return False
	elif (msg != None) and (str(msg.getPerformative()) == 'inform'):
		print color_green + "Agent: " + color_yellow + str(self.getAID().getName()) + color_green + " registered correctly (inform)" + color_none
	else:
		# There was no real answer from the AMS or it answered something weird, so error
		print color_red + "There was an error with the register of agent: " + color_yellow + str(self.getAID().getName()) + color_none
		return False
	
	return True

    def __deregister_from_AMS(self, state=None, ownership=None, debug=False):
	self._msg = ACLMessage.ACLMessage()
	self._msg.addReceiver( self.getAMS() )
	self._msg.setPerformative('request')
	self._msg.setLanguage('fipa-sl0')
	self._msg.setProtocol('fipa-request')
	self._msg.setOntology('FIPA-Agent-Management')
				
	content = "((action "
	content += str(self.getAID())
	content += "(deregister (ams-agent-description "
	content += " :name " + str(self.getAID())
	if state:
		content += " :state "+state
	if ownership:
		content += " :ownership " + ownership
	content +=" ) ) ))"

	self._msg.setContent(content)
		
	self.send(self._msg)

	# We expect the initial answer from the AMS
	msg = self._receive(True,20)
	if (msg != None) and (str(msg.getPerformative()) == 'refuse'):
		print "There was an error initiating the deregister of agent: " + str(self.getAID().getName()) + " (refuse)"
		return False
	elif (msg != None) and (str(msg.getPerformative()) == 'agree'):
		print "Agent: " + str(self.getAID().getName()) + " initiating deregistering process (agree)"
	else:
		# There was no answer from the AMS or it answered something weird, so error
		print "There was an error initiating the deregister of agent: " + str(self.getAID().getName())
		return False
			
	# Now we expect the real informative answer from the AMS
	msg = self._receive(True,20)
	if (msg != None) and (msg.getPerformative() == 'failure'):
		print "There was an error with the deregister of agent: " + str(self.getAID().getName()) + " (failure)"
		return False
	elif (msg != None) and (str(msg.getPerformative()) == 'inform'):
		print "Agent: " + str(self.getAID().getName()) + " deregistered correctly (inform)"
	else:
		# There was no real answer from the AMS or it answered something weird, so error
		print "There was an error with the deregister of agent: " + str(self.getAID().getName())
		return False
	
	return True


