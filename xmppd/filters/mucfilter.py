from xmppd import filter

class MUCFilter(filter.Filter):
	def __init__(self):
		# Build list of MUC names
		self.mucnames = []
		for name in self._router._owner.servernames:
			self.mucnames.append('muc.' + name)

	def test(self,stanza):
		to = stanza['to']
		try:
			domain = to.getDomain()
			if domain in self.mucnames:
				return True
			else:
				return False
		except:
			return False


	def filter(self,session,stanza):
		# Process message
		self._router.DEBUG("Message for MUC component", 'info')
		self._router._owner.MUC.dispatch(session, stanza)
		return None

