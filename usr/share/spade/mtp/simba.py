
from spade import MTP
from spade import AID
from spade import ACLParser
import socket
import SocketServer
import xmpp

#try:
#	import stack_thread as thread
#except:
#	import thread

import thread

class simba(MTP.MTP):
	class SimbaRequestHandler(SocketServer.DatagramRequestHandler):
                        '''
                        Request handler for SIMBA messages
                        '''
                        def handle(self):
                                print "SIMBA SS: New incoming message: " + str(self.request)
				


	def receiveThread(self):
                self.SS = SocketServer.ThreadingUDPServer(("", self.port), SimbaRequestHandler)
                print "SIMBA SS listening on port ", self.port
                self.SS.serve_forever()

	def __setup(self):
		'''
		Secondary constructor
		'''
		self.address = self.config.acc[self.name].address		
		self.port = self.config.acc[self.name].port		

		# Launch receive thread
		print ">>>SIMBA: Going to start new thread"
		tid = thread.start_new_thread(self.receiveThread, ())	
		print ">>>SIMBA: Started new thread " + str(tid)
			

	def send(self, envelope, payload, to=None):
		'''
		Send a message to a SIMBA agent
		'''
		print ">>>SIMBA TRANSPORT: A MESSAGE TO SEND FOR ME"

		payload = str(payload.getPayload()[0])
		print ">>>SIMBA: PAYLOAD = " + payload
		try:
			p = ACLParser.ACLxmlParser()
			aclmsg = p.parse(payload)
		except:
			print ">>>SIMBA: COULD NOT BUILD ACL"

		if to == None:
			to = envelope.getTo()
			print ">>>SIMBA TRANSPORT: TO = " + str(to)

		for receiver in to:
			print ">>>SIMBA TRANSPORT: RECEIVER = " + str(receiver)
			for ad in receiver.getAddresses():
				ad = str(ad)  # Type change
				print ">>>SIMBA TRANSPORT: ADDRESS = " + ad
				# SIMBA URI = simba://address:port
				if ad[0:8] == "simba://":
					ad = ad[8:]
					print ">>>SIMBA TRANSPORT: ADDRESS FINAL = " + ad
					# Check for the presence of a port
					if ':' in ad:
						ip, port = ad.split(':')
					else:
						ip = ad
						port = 2001

					# Set up a SIMBA socket to send the message
					s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
					try:
    						s.connect((ip, port))
						# FORCE ACL WITH PARENTHESIS
						s.send(str(aclmsg))  # ACL with parenthesis, oh no!
						s.close()
						print ">>>SIMBA message succesfully sent"				
					except:
						print "Could not send SIMBA message"				


# Required
PROTOCOL = "simba"
INSTANCE = simba
#port = "2001"
