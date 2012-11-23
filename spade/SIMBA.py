# -*- coding: utf-8 -*-
import xmpp
import threading
import Agent
import Envelope
import FIPAMessage
import AID
import Behaviour
import ACLParser
import socket
import SocketServer

SIMBAPORT = 20001


class SIMBA(Agent.PlatformAgent):
    class OutboxBehaviour(Behaviour.Behaviour):
        '''
        Behaviour that routes outgoing SIMBA messages
        '''

        def __init__(self):
            Behaviour.Behaviour.__init__(self)

        def sendToSimba(self, msg, to):
            '''Sends a message to a SIMBA receiver'''

            # Socket work
            ip = to.strip("simba://")
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.connect((ip, SIMBAPORT))
            except:
                print "Could not connect to SIMBA socket on " + str(ip)
            s.send(str(msg))
            s.close()

        def _process(self):
            msg = self._receive(True)
            if (msg is not None):
                to_list = msg.getReceivers()
                d = {}
                for to in to_list:
                    self.sendToSimba(msg, to)
            else:
                print "SIMBA::dying... it shouldn't happen"

    class InboxBehaviour(Behaviour.Behaviour):
        '''
        Behaviour that routes incoming SIMBA messages
        '''

        class SimbaRequestHandler(SocketServer.DatagramRequestHandler):
            '''
            Request handler for SIMBA messages
            '''
            def handle(self):
                print "SIMBA SS: New incoming message"

        def onStart(self):
            self.SS = SocketServer.ThreadingUDPServer(("", SIMBAPORT), SimbaRequestHandler)
            print "SIMBA SS listening on port ", SIMBAPORT
            self.SS.serve_forever()

    def __init__(self, node, password, server, port):
        Agent.PlatformAgent.__init__(self, node, password, server, port, debug=[])

    def _setup(self):
        self.addBehaviour(self.InboxBehaviour(), None)
        self.setDefaultBehaviour(self.OutboxBehaviour())
