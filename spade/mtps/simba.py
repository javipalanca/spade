# -*- coding: utf-8 -*-

from spade import MTP
from spade import AID
from spade import ACLParser
from spade import Envelope

import socket
import SocketServer
import xmpp

import thread


class SimbaRequestHandler(SocketServer.DatagramRequestHandler):
    '''
    Request handler for SIMBA messages
    '''
    def handle(self):
        msg = str(self.request[0])
        #print "SIMBA SS: New incoming message: " + msg
        acl = self.server.parser.parse(msg)
        envelope = Envelope.Envelope(_from=acl.getSender(), to=acl.getReceivers(), aclRepresentation="fipa.acl.rep.string.std")
        self.server.dispatch(envelope, msg)
        #print "SIMBA SS: Message dispatched"


class simba(MTP.MTP):

    def receiveThread(self):
        SocketServer.ThreadingUDPServer.allow_reuse_address = True
        self.SS = SocketServer.ThreadingUDPServer(("", self.port), SimbaRequestHandler)
        self.SS.dispatch = self.dispatch
        self.SS.parser = ACLParser.ACLParser()
        #print "SIMBA SS listening on port " + str(self.port)
        self.SS.serve_forever()

    def stop(self):
        try:
            del self.SS
        except Exception, e:
            pass
            print "EXCEPTION IN SIMBA", str(e)

    def setup(self):
        '''
        Secondary constructor
        '''
        #self.address = self.config.acc[self.name].address
        #self.port = self.config.acc[self.name].port
        self.port = 2001

        # Launch receive thread
        tid = thread.start_new_thread(self.receiveThread, ())

    def send(self, envelope, payload, to=None):
        '''
        Send a message to a SIMBA agent
        '''
        payload = str(payload.getPayload()[0])
        try:
            p = ACLParser.ACLxmlParser()
            aclmsg = p.parse(payload)
        except:
            print ">>>SIMBA: COULD NOT BUILD ACL"
            pass

        if to is None:
            to = envelope.getTo()

        for receiver in to:
            for ad in receiver.getAddresses():
                ad = str(ad)  # Type change
                # SIMBA URI = simba://address:port
                if ad[0:8] == "simba://":
                    ad = ad[8:]
                    # Check for the presence of a port
                    if ':' in ad:
                        ip, port = ad.split(':')
                    else:
                        ip = ad
                        port = 2001

                    # Set up a SIMBA socket to send the message
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    try:
                        s.connect((ip, port))
                        # FORCE ACL WITH PARENTHESIS
                        s.send(str(aclmsg))  # ACL with parenthesis, oh no!
                        s.close()
                    except:
                        print "Could not send SIMBA message"

# Required
PROTOCOL = "simba"
INSTANCE = simba
#port = "2001"
