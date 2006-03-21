from xmppd import filter


class miFiltro(filter.Filter):

	def test(self,stanza):
		return True

	def filter(self,session,stanza):
		#stanza.setBody("YOU HAVE BEEN FILTERED")
		print "YOU HAVE BEEN FILTERED"
		return stanza
