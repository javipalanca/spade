"""A multi-producer, multi-consumer, transactional queue."""

import os
import cPickle

class Empty(Exception):
    "Exception raised by Queue.get(block=0)/get_nowait()."
    pass
class Full(Exception):
    "Exception raised by Queue.put(block=0)/get_nowait()."
    pass
class NoQueueDir(Exception):
    "Exception raised by BaseACIDQueue._init"
    pass
class BadIndex(Exception):
    "Exception raised by Queue.put_commit(), Queue.get_commit(), Queue.put_rollback() and Queue.get_rollback()"
    pass


class CallbackTemplate:
    '''The "right" thing to do here is to take the ndx, item tuple passed in put() and start making a map that you can keep up with throughout the life of this object.  Delete things as they are totally deleted from the queue (i.e. in put_rollback() and get_commit()).  Use the get() method to do queue prioritizations.
    '''
    def __init__(self):
        pass
    def put(self, ndx_item_tuple):
        print "put >", ndx_item_tuple
    def put_rollback(self, ndx):
        print "put_rollback >", ndx
    def put_commit(self, ndx):
        print "put_commit>", ndx
    def get(self, avail_q):
        #the get() method expects to be able to pass in self.avail_q
        #self.avail_q should be a list-like object
        #if you have extended/modified the munkware library and expect this callback to work you must maintain the naming convention of self.avail_q
        #return a modified list-like object back to calling code
        print "get >", avail_q
        return avail_q
    def get_rollback(self, ndx):
        print "get_rollback >", ndx
    def get_commit(self, ndx):
        print "get_commit >", ndx

class BaseTransactionalQueue: # Transactional Queue
    def __init__(self, maxsize=0, requeue_to_end=0, callback=None):
        """Initialize a Transactional Queue object.
        """
        import thread
        self.requeue_to_end = requeue_to_end # determines whether get_rollback()s are put to the beginning or end of the queue - the default is to the beginning of the queue

        #PUT STATUS
        self.put_q_mutex = thread.allocate_lock()
        #AVAIL STATUS
        self.avail_q_mutex = thread.allocate_lock()
        self.avail_esema = thread.allocate_lock()
        #RQSTD STATUS
        self.rqstd_q_mutex = thread.allocate_lock()
        #COUNTER MUTEX - used for determining whether the queue is full or not
        self.counter_mutex = thread.allocate_lock()
        #FULL MUTEX
        self.full_mutex = thread.allocate_lock()
        self.callback = callback

        #Initialize
        self._init(maxsize)
        if self._empty():
            self.avail_esema.acquire()


    def empty(self):
        try:
            self.avail_q_mutex.acquire()
            n = self._empty()
        finally:
            self.avail_q_mutex.release()
        return n

    def full(self):
        try:
            self.counter_mutex.acquire()
            n = self._full()
        finally:
            self.counter_mutex.release()
        return n

    def put(self, item, block=1):
        release_full_mutex = 1
        if block:
            self.full_mutex.acquire()
        elif not self.full_mutex.acquire(0):
            raise Full
        try:
            self.counter_mutex.acquire()
            self.put_q_mutex.acquire()
            ndx = self.ndx
            self.ndx = self.ndx + 1
            self._put_add(ndx, (ndx, item))
            if not self.callback == None:
                self.callback.put((ndx, item))
            self._increment_counter()
            release_full_mutex = not self._full()
            #if any exceptions are raised, we don't want to cleanup
            self._put_cleanup()
        finally:
            self.put_q_mutex.release()
            if release_full_mutex:
                self.full_mutex.release()
            self.counter_mutex.release()
        return ndx

    def put_rollback(self, ndx):
        try:
            self.counter_mutex.acquire()
            self.put_q_mutex.acquire()
            was_full = 0
            if not self._put_ndx_exists(ndx):
                raise BadIndex
            was_full = self._full()
            #get item off of put_q
            self._put_del(ndx, 1)
            if not self.callback == None:
                self.callback.put_rollback(ndx)
            self._decrement_counter()
            #if any exceptions are raised, we don't want to cleanup
            self._put_rollback_cleanup()
        finally:
            if was_full:
                self.full_mutex.release()
            self.put_q_mutex.release()
            self.counter_mutex.release()

    def un_put(self, ndx):
        return self.put_rollback(ndx)

    #def put_ack(self, ndx):
    def put_commit(self, ndx):
        try:
            #get item off of put_q
            self.put_q_mutex.acquire()
            self.avail_q_mutex.acquire()
            #check to see if nxd exists
            #if not, raise BadIndex Exception
            if not self._put_ndx_exists(ndx):
                raise BadIndex
            item = self._put_del(ndx)
            #put the item on avail_q
            was_empty = self._empty()
            self._avail_add(item)
            if not self.callback == None:
                self.callback.put_commit(ndx)
            if was_empty:
                self.avail_esema.release()
            #if any exceptions are raised, we don't want to cleanup
            self._put_commit_cleanup()
        finally:
            self.avail_q_mutex.release()
            self.put_q_mutex.release()

    def get(self, block=1):
        if block:
            self.avail_esema.acquire()
        elif not self.avail_esema.acquire(0):
            raise Empty
        release_esema = 1
        #get item off of avail_q
        try:
            self.avail_q_mutex.acquire()
            self.rqstd_q_mutex.acquire()
            if not self.callback == None:
                self.avail_q = self.callback.get(self.avail_q)
            item = self._avail_del()
            release_esema = not self._empty()
            #put item on rqstd_q
            ndx = item[0]
            self._rqstd_add(ndx, item)
            #if any exceptions are raised, we don't want to cleanup
            self._get_cleanup()
        finally:
            if release_esema:
                self.avail_esema.release()
            self.rqstd_q_mutex.release()
            self.avail_q_mutex.release()
        # return (ndx, item) tuple
        return item

    def get_rollback(self, ndx, requeue_to_end=-1):
        # requeue_to_end = -1 : not overriden
        # requeue_to_end = 0  : requeue to beginning
        # requeue_to_end = 1  : requeue to end
        try:
            #get item off of rqstd_q
            self.avail_q_mutex.acquire()
            self.rqstd_q_mutex.acquire()
            was_empty = 0
            if not self._rqstd_ndx_exists(ndx):
                raise BadIndex
            item = self._rqstd_del(ndx)
            #put the item on avail_q
            was_empty = self._empty()
            if requeue_to_end == -1: # means that it requeue_to_end hasn't been re-assigned or hasn't been re-assigned to anything meaningful
                if self.requeue_to_end:
                    self._avail_add(item)
                else:
                    self._avail_add_to_begin(item)
            else:
                if requeue_to_end:
                    self._avail_add(item)
                else:
                    self._avail_add_to_begin(item)
            #if any exceptions are raised, we don't want to cleanup
            if not self.callback == None:
                self.callback.get_rollback(ndx)
            self._get_rollback_cleanup()
        finally:
            self.rqstd_q_mutex.release()
            self.avail_q_mutex.release()
            if was_empty:
                self.avail_esema.release()
    def un_get(self, ndx, requeue_to_end=-1):
        return self.get_rollback(ndx, requeue_to_end)

    #def get_ack(self, ndx):
    def get_commit(self, ndx):
        try:
            self.counter_mutex.acquire()
            #get item off of rqstd_q
            self.rqstd_q_mutex.acquire()
            #initialize was_full to 0 in case BadIndex is raised
            #that way, we won't unnecessarily release full_mutex
            was_full = 0
            #check to see if nxd exists
            #if not, raise BadIndex Exception
            if not self._rqstd_ndx_exists(ndx):
                raise BadIndex
            was_full = self._full()
            self._rqstd_del(ndx, 1)
            self._decrement_counter()
            #if any exceptions are raised, we don't want to cleanup
            if not self.callback == None:
                self.callback.get_commit(ndx)
            self._get_commit_cleanup()
        finally:
            if was_full:
                self.full_mutex.release()
            self.rqstd_q_mutex.release()
            self.counter_mutex.release()



    # Override these methods to implement other queue organizations
    # (e.g. stack or priority queue).
    # These will only be called with appropriate locks held

    # Initialize the queue representation
    def _init(self, maxsize):
        self.maxsize = maxsize
        self.ndx = 1
        self.put_q = {}
        self.avail_q = []
        self.rqstd_q = {}
        self.counter = 0

    # Check whether the queue is empty
    def _empty(self):
        return not self.avail_q

    # Check whether the queue is full
    def _full(self):
        return self.maxsize > 0 and self.counter >= self.maxsize

    # increment full counter
    def _increment_counter(self):
        self.counter = self.counter + 1

    # decrement full counter
    def _decrement_counter(self):
        self.counter = self.counter - 1

    # See if ndx exists on put queue
    def _put_ndx_exists(self, ndx):
        return self.put_q.has_key(ndx)

    # Add an item to the put queue
    def _put_add(self, ndx, item):
        self.put_q[ndx] = item

    # Delete an item from the put queue
    def _put_del(self, ndx, delete=0):
        item = self.put_q[ndx]
        del self.put_q[ndx]
        return item

    # Add an item to the avail queue
    def _avail_add(self, item):
        self.avail_q.append(item)

    # Add an item to the beginning of avail queue
    def _avail_add_to_begin(self, item):
        self.avail_q.insert(0, item)

    # Delete an item from the avail queue
    def _avail_del(self):
        item = self.avail_q[0]
        del self.avail_q[0]
        return item

    #See if ndx exists on rqstd queue
    def _rqstd_ndx_exists(self, ndx):
        return self.rqstd_q.has_key(ndx)

    # Add an item to the rqstd queue
    def _rqstd_add(self, ndx, item):
        self.rqstd_q[ndx] = item

    # Delete an item from the rqstd queue
    def _rqstd_del(self, ndx, delete=0):
        item = self.rqstd_q[ndx]
        del self.rqstd_q[ndx]
        return item



    #CLEANUP METHODS
    #cleanup put
    def _put_cleanup(self): #this isn't really necessary here as we override put() in ACID queue
        pass

    #cleanup put_commit
    def _put_commit_cleanup(self):
        pass

    #cleanup _put_rollback
    def _put_rollback_cleanup(self):
        pass

    #cleanup get
    def _get_cleanup(self):
        pass

    #cleanup get_commit
    def _get_commit_cleanup(self):
        pass

    #cleanup get_rollback
    def _get_rollback_cleanup(self):
        pass


class BaseACIDQueue(BaseTransactionalQueue): #Python ACID Queue
    def __init__(self, dir_name, maxsize=0, requeue_to_end=0, callback=None):
        """Initialize a Python ACID Queue object.  Benchmarked at 150 queue transactions per second on a P-III.

        """
        self.dir_name = os.path.abspath(dir_name)
        BaseTransactionalQueue.__init__(self, maxsize, requeue_to_end, callback)
        #self._init(maxsize)

    # Initialize the queue representation
    def _init(self, maxsize):
        self.maxsize = maxsize
        #In-memory queues/indeces
        self.put_q = {}
        self.avail_q = []
        self.rqstd_q = {}
        self.counter = 0
        #transaction log files
        self.put_log = os.path.join(self.dir_name, 'put_log')
        self.put_commit_log = os.path.join(self.dir_name, 'put_commit_log')
        self.put_rollback_log = os.path.join(self.dir_name, 'put_rollback_log')
        self.get_log = os.path.join(self.dir_name, 'get_log')
        self.get_commit_log = os.path.join(self.dir_name, 'get_commit_log')
        self.get_rollback_log = os.path.join(self.dir_name, 'get_rollback_log')
        #On-disk queues
        self.put_q_1 = os.path.join(self.dir_name, 'put_q_1')
        self.put_q_was = os.path.join(self.dir_name, 'put_q_was')
        self.avail_q_1 = os.path.join(self.dir_name, 'avail_q_1')
        self.avail_q_was = os.path.join(self.dir_name, 'avail_q_was')
        self.rqstd_q_1 = os.path.join(self.dir_name, 'rqstd_q_1')
        self.rqstd_q_was = os.path.join(self.dir_name, 'rqstd_q_was')
        #On-disk indeces
        self.ndx_fn_1 = os.path.join(self.dir_name, 'ndx_1')
        self.ndx_fn_was = os.path.join(self.dir_name, 'ndx_was')
        self.counter_1 = os.path.join(self.dir_name, 'counter_1')
        self.counter_was = os.path.join(self.dir_name, 'counter_was')
        # Check to see if the directory exists
        if not os.path.isdir(self.dir_name):
            raise NoQueueDir
        # Do initialization and recovery stuff
        #if any of these log files exist, it means that we should delete the corresponding "_was" files
        #deleting the "_was files" will cause the queue to continue to process the new q files
        if os.path.isfile(self.put_log):
            try:
                os.unlink(self.put_q_was)
            except:
                pass
            os.unlink(self.put_log)
        if os.path.isfile(self.put_commit_log):
            try:
                os.unlink(self.put_q_was)
                os.unlink(self.avail_q_was)
            except:
                pass
            os.unlink(self.put_commit_log)
        if os.path.isfile(self.put_rollback_log):
            try:
                os.unlink(self.put_q_was)
            except:
                pass
            os.unlink(self.put_rollback_log)
        if os.path.isfile(self.get_log):
            try:
                os.unlink(self.avail_q_was)
                os.unlink(self.rqstd_q_was)
            except:
                pass
            os.unlink(self.get_log)
        if os.path.isfile(self.get_commit_log):
            try:
                os.unlink(self.rqstd_q_was)
            except:
                pass
            os.unlink(self.get_commit_log)
        if os.path.isfile(self.get_rollback_log):
            try:
                os.unlink(self.rqstd_q_was)
                os.unlink(self.avail_q_was)
            except:
                pass
            os.unlink(self.get_rollback_log)

        # Index initialization
        if (os.path.isfile(self.ndx_fn_1) or os.path.isfile(self.ndx_fn_was)):
            if os.path.isfile(self.ndx_fn_was):
                ndx_file = open(self.ndx_fn_was, 'r')
            else:
                ndx_file = open(self.ndx_fn_1, 'r')
            self.ndx = cPickle.load(ndx_file)
            ndx_file.close()
        else:
            self.ndx = 1
            self._sync_ndx()
        # counter initialization
        if (os.path.isfile(self.counter_1) or os.path.isfile(self.counter_was)):
            if os.path.isfile(self.counter_was):
                counter_file = open(self.counter_was, 'r')
            else:
                counter_file = open(self.counter_1, 'r')
            self.counter = cPickle.load(counter_file)
            counter_file.close()
        else:
            self.counter = 0
            self._sync_counter()
        # put_q initialization
        if (os.path.isfile(self.put_q_1) or os.path.isfile(self.put_q_was)):
            if os.path.isfile(self.put_q_was):
                put_q = open(self.put_q_was, 'r')
            else:
                put_q = open(self.put_q_1, 'r')
            self.put_q = cPickle.load(put_q)
            put_q.close()
        else:
            self.put_q = {}
            self._sync_put_q()
        #avail_q initialization
        if (os.path.isfile(self.avail_q_1) or os.path.isfile(self.avail_q_was)):
            if os.path.isfile(self.avail_q_was):
                avail_q = open(self.avail_q_was, 'r')
            else:
                avail_q = open(self.avail_q_1, 'r')
            self.avail_q = cPickle.load(avail_q)
            avail_q.close()
        else:
            self.avail_q = []
            self._sync_avail_q()
        #rqstd_q initialization
        if (os.path.isfile(self.rqstd_q_1) or os.path.isfile(self.rqstd_q_was)):
            #still need to check to see if 1 and 2 are equal
            #and if 2 exists
            if os.path.isfile(self.rqstd_q_was):
                rqstd_q = open(self.rqstd_q_was, 'r')
            else:
                rqstd_q = open(self.rqstd_q_1, 'r')
            self.rqstd_q = cPickle.load(rqstd_q)
            rqstd_q.close()
        else:
            self.rqstd_q = {}
            self._sync_rqstd_q()
        # check to see if full
        if self._full():
            self.full_mutex.acquire()


    def get(self, block=1):
        #overriding get() because we need to return the item itself to the requester,
        #but put the (ndx, filename) tuple on the rqstd_q

        if block:
            self.avail_esema.acquire()
        elif not self.avail_esema.acquire(0):
            raise Empty
        release_esema = 1
        #get item off of avail_q
        try:
            self.avail_q_mutex.acquire()
            self.rqstd_q_mutex.acquire()
            if not self.callback == None:
                self.avail_q = self.callback.get(self.avail_q)
            ndx_tuple = self._avail_del()
            ndx, filename = ndx_tuple
            restore_file = open(filename, 'r')
            restored_item = cPickle.load(restore_file)
            item = (ndx, restored_item)
            release_esema = not self._empty()
            #put item on rqstd_q
            self._rqstd_add(ndx, ndx_tuple)
            #if any exceptions are raised, we don't want to cleanup
            self._get_cleanup()
        finally:
            self.avail_q_mutex.release()
            if release_esema:
                self.avail_esema.release()
            self.rqstd_q_mutex.release()
        # return (ndx, item) tuple
        return item



    # Synchronization methods
    def _sync_ndx(self):
        ndx_file = open(self.ndx_fn_1, 'wb')
        cPickle.dump(self.ndx, ndx_file, 1)
        ndx_file.close()

    def _backup_ndx(self):
        os.rename(self.ndx_fn_1, self.ndx_fn_was)

    def _sync_counter(self):
        counter_file = open(self.counter_1, 'wb')
        cPickle.dump(self.counter, counter_file, 1)
        counter_file.close()

    def _backup_counter(self):
        os.rename(self.counter_1, self.counter_was)

    def _sync_put_q(self):
        put_q_1 = open(self.put_q_1, 'wb')
        cPickle.dump(self.put_q, put_q_1, 1)
        put_q_1.close()

    def _backup_put_q(self):
        os.rename(self.put_q_1, self.put_q_was)

    def _sync_avail_q(self):
        avail_q_1 = open(self.avail_q_1, 'wb')
        cPickle.dump(self.avail_q, avail_q_1, 1)
        avail_q_1.close()

    def _backup_avail_q(self):
        os.rename(self.avail_q_1, self.avail_q_was)

    def _sync_rqstd_q(self):
        rqstd_q_1 = open(self.rqstd_q_1, 'wb')
        cPickle.dump(self.rqstd_q, rqstd_q_1, 1)
        rqstd_q_1.close()

    def _backup_rqstd_q(self):
        os.rename(self.rqstd_q_1, self.rqstd_q_was)


    # 
    # Queue modification methods
    # 
    # Add an item to the put queue
    def _put_add(self, ndx, item):
        self._backup_ndx()
        self._backup_put_q()
        item_body = item[1]
        item_fn = os.path.join(self.dir_name, str(ndx))
        #Pickle the item to its own pickle file
        pickle_file = open(item_fn, 'wb')
        cPickle.dump(item_body, pickle_file, 1)
        pickle_file.close()
        #the item portion of the item tuple is now the pickled file's filename
        self.put_q[ndx] = (ndx, item_fn)
        self._sync_ndx()
        os.unlink(self.ndx_fn_was)
        self._sync_put_q()
        #os.unlink(self.put_q_was)

    #See if ndx exists on put queue
    def _put_ndx_exists(self, ndx):
        return self.put_q.has_key(ndx)

    # increment full counter
    def _increment_counter(self):
        self._backup_counter()
        self.counter = self.counter + 1
        self._sync_counter()
        os.unlink(self.counter_was)

    # decrement full counter
    def _decrement_counter(self):
        self._backup_counter()
        self.counter = self.counter - 1
        self._sync_counter()
        os.unlink(self.counter_was)

    # Delete an item from the put queue
    def _put_del(self, ndx, delete=0):
        self._backup_put_q()
        item = self.put_q[ndx]
        del self.put_q[ndx]
        if delete:
            os.unlink(item[1])
        self._sync_put_q()
        #os.unlink(self.put_q_was)
        return item


    # Add an item to the avail queue
    def _avail_add(self, item):
        self._backup_avail_q()
        self.avail_q.append(item)
        self._sync_avail_q()
        #os.unlink(self.avail_q_was)

    # Add an item to the beginning of avail queue
    def _avail_add_to_begin(self, item):
        self._backup_avail_q()
        self.avail_q.insert(0, item)
        self._sync_avail_q()
        #os.unlink(self.avail_q_was)


    # Delete an item from the avail queue
    def _avail_del(self):
        self._backup_avail_q()
        item = self.avail_q[0]
        del self.avail_q[0]
        self._sync_avail_q()
        #os.unlink(self.avail_q_was)
        return item

    #See if ndx exists on rqstd queue
    def _rqstd_ndx_exists(self, ndx):
        return self.rqstd_q.has_key(ndx)

    # Add an item to the rqstd queue
    def _rqstd_add(self, ndx, item):
        self._backup_rqstd_q()
        self.rqstd_q[ndx] = item
        self._sync_rqstd_q()
        #os.unlink(self.rqstd_q_was)

    # Delete an item from the rqstd queue
    def _rqstd_del(self, ndx, delete=0):
        self._backup_rqstd_q()
        item = self.rqstd_q[ndx]
        del self.rqstd_q[ndx]
        if delete:
            os.unlink(item[1])
        self._sync_rqstd_q()
        #os.unlink(self.rqstd_q_was)
        return item

    #CLEANUP METHODS
    #cleanup put
    def _put_cleanup(self):
        open(self.put_log, 'w').close()
        os.unlink(self.put_q_was)
        os.unlink(self.put_log)

    #cleanup put_commit
    def _put_commit_cleanup(self):
        open(self.put_commit_log, 'w').close()
        os.unlink(self.put_q_was)
        os.unlink(self.avail_q_was)
        os.unlink(self.put_commit_log)

    #cleanup _put_rollback
    def _put_rollback_cleanup(self):
        open(self.put_rollback_log, 'w').close()
        os.unlink(self.put_q_was)
        os.unlink(self.put_rollback_log)

    #cleanup get
    def _get_cleanup(self):
        open(self.get_log, 'w').close()
        os.unlink(self.avail_q_was)
        os.unlink(self.rqstd_q_was)
        os.unlink(self.get_log)

    #cleanup get_commit
    def _get_commit_cleanup(self):
        open(self.get_commit_log, 'w').close()
        os.unlink(self.rqstd_q_was)
        os.unlink(self.get_commit_log)

    #cleanup get_rollback
    def _get_rollback_cleanup(self):
        open(self.get_rollback_log, 'w').close()
        os.unlink(self.rqstd_q_was)
        os.unlink(self.avail_q_was)
        os.unlink(self.get_rollback_log)

