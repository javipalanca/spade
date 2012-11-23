# -*- coding: utf-8 -*-
import threading
import sys
from Queue import *
import time


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
        self.setDaemon(False)
        #self.__messages = MessageList(0)
        self.__messages = Queue(0)

    '''def __getMessage(self, block, tout):
        try:
            message = self.__messages.get(block, tout)
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
    '''

    def __getMessage(self, block, tout):
        t_sleep = 0.01
        message = None
        if not block:
            try:
                message = self.__messages.get_nowait()  # (block, tout)
            except Empty:
                message = None
        else:
            while not self._forceKill.isSet():
                if tout is not None:
                    t = tout
                    while t > 0.0:
                        try:
                            message = self.__messages.get_nowait()
                        except Empty:
                            message = None
                        if message is not None:
                            return message
                        t -= t_sleep
                        time.sleep(t_sleep)
                else:
                    try:
                        message = self.__messages.get_nowait()
                    except Empty:
                        message = None
                    if message is not None:
                        return message
                    time.sleep(t_sleep)

        return message

    """
    def receive(self):
        #returns a message if available
        #else returns None
        return self.__getMessage(False, None)
    """
    def _receive(self, block=False, timeout=None, template=None):
        """
        waits for a message during timeout
        if timeout == None waits until a message is received
        if no message is received returns None
        """
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
            if not block:
                return None
            else:
                endtime = time.time() + timeout
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
        if (message is not None):
            self.post_mutex.acquire()
            #self.__messages.put_commit(self.__messages.put(message,block=True))
            self.not_full.acquire()
            self.__messages.put(message, block=True)
            self.not_empty.notify()
            self.not_full.release()
            self.post_mutex.release()
        return True
