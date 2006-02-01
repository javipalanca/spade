#!/usr/bin/env python


import httplib
import cPickle
import munkware
import string

class RemoteQueue:
    def __init__(self, host, port, queue_name):
        self.host = host
        self.port = port
        self.queue_name = queue_name
        self.conn = httplib.HTTPConnection('%s:%s' % (self.host, self.port))
    def put(self, put_obj):
        serialized_put_obj = cPickle.dumps(put_obj)
        self.conn.request("POST", "/%s" % self.queue_name, serialized_put_obj, {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"})
        rsp = self.conn.getresponse()
        status = rsp.status
        if status == 502: # this means a queue.Full exception
            raise munkware.mwQueue.Full
        elif status == 500: # this means an unknown exception
            raise "Unknown exception"
        location = rsp.getheader("Location", None)
        ndx = int(string.split(location, '/', 3)[3])
        return (ndx)
    def put_commit(self, ndx):
        self.conn.request("GET", "/%s/put_commit/%s" % (self.queue_name, ndx))
        rsp = self.conn.getresponse()
        status = rsp.status
        if status == 404: # this means a queue.BadIndex exception
            raise munkware.mwQueue.BadIndex
        elif status == 500: # this means an unknown exception
            raise "Unknown exception"
    def put_rollback(self, ndx):
        self.conn.request("GET", "/%s/put_rollback/%s" % (self.queue_name, ndx))
        rsp = self.conn.getresponse()
        status = rsp.status
        if status == 404: # this means a queue.BadIndex exception
            raise munkware.mwQueue.BadIndex
        elif status == 500: # this means an unknown exception
            raise "Unknown exception"
    def get(self):
        self.conn.request("GET", "/%s/avail" % self.queue_name)
        rsp = self.conn.getresponse()
        status = rsp.status
        if status == 204: # this means a queue.Empty exception
            raise munkware.mwQueue.Empty
        elif status == 500: # this means an unknown exception
            raise "Unknown exception"
        #print rsp.status, rsp.reason
        location = rsp.getheader("Location", None)
        ndx = int(string.split(location, '/', 3)[3])
        pickled_object = rsp.read()
        obj = cPickle.loads(pickled_object)
        return (ndx, obj)
    def get_commit(self, ndx):
        self.conn.request("GET", "/%s/get_commit/%s" % (self.queue_name, ndx))
        rsp = self.conn.getresponse()
        status = rsp.status
        if status == 404: # this means a queue.BadIndex exception
            raise munkware.mwQueue.BadIndex
        elif status == 500: # this means an unknown exception
            raise "Unknown exception"
    def get_rollback(self, ndx):
        self.conn.request("GET", "/%s/get_rollback/%s" % (self.queue_name, ndx))
        rsp = self.conn.getresponse()
        status = rsp.status
        if status == 404: # this means a queue.BadIndex exception
            raise munkware.mwQueue.BadIndex
        elif status == 500: # this means an unknown exception
            raise "Unknown exception"

        

if __name__ == "__main__":
    q = RemoteQueue('localhost', 8000, 'queue')
    #q.put({'a':'aaaaa', 'b':'bbbbb'})
    print "put"
    print "<< 1"
    print ">>", q.put('test')
    print "put_rollback"
    print "<< "
    print ">>", q.put_rollback(1)
    print "put"
    print "<< 2"
    print ">>", q.put('test')
    print "put_commit"
    print "<< "
    print ">>", q.put_commit(2)
    print "get"
    print "<< (2, \"test\")"
    print ">>", q.get()
    print "get_rollback"
    print "<< "
    print ">>", q.get_rollback(2)
    print "get"
    print "<< (2, \"test\")"
    print ">>", q.get()
    print "get_commit"
    print "<< "
    print ">>", q.get_commit(2)
    ## go for a queue.Full
    for num in range(3,8):
        print "put"
        print "<< %s" % num
        print ">>", q.put('test')
        print "put_commit"
        print "<< "
        print ">>", q.put_commit(num)
    print "<< Got full exception"
    try:
        q_res = q.put('test')
        print ">>", q_res
    except munkware.mwQueue.Full:
        print ">> Got a full exception"
