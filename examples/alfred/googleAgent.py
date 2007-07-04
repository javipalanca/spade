from spade import *
from spade.SL0Parser import *

from google import *

class GoogleAgent(Agent.Agent):

	class DefaultBehaviour(Behaviour.Behaviour):

		def __init__(self):
			Behaviour.Behaviour.__init__(self)
			self.sl0parser = SL0Parser()

		def process(self):
			error = False
			msg = self.blockingReceive()
			if msg != None:
				if msg.getPerformative().lower() == 'request':
					if msg.getOntology().lower() == "google-search":
						if msg.getLanguage().lower() == "fipa-sl0":
							content = self.sl0parser.parse(msg.getContent())
							ACLtemplate = Behaviour.ACLTemplate()
							ACLtemplate.setConversationId(msg.getConversationId())
							ACLtemplate.setSender(msg.getSender())
							template = (Behaviour.MessageTemplate(ACLtemplate))
							
							if "action" in content:
								if "search" in content.action:
									self.myAgent.addBehaviour(GoogleAgent.SearchBehaviour(msg,content), template)
							else:
								reply = msg.createReply()
								reply.setSender(self.myAgent.getAID())
								reply.setPerformative("refuse")
								reply.setContent("( "+msg.getContent() +"(unsuported-function "+ content.keys()[0] +"))")
								self.myAgent.send(reply)

								return -1


	
						else: error = "(unsupported-language "+msg.getLanguage()+")"
					else: error = "(unsupported-ontology "+msg.getOntology()+")"

	
				elif msg.getPerformative().lower() not in ['failure','refuse']:
						error = "(unsupported-act " + msg.getPerformative() + ")"
				if error:
					reply = msg.createReply()
					reply.setSender(self.myAgent.getAID())
					reply.setPerformative("not-understood")
					reply.setContent("( "+msg.getContent() + error+")")
					self.myAgent.send(reply)
					return -1
				

			return 1

	class SearchBehaviour(Behaviour.OneShotBehaviour):

		def __init__(self,msg,content):
			Behaviour.OneShotBehaviour.__init__(self)
			self.msg = msg
			self.content = content

		def process(self):

			error = False

			reply = self.msg.createReply()
			#reply.setConversationId("6969")#
			reply.setSender(self.myAgent.getAID())
			reply.setPerformative("agree")
			reply.setContent("(" + str(self.msg.getContent()) + " true)")
			self.myAgent.send(reply)

			max = 10
			if "search-constraints" in self.content.action.search:
				if "max-results" in self.content.action.search["search-constraints"]:
					try:
						max = int(self.content.action.search["search-constraints"]["max-results"])
						if max > 10: max = 10
					except Exception, err:
						error = '(internal-error "max-results is not an integer")'

			if "search-keys" in self.content.action.search:
				keys = self.content.action.search["search-keys"].sequence

			if error:
				reply = self.msg.createReply()
				reply.setSender(self.myAgent.getAID())
				reply.setPerformative("failure")
				reply.setContent("( "+msg.getContent() + error+")")
				self.myAgent.send(reply)
				return -1



			#gs = googolplex.Googolplex()
			#gs.maxresults(max)
			s=''
			for i in keys:
				s+=i

			#r = gs.search(s)
			google.setLicense('CsvPxVBQFHLyv1Ms2XtJhmoo3Ggp5TL0')
			data = google.doGoogleSearch(s,maxResults=max)

			content = u"((result (action (search " #+ self.msg.getContent()
			if len(data.results)>0:
				content += u" (set "
				for i in data.results:
					content += u'(google-result :title "'+ str(i.title.encode('ascii','replace')) + u'" :url "' +str(i.URL.encode('ascii','replace')) + u'")'
				content += u")"
				content += u"(meta"
				content += u" (num-result " + str(len(data.results)) + u")\n"
				content += u" (search-time " + str(data.meta.searchTime) + u")\n"
				content += u")"
			content += u"))))"


			reply.setPerformative("inform")
			reply.setContent(content)
			self.myAgent.send(reply)

			return 1


	def __init__(self,jid,passw):
		Agent.Agent.__init__(self,jid,passw)


	def setup(self):

		db = self.DefaultBehaviour()
		self.setDefaultBehaviour(db)


if __name__ == "__main__":
	g = GoogleAgent("google@localhost", "secret")
	g.start()

