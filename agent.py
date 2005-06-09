import socket
from select import select
from string import split,strip,join,find
import sys,os
import thread
import time
import jabber
import xmlstream
import message
import xmlcolor
import time
import imp

class Agent:
	def __init__(self, name="agent", world="localhost"):
		
		'''Constructor de agente. No sobrecargar'''
		#world es el servidor en el que el agente va a vivir
		# Inicializamos atributos
		self.agent_name = name
		self.world = world
		self.con = dict()  # Lista de conexiones abiertas
		self.jid = []
		self.jud = None
		self.world = world
		
		self.servicelist = dict()
		
		# self.ad es un diccionario conteniendo el AgentDirectory
		self.ad = dict()
		# self.sd es un diccionario conteniendo el ServiceDirectory
		self.sd = dict()
		
		self.myroster = list()
		
		
		self.flag = 0

		self.password = 'kakatua'
		resource = 'fipper'
		
		#abrimos la conexion principal
		self.con['fipper']=(self.connectToServer(world))
		self.jUsername = self.registerInServer(self.con['fipper'])
		self.login(self.con['fipper'],resource)
		
		#~ self.stabilizeConnection()
		thread.start_new_thread(self.keepAlive, tuple())
		
		self.jid.append(str(self.jUsername + '@' + world + '/' + resource))
		
		self.registerInJUD()
		print 'logged OK'
		
		
		thread.start_new_thread(self.welcomePack, tuple())

		self.run()
		
		return
	
	def run(self):
		pass
	
	def getName(self):
		return self.agent_name
	
	def getLocator(self):
		return self.jid
	'''
	def addService(self,servicename, servicepath):
		if not self.servicelist.has_key(servicename):
			#~ call(servicepath)
			file, pathname, description = imp.find_module(servicename)
			serv = imp.load_source('serv',servicepath,file)
			self.servicelist[servicename] = serv.startService(servicename,self)
			self.con[servicename] = self.connectToServer(self.world)
			self.login(self.con[servicename],servicename)
			self.stabilizeConnection(self.con[servicename])
			self.jid.append(self.jUsername + '@' + self.world + '/' +servicename)
	'''
	def addService(self,servicename,servicehandler):
		self.servicelist[servicename] = servicehandler
		self.con[servicename] = self.connectToServer(self.world)
		self.login(self.con[servicename],servicename)
		#self.stabilizeConnection(self.con[servicename])
		self.jid.append(self.jUsername + '@' + self.world + '/' +servicename)

	   
	def searchAgent(self,name):
		for k,v in self.ad.items():
			if v == name:
				return k
	def searchService(self,service):
		l = list()
		for k,v in self.sd.items():
			if k == service:
				return v  #lista de jids que ofrecen el servicio

	def sendPayload(self, payload, fromservice, toservice):
		sender = self.agent_name + '@' + self.world + '/' + fromservice
		recv = list()
		for name in payload.getReceiver():
			tmp = str(self.searchAgent(name)) + '/' + toservice
			recv.append(tmp)

		envelope = message.Envelope(toservice,recv,sender)
		print xmlcolor.colorXML(envelope.getXML())
		print xmlcolor.colorXML(payload.getXML())

		msg = message.ACLMessage(self.con[fromservice],payload,envelope)

		msg.send()

	def keepAlive(self):
		'''Mantiene viva la conexion del agente con el servidor de jabber'''
		while(1):
			#self.con_aux.process(10)
			for con in self.con.values():
				con.process(1)
			time.sleep(0.5)
		

	def remove(self):
		
	   	for c in self.con.keys():
			if c != 'fipper':
				self.con[c].disconnect()
		''' #dirty hack ->TODO: desregistrar del JUD
		iq = jabber.Iq(str(self.jud)+'.'+str(self.world),'set')
		iq.setQueryPayload("<query xmlns='jabber:iq:register'><remove/></query>")

		self.con[0].send(iq)
		'''
		self.con['fipper'].requestRegInfo(self.jud)
		req = self.con['fipper'].getRegInfo()
		for info in req.keys():
			if info == u'last':
				#print "enter %s;" % info
				self.con['fipper'].setRegInfo(info, '')
			elif info == u'nick':
				#print "enter %s;" % info
				self.con['fipper'].setRegInfo(info, self.agent_name)
			elif info == u'nick' or info == u'instructions':
				pass
			else:
				#print "enter %s;" % info
				#print "SAYING DEFAULT"
				self.con['fipper'].setRegInfo( info, "imonlyanagent" )
		self.con['fipper'].sendRegInfo(self.jud)

		iq = jabber.Iq(self.world,'set')
		iq.setQueryPayload("<query xmlns='jabber:iq:register'><remove/></query>")
		self.con['fipper'].send(iq)
		#print xmlcolor.colorXML(iq.asNode())

		self.con['fipper'].disconnect()

	   
	def addLocator(self, loc):
		self.agent_locator.append(loc)
		return
		
	def onPresence(self, con, prs):
		"""Manejador de presence"""
		#print "A presence has been detected"
		who = str(prs.getFrom())
		type = prs.getType()
		if type == None: type = 'available'

		# subscription request: 
		# - accept their subscription
		# - send request for subscription to their presence
		if type == 'subscribe':
			#print "subscribe request from %s" % (who)
			con.send(jabber.Presence(to=who, type='subscribed'))
			con.send(jabber.Presence(to=who, type='subscribe'))

		# unsubscription request: 
		# - accept their unsubscription
		# - send request for unsubscription to their presence
		elif type == 'unsubscribe':
			#print "unsubscribe request from %s" % (who)
			con.send(jabber.Presence(to=who, type='unsubscribed'))
			con.send(jabber.Presence(to=who, type='unsubscribe'))

		elif type == 'subscribed':
		   	pass
			#print "we are now subscribed to %s" % (who)

		elif type == 'unsubscribed':
		   	pass
			#print "we are now unsubscribed to %s"  % (who)

		elif type == 'available':
			#print "%s is available (%s / %s)" % (who, prs.getShow(), prs.getStatus())
			if not who in self.myroster:
				self.myroster.append(who)
		elif type == 'unavailable':
			#print "%s is unavailable (%s / %s)" % (who, prs.getShow(), prs.getStatus())
			if who in self.myroster:
				self.myroster.remove(who)

	def onIq(self,con,iq):
		"""Manejador de iq"""
		#print xmlcolor.colorXML(iq.asNode())
		# Nos llega una iq del JUD respondiendo a nuestra busqueda
		if iq.getID() == 'judsearch1':
			self.tempjud = dict()
			for item in iq.getQueryPayload():  # devuelve una lista
				for child in item.getChildren():
					if child.getName() == 'nick':
						self.tempjud[item.getAttr('jid')] = child.getData()
			self.flag = 1
		return

	def handleMessage(self,msg,fromservice):
		#sobrecargar funcion
		pass

	def onMessage(self,con,msg):
		'''Manejador de msg'''
		#print str(msg)

		tmp = str(msg.getFrom())
		i = tmp.find('/')
		fromservice = tmp[i+1:]
		
		tmp = str(msg.getTo())
		i = tmp.find('/')
		toservice = tmp[i+1:]
		
		strmessage = msg.getBody()
		i = strmessage.find('<fipa-message')
		
		strenvelope = strmessage[0:i]
		strpayload = strmessage[i:]

		envelopenode = xmlstream.Node('tmp')
		envelopenode.insertXML(strenvelope)
		l = envelopenode.getChildren()
		envelope = l[0]

		#print xmlcolor.colorXML(envelope)
		
		payloadnode = xmlstream.Node('tmp')
		payloadnode.insertXML(strpayload)
		l = payloadnode.getChildren()
		payload = l[0]
		
		#print xmlcolor.colorXML(payload)

		msgpayload = message.Payload(payload)
		

		#id = envelope.getAttr('id')
		#print 'ID: ' + str(id)
		
		if self.servicelist.has_key(toservice):
			s = self.servicelist[toservice]
			#print "VOY A PASARLE EL CONTROL AL HANDLER!!!!!!"
			#print xmlcolor.colorXML(msgpayload.getXML())
			s(msgpayload,fromservice)
		else:
			#print "VOY A PASARLE EL CONTROL AL HANDLER POR DEFECTO!!!!!!"
			#print xmlcolor.colorXML(msgpayload.getXML())
			self.handleMessage(msgpayload,fromservice)	

	def onDisconnect(self,con):
		'''Manejador de desconexion'''
		#self.remove()
		pass

	def send(self,msg):
		#print xmlcolor.colorXML(msg.asNode())
		return
	
	def createMessage(self,attrs):
		return Message(None, attrs)
		
	def connectToServer(self,world):
		'''Conexion inicial a un servidor'''
		# Conectamos con el servidor
		#~ con = jabber.Client(host=world,debug=[],log=sys.stderr)
		con = jabber.Client(host=world,debug=[])
		try:
		    con.connect()
		except IOError, e:
		    print "Couldn't connect: %s" % e
		    return
		else:
		    print "Connected"
		
		# Dar de alta manejadores
		con.setMessageHandler(self.onMessage)
		con.setPresenceHandler(self.onPresence)
		con.setIqHandler(self.onIq)
		con.setDisconnectHandler(self.onDisconnect)
		return con
		
	def registerInServer(self,con):
		'''Registra la cuenta jabber'''
		con.requestRegInfo()
		req = con.getRegInfo()
		#print req[u'instructions']
		con.setRegInfo(u'username', self.agent_name)
		con.setRegInfo(u'password', self.password)
		con.setRegInfo(u'name', self.agent_name)
		con.setRegInfo(u'email', self.agent_name+'@fipper.org')
		for info in req.keys():
			if info != u'instructions' and info != u'key' \
			and info != u'username' and info != u'password' \
			and info != u'name' and info != u'email':
			    #print "enter %s;" % info
			    #print "SAYING DEFAULT"
			    con.setRegInfo( info, "imonlyanagent" )
		con.sendRegInfo()
		req = con.getRegInfo()
		return req['username']
		
	def login(self,con,resource):
		'''Login en el servidor'''
		#~ print "Attempting to log in..."
		if con.auth(self.jUsername,self.password,resource):
		    #~ print "Logged in as %s in server " % ( self.jUsername )
		    pass
		else:
		    print "eek -> ", con.lastErr, con.lastErrCode
		    return
		con.requestRoster()
		con.sendInitPresence()
		#~ print "Ok, ready"
		return

	def stabilizeConnection(self):
		'''Lanzamos un hilo que mantenga viva una conexion'''
		thread.start_new_thread(self.keepAlive, tuple())
	
		return
		
	def registerInJUD(self):
		'''Registra al agente en el JUD'''
		# Primero tendremos que encontrar el JUD en el que registrarnos
		a = self.con['fipper'].requestAgents()
		for k,v in a.items():
			if v['service'] == u'jud':
				self.jud = k
				break
		if self.jud:
			i = self.jud.find('.')
			self.jud = self.jud[0:i]
		
			# Una vez tenemos el JUD encontrado, a registrarse
			self.con['fipper'].requestRegInfo(self.jud)
			req = self.con['fipper'].getRegInfo()
			for info in req.keys():
				if info == u'last':
					#print "enter %s;" % info
					self.con['fipper'].setRegInfo(info, 'fipperagent')
				elif info == u'nick':
					#print "enter %s;" % info
					self.con['fipper'].setRegInfo(info, self.agent_name)
				elif info == u'nick' or info == u'instructions':
					pass
				else:
					#print "enter %s;" % info
					#print "SAYING DEFAULT"
					self.con['fipper'].setRegInfo( info, "imonlyanagent" )
			self.con['fipper'].sendRegInfo(self.jud)
		return
	
	def getJUDWhereLastName(self,lastname):
		i = jabber.Iq(self.jud+'.'+self.world)
		i.setType('set')
		i.setFrom(self.jid[0])
		i.setID("judsearch1")
		i.setQuery("jabber:iq:search")
		qp = '<last>'+lastname+'</last>'
		i.setQueryPayload(qp)
		#print xmlcolor.colorXML(i.asNode(),0)
		self.con['fipper'].send(i)
		#print xmlcolor.colorXML(i)
		while self.flag == 0:
			time.sleep(0.5)
		self.flag = 0
		return self.tempjud
	
	def welcomePack(self):
		'''Genera y/o actualiza el service-root (pack de bienvenida) del agente'''
		#print "WELCOMEPACK"
		while(1):
			
			jud = self.getJUDWhereLastName('fipperagent')
						
			# Hacemos a todos los agentes "amigos" nuestros
			for key,value in jud.items():
				if value != self.agent_name:
					self.con['fipper'].send(jabber.Presence(key, 'subscribe'))
					#print 'suscribo ' + str(key)
			
			# Construimos un AD FIPA-compliant. La clave es el agent-name y 
			# el valor el agent-locator
			self.con['fipper'].requestRoster()
			roster = self.con['fipper'].getRoster()
			for key,value in jud.items():
				if roster.isOnline(key):
				   	self.ad[key] = value    # Anyadirlo al AD
					#print 'anyado agente ' + str(key) + ' ' + str(value)

			#~ print 'AD:'
			#~ print self.ad
		
			
			# Construimos el SD
			# Para cada agente del AD
			#     para cada servicio que ofrece ese agente
			#        registrar servicio en sd = dict()
			#rosterjid = roster.getJIDs()
			#print rosterjid
			#print self.myroster
			
			for item in self.ad.keys():
			   	#print item
				'''
			   	i = item.find('@')
				node = item[0:i]
				print node
				server = item[i:]
				print server
				'''
				for jid in self.myroster:
				   	#print 'SERV:' + str(jid)
					#rint 'RESOURCE: ' + str(jid.getResource())
					i = jid.find('/')
					stripped = jid[0:i]
					resource = jid[i+1:]
					if stripped == item and  resource != 'fipper':
					   	#print '#############################################servicio encontrado'
					   	if self.sd.has_key(resource):
						   	l = self.sd[resource]
						else:
							l = list()
						
						if not jid in l: l.append(str(jid))
						self.sd[resource] = l
						#print 'anyado servicio' + str(jid)
							
			#~ print 'SD:'
			#~ print self.sd
			
			time.sleep(5.0)  # Dormir un rato hasta la siguiente actualizacion
		return


		
