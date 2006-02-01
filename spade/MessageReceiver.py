import threading
from Queue import *

class MessageList(Queue):
    def putAfter(self, item, block=True, timeout=None):
        self.not_full.acquire()
        try:
            if not block:
                if self._full():
                    raise Full
            elif timeout is None:
                while self._full():
                    self.not_full.wait()
            else:
                if timeout < 0:
                    raise ValueError("'timeout' must be a positive number")
                endtime = _time() + timeout
                while self._full():
                    remaining = endtime - _time()
                    if remaining <= 0.0:
                        raise Full
                    self.not_full.wait(remaining)
            self._putAfter(item)
            self.not_empty.notify()
        finally:
            self.not_full.release()

    def _putAfter(self, item):
        self.queue.appendleft(item)

    
class MessageReceiver(threading.Thread):
	def __init__(self):
		try:
			import psyco
			psyco.full()
		except ImportError:
			pass
		threading.Thread.__init__(self)
		self.__messages = MessageList(0)
		self.setDaemon(True)

	def __getMessage(self, block, tout):
		try:
			message = self.__messages.get(block, tout)
		except Empty:
			message = None
			#print "MESSAGE = None - Empty "+str(tout)
		except:
			message = None
			#time.sleep(1)
			#print "MESSAGE = None - otra"

		return message
		
	def receive(self):
		"""
		returns a message if available
		else returns None
		"""
		return self.__getMessage(False, None)
	
	def blockingReceive(self, time_seg = None):
		"""
		waits for a message during time_seg
		if time_seg == None waits until a message is received
		if no message is received returns None
		"""
		return self.__getMessage(True, time_seg)

	def postMessage(self, message):
		if (message != None):
			self.__messages.put(message,block=True)
			self.kk()
	def kk(self):
		print "QSIZE: " + str(self.__messages.qsize())

	def putBackMessage(self, message):
		if (message != None):
			self.__messages.putAfter(message)

