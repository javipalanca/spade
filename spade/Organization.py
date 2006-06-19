from xmpp import *
from Queue import *

class Organization:

	def __init__(self, behavior, name, nick, subject=None, whitelist=[], blacklist=[], passwd=None):

		self.status    = "disconnected"

		self.behavior  = behavior
		self.name      = name
		self.nick      = nick
		self.subject   = subject
		self.whitelist = whitelist
		self.blacklist = blacklist
		self.passwd    = passwd

		self._roster   = dict()

		self.__messages = Queue(0)

		self.connect()


	###### From the MessageReceiver class

	def __getMessage(self, block, tout):
		try:
			message = self.__messages.get(block, tout)
		except Empty:
			message = None
		except:
			message = None

		return message
	def _receive(self, block = False, timeout = None):
		"""
		waits for a message during time_seg
		if time_seg == None waits until a message is received
		if no message is received returns None
		"""
		return self.__getMessage(block, timeout)

	def postMessage(self, message):
		if (message != None):
			self.__messages.put(message,block=True)
		return True

	def send(self, msg):
		self.behavior.myAgent._jabber.send(msg)

	###### Ends the MessageReceiver class

	def presenceCB(self, message):
		if self._status != "disconnected":

			if message.getType() == "error":
				self.disconnect()

			elif message.getType == None or message.getType == "available":
				if self.status == "connecting": self.status = "connected"
				self.addToRoster(message)

			elif message.getType() == "unavailable":
				self.delFromRoster(message)


	def connect(self):

		to  = self.name + self.behavior.myAgent.getMUC() + "/" + self.nick
		frm = self.behavior.myAgent.getAID().getName()
		x   = xmpp.protocol.Node('http://jabber.org/protocol/muc x')

		msg = Presence(to = to, frm = frm)
		msg.addData(x)

		self._status = "connecting"

		self.send(msg)

	def disconnect(self):

		to  = self.name + self.behavior.myAgent.getMUC() + "/" + self.nick
		frm = self.behavior.myAgent.getAID().getName()

		msg = Presence(to = to, frm = frm, typ = "unavailable")

		self._status = "disconnected"

		self.send(msg)


	def addToRoster(self, message):

		frm = message.getFrom()

		if not self._roster.has_key(frm):
			self._roster[frm] = dict()

		for child in message.getChildren():
			if child.getNamespace() == "http://jabber.org/protocol/muc#user":
				for child2 in child.getChildren():
					if child2.getName() == "item":
						for attr,value in child2.items():
							self._roster[frm][attr]=value

	def delFromRoster(self, message):

		frm = message.getFrom()

		try:
			del self._roster[frm]
		except:
			pass
