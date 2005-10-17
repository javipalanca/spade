import threading
import Queue

class MessageList(Queue.Queue):
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
		threading.Thread.__init__(self)
		self.__messages = MessageList()

	def __getMessage(self, block, timeout):
		try:
			message = self.__messages.get(block, timeout)
		except Queue.Empty:
			message = None
		return message
		
	def receive(self):
		return self.__getMessage(False, None)
	
	def blockingReceive(self, time_seg = None):
		return self.__getMessage(True, time_seg)

	def postMessage(self, message):
		if (message != None):
			self.__messages.put(message)

	def putBackMessage(self, message):
		if (message != None):
			self.__messages.putAfter(message)
