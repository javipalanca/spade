from pyxmpp import JabberClient, JID



class Agent:

	def __init__(self,name,server,password):
		self.name = name
		self.server = server
		self.password = password
		self.jid = JID(name,server)

	def register(self):
		pass

	def setup(self):
		#debe ser sobrecargado
		pass

	def run(self):
		#debe ser sobrecargado
		pass
