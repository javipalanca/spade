#!/usr/bin/python
# -*- coding: koi8-r -*-
from xmpp import *

def PresenceHandler(conn,presence_node):
    """ Handler for playing a sound when particular contact became online """
    targetJID='node@domain.org'
    if presence_node.getFrom().bareMatch(targetJID):
        # play a sound
        pass
def iqHandler(conn,iq_node):
    """ Handler for processing some "get" query from custom namespace"""
    reply=Iq('result',iq_node.getNS(),to=iq_node.getFrom())
    # ... put some content into reply node
    conn.send(reply)
    raise NodeProcessed  # This stanza is fully processed
def messageHandler(conn,mess_node): pass

if 1:
    """
        Example 1:
        Connecting to specified IP address.
        Connecting to port 5223 - TLS is pre-started.
        Using direct connect.
    """
    # Born a client
    cl=Client('ejabberd.somedomain.org')
    # ...connect it to SSL port directly
    if not cl.connect(server=('1.2.3.4',5223)):
        raise IOError('Can not connect to server.')
else:
    """
        Example 2:
        Connecting to server via proxy.
        Assuming that servername resolves to jabber server IP.
        TLS will be started automatically if available.
    """
    # Born a client
    cl=Client('jabberd2.somedomain.org')
    # ...connect via proxy
    if not cl.connect(proxy={'host':'someproxy.somedomain.org','port':'8080','user':'proxyuser','password':'proxyuserpassword'}):
        raise IOError('Can not connect to server.')
# ...authorize client
if not cl.auth('jabberuser','jabberuserpassword','optional resource name'):
    raise IOError('Can not auth with server.')
# ...register some handlers (if you will register them before auth they will be thrown away)
cl.RegisterHandler('presence',presenceHandler)
cl.RegisterHandler('iq',iqHandler)
cl.RegisterHandler('message',messageHandler)
# ...become available
cl.sendInitPresence()
# ...work some time
cl.Process(1)
# ...if connection is brocken - restore it
if not cl.isConnected(): cl.reconnectAndReauth()
# ...send an ASCII message
cl.send(Message('test@jabber.org','Test message'))
# ...send a national message
cl.send(Message('test@jabber.org',unicode('Проверка связи','koi8-r')))
# ...send another national message
simplexml.ENCODING='koi8-r'
cl.send(Message('test@jabber.org','Проверка связи 2'))
# ...work some more time - collect replies
cl.Process(1)
# ...and then disconnect.
cl.disconnect()

"""
If you have used jabberpy before you will find xmpppy very similar.
Though read of xmpppy sources highly recommended.
At least read the client.py code - you will see what params it can take
and simplexml code - you will see the main differences in XML handling.
"""
