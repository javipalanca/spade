from xmppd import filter

class MUCFilter(filter.Filter):

	def test(self,stanza):
		to = stanza['to']
		try:
			domain = to.getDomain()
			if domain == self_router._owner.mucjid:
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

