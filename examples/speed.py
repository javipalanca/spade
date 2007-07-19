#!/usr/bin/env python
# encoding: utf-8

import sys
import os
sys.path.append('..'+os.sep+'trunk')
sys.path.append('..')

from spade import *
from spade.ACLMessage import *
from string import *
from time import sleep
from xmpp import *
import cPickle as pickle

repeats = 10000

print "Jabber message test . . ."
msg = ACLMessage()
msg.setPerformative("request")
msg.setSender(AID.aid("speed@platform.com", ["xmpp://speed@platform.com"]))
msg.addReceiver(AID.aid("receiver@platform.com", ["xmpp://receiver@platform.com"]))
msg.setContent("Arbitrary Message Content. One Ring to rule them all. One ring to find them. One ring to bring them all and in the darkness bind them")

t0 = time.time()
for i in range(repeats):
	jabber_msg = protocol.Message("receiver@platform.com", xmlns="")
	jabber_msg.attrs.update(msg._attrs)
	jabber_msg["from"]=msg.getSender().getName()
	s = str(jabber_msg)
	# Send . . .
	n = simplexml.XML2Node(s)
	mess = Message(node=n)
	ACLmsg = ACLMessage()
        ACLmsg._attrs.update(mess.attrs)
	ACLmsg.setContent(mess.getBody())
	ACLmsg.setSender(AID.aid(str(mess.getFrom()), ["xmpp://"+str(mess.getFrom())]))
        ACLmsg.addReceiver(AID.aid(str(mess.getTo()), ["xmpp://"+str(mess.getTo())]))
t1 = time.time() - t0
print "Time:",str(t1)
print "Size:",str(len(s))

print "cPickle test . . ."
t2 = time.time()
for i in range(repeats):
	data = pickle.dumps(msg)
	# Send . . .
	newpick = pickle.loads(data)
t3 = time.time() - t2
print "Time:", str(t3)
print "Size:",str(len(data))

