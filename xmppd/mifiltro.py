import filter


class miFiltro(filter.Filter):

	def __init__(self):
		print "me inicio"


	def test(self,stanza):
		return True

	def filter(self,stanza):
		stanza.setBody("YOU HAVE BEEN FILTERED")
		return stanza
