# -*- coding: utf-8 -*-
import Behaviour
import xmlrpclib
import xmpp
from xmpp.protocol import NS_RPC
from xmpp import Iq

import types

class RPC(object):

    def __init__(self, agent):  # , msgrecv):
        self._client = agent.getAID().getName()
        #self.msgrecv = msgrecv
        self.myAgent = agent
        self._server = agent.server
        agent.addBehaviour(RPCServerBehaviour(), Behaviour.MessageTemplate(Iq(typ='set', queryNS=NS_RPC)))

    def register(self):
        self.myAgent.jabber.RegisterHandler('iq', self.myAgent._jabber_messageCB,'set', NS_RPC)
        self.myAgent.jabber.RegisterHandler('iq', self.myAgent._jabber_messageCB,'get', NS_RPC)
        self.myAgent.jabber.RegisterHandler('iq', self.myAgent._jabber_messageCB,'result', NS_RPC)
        self.myAgent.jabber.RegisterHandler('iq', self.myAgent._jabber_messageCB,'error', NS_RPC)

class RPCServerBehaviour(Behaviour.EventBehaviour):

    def _process(self):
        self.result = None
        self.msg = self._receive(False)
        if self.msg is not None:
            if self.msg.getType() == "set":

                self.myAgent.DEBUG("RPC request received: " + str(self.msg), 'info', "rpc")

                mc = self.msg.getTag('query')
                params, name = xmlrpclib.loads("<?xml version='1.0'?>%s" % str(mc))
                name = name.lower()
                self.myAgent.DEBUG("Params processed: name=" + name + " params=" + str(params) + " in " + str(self.myAgent.RPC.keys()), "info", "rpc")

                if name not in self.myAgent.RPC:
                    self.myAgent.DEBUG("RPC: 404 method not found", 'error', "rpc")
                    xmlrpc_res = xmlrpclib.dumps(xmlrpclib.Fault(404, "method not found"))
                    reply = self.msg.buildReply("error")
                    reply.setQueryPayload([xmpp.simplexml.XML2Node(xmlrpc_res)])
                    reply.setType("result")
                    reply.setFrom(self.myAgent.JID)
                    self.myAgent.send(reply)
                    return

                service, methodCall = self.myAgent.RPC[name]

                self.myAgent.DEBUG("service and method: " + str(service) + " --> " + str(methodCall), "info", "rpc")

                self.myAgent.DEBUG("Comparing service.getInputs(): " + str(service.getInputs()) + " with params--> " + str(params), "info", "rpc")
                ps = params[0].keys()
                for p in eval(str(service.getInputs())):  # service.getP():
                    self.myAgent.DEBUG("Comparing input " + str(p) + " with " + str(ps))
                    if str(p) not in ps:
                        self.myAgent.DEBUG("RPC: 500 missing input: " + str(p) + " is not in " + str(params), 'error', "rpc")
                        xmlrpc_res = xmlrpclib.dumps(xmlrpclib.Fault(500, "missing input"))
                        reply = self.msg.buildReply("error")
                        reply.setQueryPayload([xmpp.simplexml.XML2Node(xmlrpc_res)])
                        reply.setType("result")
                        reply.setFrom(self.myAgent.JID)
                        self.myAgent.send(reply)
                        return

                try:
                    self.myAgent.DEBUG("Calling method " + str(methodCall) + " with params " + str(params), "info", "rpc")
                    if params == (None,):
                        result = methodCall()
                    else:
                        args = ""
                        for k, v in params[0].items():
                            args += str(k) + "=" + str(v) + ","
                        args = args[:-1]
                        result = eval("methodCall(" + args + ")")
                except Exception, e:
                    self.myAgent.DEBUG("RPC: 500 method error: " + str(e), 'error', "rpc")
                    xmlrpc_res = xmlrpclib.dumps(xmlrpclib.Fault(500, "method error: " + str(e)))
                    reply = self.msg.buildReply("error")
                    reply.setQueryPayload([xmpp.simplexml.XML2Node(xmlrpc_res)])
                    reply.setType("result")
                    reply.setFrom(self.myAgent.JID)
                    self.myAgent.send(reply)
                    return

                #Check outputs
                try:
                    fail = False
                    outputs = {}
                    if isinstance(result, types.DictType):
                        for q in eval(str(service.getOutputs())):  # service.getQ():
                            if q not in result.keys():
                                fail = True
                                break
                            else:
                                outputs[q] = result[q]
                        params = (outputs,)
                    else:
                        self.myAgent.DEBUG("RPC method MUST return a dict.", 'error', "rpc")
                        fail = True
                except:
                    fail = True
                if fail:
                    self.myAgent.DEBUG("RPC: 500 missing output: " + str(service.getQ()), 'error', "rpc")
                    xmlrpc_res = xmlrpclib.dumps(xmlrpclib.Fault(500, "missing output"))
                    reply = self.msg.buildReply("error")
                    reply.setQueryPayload([xmpp.simplexml.XML2Node(xmlrpc_res)])
                    reply.setType("result")
                    reply.setFrom(self.myAgent.JID)
                    self.myAgent.send(reply)
                    return

                #Everything was ok. Return results
                xmlrpc_res = xmlrpclib.dumps(params, methodresponse=True, allow_none=True)
                reply = self.msg.buildReply("result")
                reply.setQueryPayload([xmpp.simplexml.XML2Node(xmlrpc_res)])
                self.myAgent.send(reply)
                self.myAgent.DEBUG("RPC: method succesfully served: " + str(reply), 'ok', "rpc")

        else:
            self.myAgent.DEBUG("RPCServerBehaviour returned with no message", "warn", "rpc")


class RPCClientBehaviour(Behaviour.OneShotBehaviour):

    def __init__(self, service, inputs, num):
        '''
        This behaviour makes the Remote Procedure Call to the server
        Usage:
        service - DF.Service to be called
        inputs  - dictionary of inputs where key=input name, value=input value
        num     - a numeric id
        '''
        Behaviour.OneShotBehaviour.__init__(self)
        self.service = service
        self.inputs = inputs
        self.num = num

    def _process(self):
        self.result = None

        #send IQ methodCall
        params = self.inputs
        ps = None
        ps = self.service.getP()  # self.service.getDAD().getServices()[0].getProperty("P")
        for p in ps:  # check all Preconditions are True
            #if not p in self.inputs.keys():
            if not self.myAgent.askBelieve(p):
                self.myAgent.DEBUG("Precondition " + str(p) + " is not satisfied. Can't call method " + self.service.getName(), 'error', "rpc")
                self.result = False
                return
            #else: params[p] = self.inputs[p]

        #params = tuple(ps)
        self.myAgent.DEBUG("Params processed: " + str(params), "info", "rpc")

        #if agent is a BDIAgent check preconditions
        #if "askBelieve" in dir(self.myAgent):
        #    for p in params:
        #        if not self.myAgent.askBelieve(p):
        #            self.result=False
        #            self.myAgent.DEBUG("Precondition "+ str(p) + " is not satisfied. Can't call method "+self.service.getName(),'error',"rpc")
        #            return

        payload = xmlrpclib.dumps((params,), methodname=self.service.getName(), allow_none=True)
        self.myAgent.DEBUG("Marshalled " + payload, "info", "rpc")
        payload_node = xmpp.simplexml.XML2Node(payload)
        to = xmpp.protocol.JID(self.service.getOwner().getName())
        iq = xmpp.protocol.Iq(typ='set', queryNS="jabber:iq:rpc", frm=self.myAgent.JID, to=to, attrs={'id': self.num})
        iq.setQueryPayload([payload_node])
        self.myAgent.DEBUG("Calling method with: " + str(iq), "info", "rpc")
        self.myAgent.send(iq)
        self.myAgent.DEBUG(self.service.getName() + " method called. Waiting for response", 'ok', "rpc")

        #receive IQ methodResponse
        self.msg = self._receive(True)
        if self.msg is not None:
            self.myAgent.DEBUG("Response received for method " + self.service.getName() + ":" + str(self.msg), 'ok', "rpc")
            if self.msg.getType() == "result":
                try:
                    params, method = xmlrpclib.loads("<?xml version='1.0'?>%s" % self.msg)
                    self.DEBUG("Returned params " + str(params), 'ok', "rpc")
                    self.result = params[0]
                    #if agent is a BDIAgent add result params as postconditions
                    for k, v in self.result.items():  # [0]:
                            self.myAgent.kb.set(k, v)
                    for q in self.service.getQ():
                        if not self.myAgent.askBelieve(q):
                            raise Exception("PostCondition " + str(q) + " not satisfied.")
                    return self.result
                except Exception, e:
                    self.myAgent.DEBUG("Error executing RPC service: " + str(e), "error", "rpc")
                    self.result = False
                    return False
            else:
                self.result = False
                return False
        else:
            self.result = False
            return False
