import filter

class Console(filter.Filter):

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
		self.servercommandHandler(session, stanza)
		raise NodeProcessed


	def servercommandHandler(self, session, stanza):
                simple_from = ''
                for k, v in self._owner.routes.items():
                        if v == session:
                                simple_from = k
                if simple_from == '':
                        # Bizarre situation when a command has arrived from a non-existent session
                        return
                username = simple_from.split('@')[0]
                if self._owner.AUTH.isadmin(str(username)):
                        # An admin has sent a command
                        body = stanza.getBody()
                        if body == 'SAVEDB':
                                try:
                                        if self._owner.DB.savedb():
                                                simple_to = str(stanza['to'])
                                                rep = Message(simple_from,'Database Saved Succesfully', frm=simple_to)
                                                session.enqueue(rep)
                                except:
                                        pass
                        elif body == 'LOADDB':
                                try:
                                        if self._owner.DB.loaddb():
                                                simple_to = str(stanza['to'])
                                                rep = Message(simple_from,'Database Loaded Succesfully', frm=simple_to)
                                                session.enqueue(rep)
                                except:
                                        pass
                        elif body == 'DB':
                                try:
                                        content = str(self._owner.DB.listdb())
                                        simple_to = str(stanza['to'])
                                        rep = Message(simple_from,content,frm=simple_to)
                                        session.enqueue(rep)
                                except:
                                        pass

                                                                                                           410,0-1     Final


