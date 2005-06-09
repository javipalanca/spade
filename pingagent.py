import agent
import time
import message
import sys
import xmlcolor
from select import select

class ActivePingAgent(agent.Agent):
	def run(self):
		while(1):
			print 'AD: ' + str(self.ad)
			print 'SD: ' + str(self.sd)
			print '>>>'
			inputs, outputs, errors = select([sys.stdin], [], [],1)
			line = sys.stdin.readline()
			if line[0] == 'q':
				self.remove()
				print 'aaaadios'
				sys.exit(0)
			elif line[0] == 'p':
				# Buscar servicios de ping
				s = None
				s = self.searchService('ping')
				l=list()
				if s:
					for item in s:
						i=item.find('@')
						item = item[0:i]
						l.append(item)
				if s!=None:
					print 'he encontrado el servicio ping en ' + str(l)
					# Crear el payload 
					p = message.Payload()
					p.setSender(self.agent_name)
					p.setReceiver(l)
					p.setPerformative('query-ref')
					p.setContent('PING')
					self.sendPayload(p,'fipper','ping')
			
	def handleMessage(self, msg, remoteservice):
		print 'msg recibido'
		if msg.getContent() == 'PONG':
		   	print xmlcolor.colorize('PPPPP OOOOO N   N GGGGG','green')
			print xmlcolor.colorize('P   P O   O NN  N G','green')
			print xmlcolor.colorize('PPPPP O   O N N N G  GG','green')
			print xmlcolor.colorize('P     O   O N  NN G   G','green')
			print xmlcolor.colorize('P     OOOOO N   N GGGGG','green')
			print ''
			print 'PONG de '+str(msg.getSender()) 
		return
		
