"""
HTTP MTP for SPADE

This module have been developed following the "FIPA Agent Message Transport Protocol 
for HTTP" standard. 

www.fipa.org
"""

import BaseHTTPServer
import sys
import threading
from spade import MTP
from spade import XMLCodec
from spade import SpadeConfigParser
import httplib



#Specific constants
PORT = 8000
PROTOCOL_VERSION = "HTTP/1.1"
BOUNDARY = "SpadeMtpHttpMimeMultipartMixedBoundary"
BI="--"
FIPA_CT = "multipart-mixed"
FIPA_HP = {'Cache-Control':'no-cache', 'host':'localhost:80', 'Mime-Version':'1.0', 
			'Content-Type':FIPA_CT+' ; boundary="'+BOUNDARY+'"',
			'Content-Length':'0' , 'Connection':'close'}

FIPA_HR = {'Content-type':'text/plain','Cache-Control':'no-cache','Connection':'close'}
FIPA_CT_ENV = "application/fipa.mts.env.rep.xml.std"
FIPA_CT_PAY = "application/fipa.acl.rep.string.std"



class http(MTP.MTP):


	def setup(self):

		httpserver = HttpServer()
		httpserver.setName("SpadeHttpServer")
		httpserver.start()
	

	def make_body(self,envelope,payload):
		"""
		Create the body of the message 	
		"""
		body = BI + BOUNDARY + "\n" 
		body = body + FIPA_CT_ENV + "\n\n"
		body = body + envelope + "\n\n" + BI + BOUNDARY + "\n"
		body = body + FIPA_CT_PAY + "\n\n"
		body = body + payload + "\n\n"
		body = body + BI + BOUNDARY + BI +"\n"

		return body
	
	

	def send(self,envelope,payload):
		"""
		Send a message to a http agent
		"""
		
		#print ">>>HTTP TRANSPORT: A MESSAGE TO SEND FOR ME"

		#print ">>>HTTP: PAYLOAD = " + payload

		xc = XMLCodec.XMLCodec()
		try:
			envxml = xc.encodeXML(envelope)
		except:
			#error
			pass
		
		# Making the body to send
		body = self.make_body(envxml,payload);

		self.fipaHeadersPost = FIPA_HP
		self.fipaHeadersPost['Content-Length'] = str(len(body))	
	
		# Geting message receivers 
		to = envelope.getTo()
		#print ">>>HTTP TRANSPORT: TO = " + str(to)

		for receiver in to:
			#print ">>>HTTP TRANSPORT: RECEIVER = " + str(receiver)
			for ad in receiver.getAddresses():
				ad = str(ad)
				#print ">>>HTTP TRANSPORT: ADDRESS = " + ad
		
				# HTTP URI = http://address:port
				if ad[0:7] == "http://":
					ad = ad[7:]
					#print ">>>HTTP TRANSPORT: FINAL ADDRESS = " + ad

					# HTTP connection
					host = ad.split("/acc")[0]
					conn = httplib.HTTPConnection(host)
			
					self.fipaHeadersPost['host'] = host 
			
					conn.request("POST","/acc",body,self.fipaHeadersPost)
					response = conn.getresponse()
			
					if response.status != 200:
						print "Conection Error: Bad response\n"
				
					if response.reason != "OK":
						print "Conection Error: Bad reason\n"
					
					print response.status, response.reason
				
					conn.close()
					# End connection
					#print "Conneticon finalized"



class HttpServer(threading.Thread):
	def run(self):
		httpd = BaseHTTPServer.HTTPServer(("", PORT), Handler)
		print "serving at port", PORT
		httpd.serve_forever()


class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
	protocol_version = PROTOCOL_VERSION

	def send_response(self, code, message=None): 
		"""
		Overloaded for fipa specification responses compliancy
        	"""
        	self.log_request(code)
        	if message is None:
            		if code in self.responses:
                		message = self.responses[code][0]
            		else:
                		message = ''
		self.wfile.write("%s %d %s\r\n" %(self.protocol_version, code, message))


    	def do_POST(self):
		"""
		Serve Fipa Post requests
		"""
		if self.request_version != self.protocol_version:
			# fipa specification only allows HTTP/1.1
			self.send_error(505)

		if self.headers.keys() != FIPA_HP.keys():
			self.send_error(400,"FIPA headers required (www.fipa.org)")

		if self.headers.getheader('Mime-Version') != FIPA_HP['Mime-Version']:
			self.send_error(400,"Mime-Version must be 1.0")

		if FIPA_CT not in self.headers.getheader('Content-Type'):
			self.send_error(415)

		if 'boundary' not in self.headers.getparamnames():
			self.send_error(415)
		
		boundary = self.headers.getparam('boundary')
	
		clen = self.headers.getheader('Content-Length')	
		if clen <= 0:
			send_error(411)
	
		envelopexml , payload = self.getContent(self.rfile,boundary,clen)

		# parsing the envelope
		xc = XMLCodec.XMLCodec()
		try:
			envelope = xc.parse(envelopexml)
		except:
			self.send_error(400,"Malformed FIPA Envelope")

		# Dispatching message
		MTP.MTP.dispatch(envelope,payload)
			
		# Response 
        	self.send_response(200)
		for header in FIPA_HR.keys():
			self.send_header(header,FIPA_HR[header])
        	self.end_headers()


 	def getContent(self,rfile,boundary,clen):
		"""
		Parses entity body catching the envelope and payload of the incoming message 
		"""

		env = None
		pay = None
		
		
		part = 0
		buf1 = rfile.read(int(clen)).split(BI+boundary+BI)

		if len(buf1) != 2:
			self.send_error(400,"Malformed Multipart-Mixed MIME")

		buf2 = buf1[0].split(BI+boundary)

		parts = len(buf2)

		try:
			if parts == 2:
				env = buf2[0]
				pay = buf2[1]
			
			elif parts == 3:
				# there is text before the first boundary delimiter line, and it is ignored
				env = buf2[1]
				pay = buf2[2]

			else:
				self.send_error(400,"Malformed Multipart-Mixed MIME")
		except:
			self.send_error(400,"Malformed Multipart-Mixed MIME")
		
		# searching CLRF CLRF where envelope really starts, before this sequence is the envelope content type
		index = env.find('\n\n')
		type_env = env[0:index]
		env = env[index+2:]

		# the same for payload 
		index = pay.find('\n\n')
		type_pay = pay[0:index]
		pay = pay[index+2:]


		# Content types check
		try:
			type_env = type_env.split(':')[1].split(';')[0].strip()
			type_pay = type_pay.split(':')[1].split(';')[0].strip()
		
		except:
			self.send_error(415)

		if type_env != FIPA_CT_ENV or type_pay != FIPA_CT_PAY:
			self.send_error(415)
				
		return (env,pay)





#Required constants
PROTOCOL = "http"
INSTANCE = http


if __name__ == "__main__":

	http_mtp = http("SpadeHttpSever",None,None)

	import time
	time.sleep(5)
	fenv = open('env.example','r')
	fpay = open('pay.example','r')

	envxml = fenv.read()
	payload = fpay.read()
	xc = XMLCodec.XMLCodec()
	envelope = xc.parse(envxml)
	print "HORRRRRRRRRRRRRRRRRRRRRRRR"
	print envelope
	http_mtp.send(envelope,payload)



"""
TODO
- el send ha de tornar un codi de error quan falla, no imprimir res
"""
