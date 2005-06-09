import service

class Ping(service.Service):		
	def handle(self, msg = None, remoteservice = None):
		#Hago cosas
		#y respondo al agente si hace falta
		m = message.Payload()
		m.setSender(msg.getReceiver())
		m.setReceiver(msg.getSender())
		m.setPerformative('inform')
		m.setContent('PONG')
		agent.sendPayload(m,self.servicename,remoteservice)
		return


def startService(servicename, agent):
	return Ping(servicename, agent)
