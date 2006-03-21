import filter

class ACC(filter.Filter):

	def test(self,stanza):
		simple_to = str(stanza['to'])
		if not('@' in simple_to):  # Component name
			# SPADE CASE: message directed to the ACC component
			if simple_to[0:4] == "acc.":
				return True
		return False


	def filter(self,session,stanza):

		receivers = self.getRealTo(stanza)
		to = str(receivers[0])  # FIX THIS TO ALLOW MULTIPLE RECEIVERS
		# We do NOT raise the NodeProcessed exception, the message follows its normal course from here
		stanza['to'] = to
		return stanza

