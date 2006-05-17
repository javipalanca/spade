from xmppd import filter

class MUCFilter(filter.Filter):

	def test(self,stanza):
		simple_to = str(stanza['to'])
		
		if not('@' in simple_to) and \
		(simple_to in self._router._owner.servernames) and \
		(stanza.getName()=='message'):
				return True
		return False


	def filter(self,session,stanza):
		# Process message
		self._router.DEBUG("Message for the server", 'info')
		return None

