from xmppd import filter

class MUCFilter(filter.Filter):
	def __init__(self, router):
		self._router = router

	def test(self,stanza):
		to = stanza['to']
		try:
			domain = to.getDomain()
			if domain == self._router._owner.mucjid:
				return True
			else:
				return False
		except:
			return False


	def filter(self,session,stanza):
		# Process message
		self._router.DEBUG("Stanza for MUC component", 'info')
		self._router._owner.MUC.dispatch(session, stanza)
		self._router.DEBUG("Stanza dispatched by MUC component", 'info')
		return None

