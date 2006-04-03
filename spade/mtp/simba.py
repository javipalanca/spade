
from spade import MTP
from spade import AID
import socket
import SocketServer
try:
	import stack_thread as thread
except:
	import thread

CONFIGFILE = "/etc/spade/spade.xml"


class simba(MTP.MTP):
	class SimbaRequestHandler(SocketServer.DatagramRequestHandler):
                        '''
                        Request handler for SIMBA messages
                        '''
                        def handle(self):
                                print "SIMBA SS: New incoming message"


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
		thread.start_new_thread(self.receiveThread, ())	
			

	def send(self, envelope, payload, to=None):
		'''
		Send a message to a SIMBA agent
		'''
		print ">>>SIMBA TRANSPORT: A MESSAGE ARRIVED FOR ME"
		if to == None:
			to = envelope.getTo()

		for receiver in to:
			for ad in receiver.getAddresses():
				# SIMBA URI = simba://address:port
				if ad[0:7] == "simba://":
					ad = str(ad)
					ad = ad.strip("simba://")
					# Check for the presence of a port
					if ':' in ad:
						ip, port = ad.split(':')
					else:
						ip = ad
						port = 20001

					# Set up a SIMBA socket to send the message
					s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
					try:
    						s.connect((ip, port))
						# FORCE ACL WITH PARENTHESIS
						s.send(str(payload))  # ACL with parenthesis, oh no!
						s.close()
						print "SIMBA message succesfully sent"				
					except:
						print "Could not send SIMBA message"				


