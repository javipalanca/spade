

class Filter:

	def __init__(self,router):
		self._router=router

	def test(self, stanza):
		#must be overloaded
		raise NotImplemented

	def filter(self, session,stanza):
		#must be overloaded
		raise NotImplemented
