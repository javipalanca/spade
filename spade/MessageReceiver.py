import threading
import sys
from Queue import *

#from munkware.mwQueue import *

# Changed to be a 'daemonic' python Thread
class MessageReceiver(threading.Thread):
	def __init__(self):
		try:
			import psyco
			#######psyco.full()
		except ImportError:
			pass
		threading.Thread.__init__(self)
		self.setDaemon(False)
		#self.__messages = MessageList(0)
		self.__messages = Queue(0)
		#self.setDaemon(True)

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
	def _receive(self, block = False, timeout = None):
		"""
		waits for a message during time_seg
		if time_seg == None waits until a message is received
		if no message is received returns None
		"""
		#print ">>> blockingReceive time_seg = " + str(time_seg)
		return self.__getMessage(block, timeout)

	def postMessage(self, message):
		if (message != None):
			#self.__messages.put_commit(self.__messages.put(message,block=True))
			self.__messages.put(message,block=True)
			#print ">>>>>MSG posteado DE VERDAD: " + str(message.getContent())
		return True

