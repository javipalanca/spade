import xmpp
import threading
import Agent
import Envelope
import FIPAMessage
import AID
import Behaviour



class SpadePlatform(Agent.PlatformAgent):
	class RouteBehaviour(Behaviour.Behaviour):
		def __init__(self):
			Behaviour.Behaviour.__init__(self)
		def _process(self):
			msg = self._receive(True)
			if (msg != None):
				to_list = msg.getReceivers()
				d = {}
				for to in to_list:
					if not to.getAddresses()[0] in d: d[to.getAddresses()[0]]=list()
					d[to.getAddresses()[0]].append(to)
				for k,v in d.items():
					newmsg = msg
					newmsg.to = v
					#print "############# k != plat?"
					#print " k>>"+k[7:] + "    plat>>"+self.myAgent.getSpadePlatformJID()
					if k[7:] != self.myAgent.getSpadePlatformJID():
						self.myAgent._sendTo(newmsg, k[7:])
					else:
						for recv in v:
							self.myAgent._sendTo(newmsg, recv.getName())
					# Reenviamos el msg a todos los destinatarios
					# Deberiamos de comprobar si el destinatario estaen otro servidor y reenviarselo a la plataforma en vez de a el.
					# Tambien deberiamos comprobar el protocolo y usar una pasarela en el caso de que sea necesario.
					#print "Message to", to.getName(), "... Posting!"
			else:
				print "ACC::dying... it shouldn't happen"
			
	def __init__(self, node, password, server, port):
		Agent.PlatformAgent.__init__(self, node, password, server, port, debug=[])

	def _setup(self):
		self.setDefaultBehaviour(self.RouteBehaviour())


"""
class FipperPlatform(threading.Thread):
    def __init__(self, params=dict()):
        threading.Thread.__init__(self)
        self.__params = params
        self.__mts = MTS(params)

        try:
            mtp_list = params["mtps"]
            for mtp in mtp_list:
                self.__mts.addMTP(mtp)
        except KeyError:
            pass

    def getMTS(self):
        return self.__mts
        
    def run(self):
        pass
        
        


class MTS:

    def __init__(self, params=dict()):
        self.__platformagents = dict()

    def addAgent(self, agent):
        aid = agent.getAID()
        self.__platformagents[aid] = agent

    def addMTP(self, mtp):
        pass

     
    def dispatch(self, msg):
        print "Dispatching msg..."
        envelope = msg.getEnvelope()
        to_list = envelope.getTo()
        #for to in to_list:
	#	print to
	
        for to in to_list:
            if to in self.__platformagents:
                print "Agend finded! Posting..."
                self.__platformagents[to].postMessage(msg)
	


class MTP:
    def getName(self):
        raise NotImplemented

    def getSupportedProtocols(self):
        raise NotImplemented

    def activate(self, dispatcher, params):
        raise NotImplemented

    def deactivate(self):
        raise NotImplemented
        
    def deliver(self, addr, envelope, payload):
        raise NotImplemented
        
"""

