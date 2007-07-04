from spade import *
import xmpp

class GoogleBehaviour(Behaviour.OneShotBehaviour):

	def __init__(self, msg, string,max):

		self.msg = msg
		self.string = string
		self.max = max
		Behaviour.OneShotBehaviour.__init__(self)
		self.sl0parser = SL0Parser.SL0Parser()

	def onStart(self):
		to = AID.aid("google@localhost", [ "xmpp://spade.localhost" ])
		self.msg.setSender(self.myAgent.getAID())
		self.msg.addReceiver(to);
		self.msg.setPerformative('request')
		self.msg.setOntology("google-search")
		self.msg.setLanguage("fipa-sl0")

		content = "((action (search (search-keys (sequence "
		content += self.string + ")"
		if self.max:
			content += "(search-constraints :max-results " + self.max + ")"
		content += "))))"

		self.msg.setContent(content)
		self.myAgent.send(self.msg)


	def process(self):
		error = False
		n=None
		time=None
		error = None
		msg = self.blockingReceive(20)
		if msg != None and msg.getPerformative().lower() == 'agree':
			pass
		msg = self.blockingReceive(20)
		if msg != None:
			content = self.sl0parser.parse(msg.getContent())
			if msg.getPerformative().lower() == 'inform':
				if msg.getOntology().lower() == "google-search":
					if msg.getLanguage().lower() == "fipa-sl0":
						content = self.sl0parser.parse(msg.getContent())
							
						if "result" in content:
							if "action" in content.result:
								if "search" in content.result.action:
									if "meta" in content.result.action.search:
										if "num-result" in content.result.action.search.meta:
											n = int(content.result.action.search.meta['num-result'][0])
										if "search-time" in content.result.action.search.meta:
											time = content.result.action.search.meta['search-time'][0]
									if "set" in content.result.action.search:
										set = content.result.action.search.set
										result = {}
										for i in range(0,n):
											result[set[i][1][0][1][0]] = set[i][1][1][1][0]
										payload = ""
										for k,v in result.items():
											payload += '<a href='+str(v)+'>'+str(k)+"</a>\n"
										if time:
											payload +="El tiempo de búsqueda ha sido de "+str(time) + " segundos."
										jabber_msg = xmpp.protocol.Message(self.myAgent.owner,payload, xmlns="")
										jabber_msg["from"]=self.myAgent.getAID().getName()
									        self.myAgent.jabber.send(jabber_msg)
										return 1
									else:
										error = "Lo siento Señor. Ha ocurrido un error #1 en la búsqueda. Inténtelo más tarde."
								else:
									error = "Lo siento Señor. Ha ocurrido un error #2 en la búsqueda. Inténtelo más tarde"
							else:
								error = "Lo siento Señor. Ha ocurrido un error #3 en la búsqueda. Inténtelo más tarde"
						else:
							error = "Lo siento Señor. Ha ocurrido un error #4 en la búsqueda. Inténtelo más tarde"

					else:
						error = "Lo siento Señor. Ha ocurrido un error #5 en la búsqueda. Inténtelo más tarde"

				else:
					error = "Lo siento Señor. Ha ocurrido un error #6 en la búsqueda. Inténtelo más tarde"

			else:
				error = "Lo siento Señor. Ha ocurrido un error #7 en la búsqueda. Inténtelo más tarde"

		else:
			error = "Lo siento Señor. Ahora mismo el servicio de búsqueda no está disponible. Inténtelo más tarde"

		if error:
			jabber_msg = xmpp.protocol.Message(self.myAgent.owner,error)
			jabber_msg["from"]=self.myAgent.getAID().getName()
			self.myAgent.jabber.send(jabber_msg)

		return 1


