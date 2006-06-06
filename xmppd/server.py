#!/usr/bin/python
##
##   XMPP server
##
##   Copyright (C) 2004 Alexey "Snake" Nezhdanov
##   Copyright (C) 2005 Gustavo Aranda & Javier Palanca
##
##   This program is free software; you can redistribute it and/or modify
##   it under the terms of the GNU General Public License as published by
##   the Free Software Foundation; either version 2, or (at your option)
##   any later version.
##
##   This program is distributed in the hope that it will be useful,
##   but WITHOUT ANY WARRANTY; without even the implied warranty of
##   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##   GNU General Public License for more details.

Revision="$Id: xmppd.py,v 1.10 2004/10/24 04:37:19 snakeru Exp $"[5:41].replace(',v',' Rev:')

from xmpp import *
from xmppd import *
from constants import *

from stanza_queue import StanzaQueue
from Queue import Queue

import ch
import config
import db_fake
import dialback
import dummy
import jep0077
import jep0078
import roster
import router
import stream
#import accPlugin

import threading
import os

addons = [
# System stuff
    config.Config,
    db_fake.AUTH,
    db_fake.DB,

# XMPP-Core
    #stream.TLS,
    stream.SASL,
    dialback.Dialback,
    
    roster.rosterPlugIn,
    muc.MUC,


# XMPP-IM
    stream.Bind,
    stream.Session,
    router.Router,
#    privacy.Privacy,

# JEPs
    jep0077.IBR,
    jep0078.NSA

# Mine
    #ch.CH,
    #dummy.dummyClass,
    #accPlugin.accPlugIn
    ]

#if __name__=='__main__':
#    print "Firing up PsyCo"
#    from psyco.classes import *

import socket,select,random,os,thread,errno,sys,threading
from getopt import getopt
"""
_socket_state live/dead
_session_state   no/in-process/yes
_stream_state not-opened/opened/closing/closed
"""
# Transport-level flags
#SOCKET_UNCONNECTED  =0
#SOCKET_ALIVE        =1
#SOCKET_DEAD         =2
# XML-level flags
#STREAM__NOT_OPENED =1
#STREAM__OPENED     =2
#STREAM__CLOSING    =3
#STREAM__CLOSED     =4
# XMPP-session flags
#SESSION_NOT_AUTHED =1
#SESSION_AUTHED     =2
#SESSION_BOUND      =3
#SESSION_OPENED     =4

class Session:
    def __init__(self,socket,server,xmlns,peer=None):
        self.xmlns=xmlns
        if peer:
            self.TYP='client'
            self.peer=peer
            self._socket_state=SOCKET_UNCONNECTED
        else:
            self.TYP='server'
            self.peer=None
            self._socket_state=SOCKET_ALIVE
        self._sock=socket
        self._send=socket.send
        self._recv=socket.recv
        self._registered=0
        self.trusted=0

        self.Dispatcher=server.Dispatcher
        self.DBG_LINE='session'
        self.DEBUG=server.Dispatcher.DEBUG
        self._expected={}
        self._owner=server
        if self.TYP=='server': self.ID=`random.random()`[2:]
        else: self.ID=None

        self.sendbuffer=''
        self._stream_pos_queued=None
        self._stream_pos_sent=0
        self.deliver_key_queue=[]
        self.deliver_queue_map={}
        #self.stanza_queue=[]
	self.stanza_queue = StanzaQueue()
        self.pushlock = threading.Lock()
        self.enqueuelock = threading.Lock()

        self._session_state=SESSION_NOT_AUTHED
        self.waiting_features=[]
        for feature in [NS_TLS,NS_SASL,NS_BIND,NS_SESSION]:
            if feature in server.features: self.waiting_features.append(feature)
        self.features=[]
        self.feature_in_process=None
        self.slave_session=None
        self.StartStream()

    def StartStream(self):
        self._stream_state=STREAM__NOT_OPENED
        self.Stream=simplexml.NodeBuilder()
        self.Stream._dispatch_depth=2
        self.Stream.dispatch=self.dispatch
        self.Parse=self.Stream.Parse
        self.Stream.stream_footer_received=self._stream_close
        if self.TYP=='client':
            self.Stream.stream_header_received=self._catch_stream_id
            self._stream_open()
        else:
            self.Stream.stream_header_received=self._stream_open

    def receive(self):
        """Reads all pending incoming data. Raises IOError on disconnect."""
        try: received = self._recv(10240)
        except: received = ''

        if len(received): # length of 0 means disconnect
            self.DEBUG(`self._sock.fileno()`+' '+received,'got')
        else:
            self.DEBUG('Socket error while receiving data','error')
            self.set_socket_state(SOCKET_DEAD)
            raise IOError("Peer disconnected")
        return received

    def send(self,chunk):
        if isinstance(chunk,Node): chunk = str(chunk).encode('utf-8')
        elif type(chunk)==type(u''): chunk = chunk.encode('utf-8')
        self.enqueue(chunk)

    def enqueue(self,stanza):
        """ Takes Protocol instance as argument. """
	self.enqueuelock.acquire()
        if isinstance(stanza,Protocol):
            self.stanza_queue.append(stanza)
	    #print ">>>> Session" + str(self)+  ": append stanza"
        else: 
	    self.sendbuffer+=stanza
	    #print ">>>> Session" + str(self)+  ": sendbuffer"
        if self._socket_state>=SOCKET_ALIVE:
	    qp = self.push_queue()
	    #print ">>>> Session" + str(self)+  ": queue pushed: " + str(qp)
	self.enqueuelock.release()

    def push_queue(self,failreason=ERR_RECIPIENT_UNAVAILABLE):

        if self._stream_state>=STREAM__CLOSED or self._socket_state>=SOCKET_DEAD: # the stream failed. Return all stanzas that are still waiting for delivery.
	    #print "push_queue: STREAM CLOSED or SOCKET DEAD!!"
            self._owner.deactivatesession(self)
            self.trusted=1
            for key in self.deliver_key_queue:                            # Not sure. May be I
                self.dispatch(Error(self.deliver_queue_map[key],failreason))                                          # should simply re-dispatch it?
            for stanza in self.stanza_queue:                              # But such action can invoke
                self.dispatch(Error(stanza,failreason))                                          # Infinite loops in case of S2S connection...
            #self.deliver_queue_map,self.deliver_key_queue,self.stanza_queue={},[],[]
            self.deliver_queue_map,self.deliver_key_queue={},[]
	    self.stanza_queue.init()
            return
        elif self._session_state>=SESSION_AUTHED:       # FIXME!
	    #print "push_queue: Session is SESSION_AUTHED"
	    self.pushlock.acquire() #### LOCK_QUEUE
            for stanza in self.stanza_queue:
		#print ">>>>push_queue: PUSHING STANZA: " + str(stanza)
                txt=stanza.__str__().encode('utf-8')
                self.sendbuffer+=txt
                self._stream_pos_queued+=len(txt)       # should be re-evaluated for SSL connection.
                self.deliver_queue_map[self._stream_pos_queued]=stanza     # position of the stream when stanza will be successfully and fully sent
                self.deliver_key_queue.append(self._stream_pos_queued)
            #self.stanza_queue=[]
            self.stanza_queue.init()
            self.pushlock.release()#### UNLOCK_QUEUE

        #if self.sendbuffer and select.select([],[self._sock],[])[1]:  # Gus
        if self.sendbuffer:
	    #print "push_queue: sendbuffer has DATA"
            try:
		#print "pushlock.acquire"
                self.pushlock.acquire()# LOCK_QUEUE
                sent=self._send(self.sendbuffer)
            except:
                self.set_socket_state(SOCKET_DEAD)
                self.DEBUG("Socket error while sending data",'error')
                self.pushlock.release()# UNLOCK_QUEUE
                return self.terminate_stream()
            self.DEBUG(`self._sock.fileno()`+' '+self.sendbuffer[:sent],'sent')
            self._stream_pos_sent+=sent
            self.sendbuffer=self.sendbuffer[sent:]
            self._stream_pos_delivered=self._stream_pos_sent            # Should be acquired from socket somehow. Take SSL into account.
            while self.deliver_key_queue and self._stream_pos_delivered>self.deliver_key_queue[0]:
                del self.deliver_queue_map[self.deliver_key_queue[0]]
                self.deliver_key_queue.remove(self.deliver_key_queue[0])
            self.pushlock.release()# UNLOCK_QUEUE

    def dispatch(self,stanza):
        if self._stream_state==STREAM__OPENED:                  # if the server really should reject all stanzas after he is closed stream (himeself)?
            self.DEBUG(stanza.__str__(),'dispatch')
            return self.Dispatcher.dispatch(stanza,self)

    def fileno(self): return self._sock.fileno()

    def _catch_stream_id(self,ns=None,tag='stream',attrs={}):
        if not attrs.has_key('id') or not attrs['id']:
            return self.terminate_stream(STREAM_INVALID_XML)
        self.ID=attrs['id']
        if not attrs.has_key('version'): self._owner.Dialback(self)

    def _stream_open(self,ns=None,tag='stream',attrs={}):
        text='<?xml version="1.0" encoding="utf-8"?>\n<stream:stream'
        if self.TYP=='client':
            text+=' to="%s"'%self.peer
        else:
            text+=' id="%s"'%self.ID
            if not attrs.has_key('to'): text+=' from="%s"'%self._owner.servernames[0]
            else: text+=' from="%s"'%attrs['to']
        if attrs.has_key('xml:lang'): text+=' xml:lang="%s"'%attrs['xml:lang']
        if self.xmlns: xmlns=self.xmlns
        else: xmlns=NS_SERVER
        text+=' xmlns:db="%s" xmlns:stream="%s" xmlns="%s"'%(NS_DIALBACK,NS_STREAMS,xmlns)
        if attrs.has_key('version') or self.TYP=='client': text+=' version="1.0"'
        self.send(text+'>')
        self.set_stream_state(STREAM__OPENED)
        if self.TYP=='client': return
        if tag<>'stream': return self.terminate_stream(STREAM_INVALID_XML)
        if ns<>NS_STREAMS: return self.terminate_stream(STREAM_INVALID_NAMESPACE)
        if self.Stream.xmlns<>self.xmlns: return self.terminate_stream(STREAM_BAD_NAMESPACE_PREFIX)
        if not attrs.has_key('to'): return self.terminate_stream(STREAM_IMPROPER_ADDRESSING)
        if attrs['to'] not in self._owner.servernames: return self.terminate_stream(STREAM_HOST_UNKNOWN)
        self.ourname=attrs['to'].lower()
        if self.TYP=='server' and attrs.has_key('version'): self.send_features()

    def send_features(self):
        features=Node('stream:features')
        if NS_TLS in self.waiting_features:
            features.T.starttls.setNamespace(NS_TLS)
            features.T.starttls.T.required
        if NS_SASL in self.waiting_features:
            features.T.mechanisms.setNamespace(NS_SASL)
            for mec in self._owner.SASL.mechanisms:
                features.T.mechanisms.NT.mechanism=mec
        else:
            if NS_BIND in self.waiting_features: features.T.bind.setNamespace(NS_BIND)
            if NS_SESSION in self.waiting_features: features.T.session.setNamespace(NS_SESSION)
        self.send(features)

    def feature(self,feature):
        if feature not in self.features: self.features.append(feature)
        self.unfeature(feature)

    def unfeature(self,feature):
        if feature in self.waiting_features: self.waiting_features.remove(feature)

    def _stream_close(self,unregister=1):
        if self._stream_state>=STREAM__CLOSED: return
        self.set_stream_state(STREAM__CLOSING)
        self.send('</stream:stream>')
        self.set_stream_state(STREAM__CLOSED)
        self.push_queue()       # decompose queue really since STREAM__CLOSED
        if unregister:
		self._owner.session_locator_lock.acquire()
		if self.fileno() in self._owner.session_locator.keys():
			t = self._owner.session_locator[self.fileno()]
			t.unregistersession(self)
			del self._owner.session_locator[self.fileno()]
			print "### Before closing session"
		else:
			self._owner.unregistersession(self)
		self._owner.session_locator_lock.release()
	print "### Stream close: session " + str(self)
        self._destroy_socket()

    def terminate_stream(self,error=None,unregister=1):
        if self._stream_state>=STREAM__CLOSING: return
        if self._stream_state<STREAM__OPENED:
            self.set_stream_state(STREAM__CLOSING)
            self._stream_open()
        else:
            self.set_stream_state(STREAM__CLOSING)
            p=Presence(typ='unavailable')
            p.setNamespace(NS_CLIENT)
            self.Dispatcher.dispatch(p,self)
        if error:
            if isinstance(error,Node): self.send(error)
            else: self.send(ErrorNode(error))
        self._stream_close(unregister=unregister)
        if self.slave_session:
            self.slave_session.terminate_stream(STREAM_REMOTE_CONNECTION_FAILED)

    def _destroy_socket(self):
        """ breaking cyclic dependancy to let python's GC free memory just now """
        self.Stream.dispatch=None
        self.Stream.stream_footer_received=None
        self.Stream.stream_header_received=None
        self.Stream.destroy()
        self._sock.close()
        self.set_socket_state(SOCKET_DEAD)

    def start_feature(self,f):
        if self.feature_in_process: raise "Starting feature %s over %s !"%(f,self.feature_in_process)
        self.feature_in_process=f
    def stop_feature(self,f):
        if self.feature_in_process<>f: raise "Stopping feature %s instead of %s !"%(f,self.feature_in_process)
        self.feature_in_process=None
    def set_socket_state(self,newstate):
        if self._socket_state<newstate: self._socket_state=newstate
    def set_session_state(self,newstate):
        if self._session_state<newstate:
            if self._session_state<SESSION_AUTHED and \
               newstate>=SESSION_AUTHED: self._stream_pos_queued=self._stream_pos_sent
            self._session_state=newstate
            if newstate==SESSION_OPENED:
		self.enqueue(Message(self.peer,Revision,frm=self.ourname))     # Remove in prod. quality server
		self.DEBUG(str('Sent Welcome message to peer '+str(self.peer)))
	else:
		print "sss: Mi estado es " + str(self._session_state) + " y me pasan " + str(newstate)

    def set_stream_state(self,newstate):
        if self._stream_state<newstate: self._stream_state=newstate


class Socket_Process(threading.Thread):

	def __init__(self):
		#self.__owner = owner
        	self.__sockpoll=select.poll()
		self.sockets = {}
        	self.SESS_LOCK=thread.allocate_lock()
		threading.Thread.__init__(self)
		
		self.isAlive = True

		self.setDaemon(True)

	def registersession(self, sess):
	        self.SESS_LOCK.acquire()
	        if isinstance(sess,Session):
	            if sess._registered:
	                self.SESS_LOCK.release()
	                #if self._DEBUG.active: raise "Twice session Registration!"
	                return
	                #else: return
	            sess._registered=1
	            self.sockets[sess.fileno()]=sess
	            self.__sockpoll.register(sess,select.POLLIN | select.POLLPRI | select.POLLERR | select.POLLHUP)
 	            self.DEBUG('SocketProcess','succesfully registered %s (%s) at SocketProcess %s'%(sess.fileno(),sess,self))
	            self.SESS_LOCK.release()

	def unregistersession(self, sess):
		#self.SESS_LOCK.acquire()
		if isinstance(sess,Session):
			if not sess._registered:
				#self.SESS_LOCK.release()
				#if self._DEBUG.active: raise "Twice session UNregistration!"
				return
				#else: return
			sess._registered=0
			try:
				self.__sockpoll.unregister(sess)
				del self.sockets[sess.fileno()]
				print "### SocketProcess UNregister session " + str(sess)
			except:
				# Session wasn't here
				pass
			#self.DEBUG('server','UNregistered %s (%s)'%(self.session.fileno(),self.session))
			#self.SESS_LOCK.release()
			#self.isAlive = False



	def run(self):
		while self.isAlive:
			try:
				# We MUST put a timeout here, believe me
				for fileno,ev in self.__sockpoll.poll(100):
		    		
				    try:
					sess=self.sockets[fileno]
				    except:
					sess = None

				    if isinstance(sess,Session):
					try:
					    data=sess.receive()
					except IOError: # client closed the connection
					    print "### IOError"
					    sess.terminate_stream()
					    self.__sockpoll.unregister(sess)
					    del self.sockets[fileno]
					    data=''
					if data:
						try:
							sess.Parse(data)
						except simplexml.xml.parsers.expat.ExpatError:
							sess.terminate_stream(STREAM_XML_NOT_WELL_FORMED)
							self.__sockpoll.unregister(sess)
							del self.sockets[fileno]
							#self.isAlive=False
			except:
				self.isAlive=False
				#self.setDaemon(False)
		    

		        #print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>leyendo " + str(self)
			#t = self.__owner.data_queue.get()
		        #print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>leido " + str(self)
			#sess=t[0]
			#data = t[1]
			#try:
                        # 	sess.Parse(data)
			#except simplexml.xml.parsers.expat.ExpatError:
			#	sess.terminate_stream(STREAM_XML_NOT_WELL_FORMED)

class Server:

    def DEBUG_ts(self, orig, msg, type=''):
	self.debug_mutex.acquire()
	self._DEBUG.Show(orig, msg, type)
	self.debug_mutex.release()
	

    def __init__(self,debug=[],cfgfile=None, max_threads=100):
	self.alive = True

	self.debug_mutex = threading.Lock()

        self.sockets={}
        self.sockpoll=select.poll()
        self.ID=`random.random()`[2:]

	self.data_queue = Queue()

        # if debug == None:
	#	self._DEBUG = Debug.NoDebug()
	#else:
	self._DEBUG=Debug.Debug(debug)
        self.DEBUG=self._DEBUG.Show
        #self.DEBUG=self.DEBUG_ts
        self.debug_flags=self._DEBUG.debug_flags
        self.debug_flags.append('session')
        self.debug_flags.append('dispatcher')
        self.debug_flags.append('server')

	self.thread_pull = []
	self.max_threads = max_threads

	# Key: session fileno , Value = Socket_Process managing the session
	self.session_locator = {}
	self.session_locator_lock = threading.Lock()  # Lock for protecting session_locator

	for i in range(0, self.max_threads):
		t = Socket_Process()
		t.start()
		self.thread_pull.append(t)
	self.DEBUG('server', 'Created succesfully '+str(i+1)+' Socket Process Threads', 'ok')

	if cfgfile == None:
		self.cfgfile = '.' + os.sep + 'xmppd.xml'
	else:
		self.cfgfile = cfgfile
	if not os.path.exists(self.cfgfile):
		self.DEBUG('server','Could not load configuration file for xmppd. Bye', 'error')
		self.shutdown(STREAM_SYSTEM_SHUTDOWN)
		sys.exit(1)

        self.SESS_LOCK=thread.allocate_lock()
        self.Dispatcher=dispatcher.Dispatcher()
        self.Dispatcher._owner=self
	self.defaultNamespace = NS_CLIENT
        self.Dispatcher._init()

	self.router_filters = list()
	#this is for test
	from filters import *
	self.router_filter_names = [acc.ACC,component.Component,console.Console,mucfilter.MUCFilter]

        self.features=[]
        #import modules
        for addon in addons:
            if issubclass(addon,PlugIn): addon().PlugIn(self)
            else: self.__dict__[addon.__class__.__name__]=addon()
            self.feature(addon.NS)
        self.routes={}
	self.routes_lock = threading.Lock()

        for port in [5222,5223,5269,9000,9001,9002]:
            sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', port))
            sock.listen(1)
            self.registersession(sock)


    def feature(self,feature):
        if feature and feature not in self.features: self.features.append(feature)

    def registersession(self,s):
        self.SESS_LOCK.acquire()
        if isinstance(s,Session):
            if s._registered:
                self.SESS_LOCK.release()
                if self._DEBUG.active: raise "Twice session Registration!"
                else: return
            s._registered=1
        self.sockets[s.fileno()]=s
        self.sockpoll.register(s,select.POLLIN | select.POLLPRI | select.POLLERR | select.POLLHUP)
        self.DEBUG('server','registered %s (%s)'%(s.fileno(),s))
        self.SESS_LOCK.release()

    def unregistersession(self,s):
        self.SESS_LOCK.acquire()
        if isinstance(s,Session):
            if not s._registered:
                self.SESS_LOCK.release()
                if self._DEBUG.active: raise "Twice session UNregistration!"
                else: return
            s._registered=0
        self.sockpoll.unregister(s)
        del self.sockets[s.fileno()]
        self.DEBUG('server','UNregistered %s (%s)'%(s.fileno(),s))
        self.SESS_LOCK.release()

    def activatesession(self,s,peer=None):
        if not peer: peer=s.peer
        alt_s=self.getsession(peer)
        if s==alt_s: return
        elif alt_s: self.deactivatesession(peer)
	self.routes_lock.acquire()
        self.routes[peer]=s
	self.routes_lock.release()
	self.DEBUG('session', 'Activating session %s with peer %s' % (str(s),str(peer)))

    def getsession(self, jid):
        try:
		self.routes_lock.acquire()
		s = self.routes[jid]
		self.routes_lock.release()
		return s
        except KeyError:
		self.routes_lock.release()
		pass

    def deactivatesession(self, peer):
        s=self.getsession(peer)
	self.routes_lock.acquire()	
        if self.routes.has_key(peer):
		del self.routes[peer]
	self.routes_lock.release()
        return s

    def getSocketProcess(self):
	return random.choice(self.thread_pull)

    def handle(self):
        for fileno,ev in self.sockpoll.poll(1000):
	    
            sock=self.sockets[fileno]

            if isinstance(sock,socket.socket):
                conn, addr = sock.accept()
                host,port=sock.getsockname()
                if port in [5222,5223]: sess=Session(conn,self,NS_CLIENT)
		elif port in [9000,9001,9002]: sess=Session(conn, self, NS_COMPONENT_ACCEPT)  # It is a component
                else: sess=Session(conn,self,NS_SERVER)

		'''
		1. Select a 't' from a pool of 'Socket_Process's
		    t = self.getSocketProcess()
		2.  t.registersession(sess)
		3. Add 't' to the session_locator dictionary, indexed by its session's fileno
		    self.session_locator[sess.fileno()] = t
		'''

		#t = Socket_Process(sess)
		t = self.getSocketProcess()
		t.registersession(sess)
 	        self.DEBUG('server','registered %s (%s)'%(sess.fileno(),sess))
		self.session_locator_lock.acquire()
		self.session_locator[sess.fileno()] = t
		self.session_locator_lock.release()
 	        self.DEBUG('server','session %s assigned to SocketProcess %s'%(sess, t))

                #self.registersession(sess)
                if port==5223: self.TLS.startservertls(sess)
            else: raise "Unknown instance type: %s"%sock
	    

    def run(self):
	self.DEBUG('server', "SERVER ON THE RUN", 'info')

	#for i in range(0,self.max_threads):
	#	th = Socket_Process(self)
	#	th.start()
	#	self.thread_pull.append(th)

        while self.alive: 
        	try:
			#active_th = []
			#for th in self.thread_pull:
			#	if th.isAlive:
			#		active_th.append(th)
			#print "### thread_pull: " + str(active_th)
			self.handle()
		        #except KeyboardInterrupt:
		except Exception, e:
			print "### UNKNOWN EXCEPTION: " + str(e)
			self.DEBUG('server','Shutting down on user\'s behalf', prefix='info')
			#print "Server: Shuting down ..."
       	    		self.shutdown(STREAM_SYSTEM_SHUTDOWN)
	     		#except: self.shutdown(STREAM_INTERNAL_SERVER_ERROR); raise
			break

    def shutdown(self,reason):

	self.DEBUG('server', 'Deregistering sessions ...', 'info')
	for th in self.thread_pull:
		for sess in th.sockets.values():
			th.unregistersession(sess)
			sess.terminate_stream(reason)
		th.isAlive = False  # Kill the thread
	self.DEBUG('server', 'Sessions deregistered...', 'info')


        socklist=self.sockets.keys()
        for fileno in socklist:
            s=self.sockets[fileno]
            if isinstance(s,socket.socket):
                self.unregistersession(s)
                s.shutdown(2)
                s.close()
            elif isinstance(s,Session): s.terminate_stream(reason)

	self.alive = False

    def S2S(self,ourname,domain,slave_session=None):
        s=Session(socket.socket(socket.AF_INET, socket.SOCK_STREAM),self,NS_SERVER,domain)
        s.slave_session=slave_session
        s.ourname=ourname
        self.activatesession(s)
        thread.start_new_thread(self._connect_session,(s,domain))
        return s

    def _connect_session(self,session,domain):
        try: session._sock.connect((domain,5269))
        except socket.error,err:
            session.set_session_state(SESSION_BOUND)
            session.set_socket_state(SOCKET_DEAD)
            if err[0]==errno.ETIMEDOUT: failreason=ERR_REMOTE_SERVER_TIMEOUT
            elif err[0]==socket.EAI_NONAME: failreason=ERR_REMOTE_SERVER_NOT_FOUND
            else: failreason=ERR_UNDEFINED_CONDITION
            session.push_queue(failreason)
            session.terminate_stream(STREAM_REMOTE_CONNECTION_FAILED,unregister=0)
            return
        session.set_socket_state(SOCKET_ALIVE)
        session.push_queue()
	t = self.getSocketProcess()
        t.registersession(session)

    def Privacy(self,peer,stanza): pass
    def Dialback(self,session):
        session.terminate_stream(STREAM_UNSUPPORTED_VERSION)

def start_new_thread_fake(func,args):
    func(*args)

def testrun():
    thread.start_new_thread=start_new_thread_fake
    import modules
    modules.stream.thread.start_new_thread=start_new_thread_fake
    return Server()

def print_help():
    print "xmppd Jabber Server Help"
    print "========================\n\n"
    print "Usage: xmppd.py -c configfile\n\n"

if __name__=='__main__':
    #print "Firing up PsyCo"
    #import psyco
    #psyco.log()
    #psyco.full()
   
    cfgfile = None 
    debug = []
    for opt, arg in getopt(sys.argv[1:], "hvdc:", ["help", "configfile="])[0]:
	    if opt in ["-h", "--help"]:
		print_help()
		sys.exit(0)
	    elif opt in ["-v", "--version"]:
		print Revision + "\n"
		sys.exit(0)
	    elif opt in ["-c", "--configfile"]: cfgfile=arg
	    elif opt in ["-d", "--debug"]: debug=['always']

    if cfgfile:
	    s=Server(cfgfile=cfgfile, debug=debug)
	    s.run()
    else:
	    s=Server(debug=debug)
	    s.run()

