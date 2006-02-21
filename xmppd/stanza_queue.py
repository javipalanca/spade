import Queue

class StanzaQueue(Queue.Queue):

	def init(self):
		self._init(0)

	def append(self,stanza):
		self.put(stanza)

	def pop(self):
		return self.get()

	def __iter__(self):
		self.mutex.acquire()
		n = iter(self.queue)
		self.mutex.release()

		return n
