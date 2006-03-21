import filter

class Component(filter.Filter):

	def test(self,stanza):
		#Counter measure for component originated messages
		the_from = stanza['from']
		simple_from = str(the_from)
		if not('@' in simple_from):  # Component-originated
			if stanza.getNamespace()==NS_COMPONENT_ACCEPT and stanza.getName()=='message':
				return True
		return False


	def filter(self,session,stanza):

			s=self._owner.getsession(to)
			#self._router.DEBUG("Component getsession("+str(to)+") ->" + str(s), 'info')
			if s:
                        	# Fake the namespace. Pose as a client
	                        stanza.setNamespace(NS_CLIENT)
        	                self._router.DEBUG("NS faked: " + str(stanza.getNamespace()), 'info')
				s.enqueue(stanza)
				self.DEBUG("There was a message for a component and it has been delivered", 'info')
				raise NodeProcessed
			else:
				return stanza


