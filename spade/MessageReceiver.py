import threading
import sys
from Queue import *
import time

#from munkware.mwQueue import *

# Changed to be a 'daemonic' python Thread
class MessageReceiver(threading.Thread):
	def __init__(self):
		try:
			import psyco
			psyco.full()
		except ImportError:
			pass
		threading.Thread.__init__(self)
		self.post_mutex = threading.Lock()
		self.mutex = threading.Lock()
		self.not_empty = threading.Condition(self.mutex)
		self.not_full = threading.Condition(self.mutex)
		self.setDaemon(True)
		#self.__messages = MessageList(0)
		self.__messages = Queue(0)

	def __getMessage(self, block, tout):
		try:
			#if block:
			#	block_int = 1
			#else:
			#	block_int = 0
			#item = self.__messages.get(block_int)#, tout)
			message = self.__messages.get(block, tout)
			#self.__messages.get_commit(item[0])
			#message = item[1]
			#print ">>> __getMessage: SUCCESS "
		except Empty:
			message = None
			#print "MESSAGE = None - Empty "+str(tout)
			#print ">>> __getMessage: EMPTY"
		except:
			message = None
			#time.sleep(1)
			#print "MESSAGE = None - otra.", sys.exc_info()[0]
			#print ">>> __getMessage: FUCKING EXCEPTION"

		return message
	"""
	def receive(self):
		#returns a message if available
		#else returns None
		return self.__getMessage(False, None)
	"""
	def _receive(self, block = False, timeout = None, template = None):
		"""
		waits for a message during timeout
		if timeout == None waits until a message is received
		if no message is received returns None
		"""
		#print ">>> blockingReceive time_seg = " + str(time_seg)
		if not template:
			return self.__getMessage(block, timeout)
		else:
			self.not_empty.acquire()
			for msg in self.__messages.queue:
				if template.match(msg):
					self.not_empty.release()
					self.__messages.queue.remove(msg)
					return msg
			self.not_empty.release()
			if not block: return None
			else:
				endtime = time.time()+timeout
				self.not_empty.acquire()
				while True:
					for msg in self.__messages.queue:
						if template.match(msg):
							self.not_empty.release()
							self.__messages.queue.remove(msg)
							return msg
					remaining = endtime - time.time()
					if timeout and remaining <= 0.0:
						self.not_empty.release()
						return None
					self.not_empty.wait(remaining)

	def postMessage(self, message):
		if (message != None):
			self.post_mutex.acquire()
			#self.__messages.put_commit(self.__messages.put(message,block=True))
			self.not_full.acquire()
			self.__messages.put(message,block=True)
			self.not_empty.notify()
			self.not_full.release()
			#print ">>>>>MSG posteado DE VERDAD: " + str(message.getContent())
			self.post_mutex.release()
		return True

