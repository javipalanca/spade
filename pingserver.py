import agent
import time
import message
import sys
import xmlstream
import xmlcolor
import jabber
from select import select

class PassivePingAgent(agent.Agent):
	def run(self):
	   	self.addService('ping',self.pingHandler)
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
			time.sleep(0.4)

	def pingHandler(self,msg,fromservice):
	   	#print "OOOOHHHHH , ME HA LLEGADO UN MENSAJE!!!!!!!!!!!!!!"
		m = message.Payload()
		m.setSender(self.agent_name)
		recv = list()
		recv.append(msg.getSender())
		m.setReceiver(recv)
		m.setPerformative('inform')
		m.setContent('PONG')
		print xmlcolor.colorize('PPPPP IIIII N   N GGGGG','red')
		print xmlcolor.colorize('P   P   I   NN  N G','red')
		print xmlcolor.colorize('PPPPP   I   N N N G  GG','red')
		print xmlcolor.colorize('P       I   N  NN G   G','red')
		print xmlcolor.colorize('P     IIIII N   N GGGGG','red')
		print ''
		print xmlcolor.colorXML(m.getXML())
		self.sendPayload(m,'ping',fromservice)
		return

