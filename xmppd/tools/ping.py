#!/usr/bin/python
# -*- coding: utf-8 -*-
from xmpp import *
import time
import sha

message_pool = {}
our_resource = sha.new(str(time.time())).hexdigest()


def PresenceHandler(conn, presence_node):
    """ Handler for playing a sound when particular contact became online """
    targetJID = 'node@domain.org'
    if presence_node.getFrom().bareMatch(targetJID):
        # play a sound
        pass


def iqHandler(conn, iq_node):
    """ Handler for processing some "get" query from custom namespace"""
    reply = Iq('result', iq_node.getNS(), to=iq_node.getFrom())
    # ... put some content into reply node
    conn.send(reply)
    raise NodeProcessed  # This stanza is fully processed


def messageHandler(conn, mess_node):
    global message_pool
    the_body = mess_node.getBody()
    if the_body in message_pool:
        message_pool[the_body]['fin'] = time.time()
        message_pool[the_body]['returned'] = True
    else:
        print "Damn!"


"""
    Example 1:
    Connecting to specified IP address.
    Connecting to port 5223 - TLS is pre-started.
    Using direct connect.
"""
# Born a client
cl = Client('127.0.0.1', 5223, None)
# ...connect it to SSL port directly
if not cl.connect(server=('127.0.0.1', 5223)):
    raise IOError('Can not connect to server.')

# ...authorize client
if not cl.auth('test', 'test', our_resource):
    raise IOError('Can not auth with server.')
# ...register some handlers (if you will register them before auth they will be thrown away)
cl.RegisterHandler('presence', PresenceHandler)
#cl.RegisterHandler('iq',iqHandler)
cl.RegisterHandler('message', messageHandler)
# ...become available
cl.sendInitPresence()
# ...work some time
cl.Process(1)

if not cl.isConnected():
    cl.reconnectAndReauth()

interation_max = int(raw_input("How many times will we be grilling the server?\n"))
wait_time = 0.0001  # raw_input("For what interval?\n") * 1.0
i = 0


try:
    while i < interation_max:
        the_time = time.time()
        data = sha.new(str(the_time)).hexdigest()
        print len(data)
        message_pool.update({data: {'start': the_time, 'fin': 0.0, 'returned': False}})
        cl.send(Message('test@127.0.0.1', data))  # /%s'%our_resource,data))
        cl.Process(wait_time)
        i += 1

except KeyboardInterrupt:
    print "We're just waiting for 2 secs..."
    time.sleep(2)

avg_time_data = []
number_returned = 0
for x, y in message_pool.iteritems():
    if message_pool[x]['returned'] is True:
        avg_time_data += [message_pool[x]['fin'] - message_pool[x]['start']]
        number_returned += 1

avg_time = 0.0
for atime in avg_time_data:
    avg_time += atime
avg_time = avg_time / len(avg_time_data)
print "\n\n\nAverage round-trip: %f\n%i stanzas returned out of %i which is %f%%" % (avg_time, number_returned, len(message_pool.keys()), (number_returned / len(message_pool.keys()) * 1.0) * 100)
