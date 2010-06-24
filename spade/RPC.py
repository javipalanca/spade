import Behaviour
import xmlrpclib
import xmpp

class RPCServerBehaviour(Behaviour.EventBehaviour):

    def _process(self):
        self.result=None
        self.msg = self._receive(False)
        if self.msg != None:
            if self.msg.getType() == "set":

                mc = self.msg.getTag('query').getChild()
                params, method = xmlrpclib.loads("<?xml version='1.0'?>%s" % str(mc))
                    
                if not self.myAgent.RPC.has_key(name):
                    xmlrpc_res = xmlrpclib.dumps( xmlrpclib.Fault(404, "method not found"))
                    reply = self.msg.buildReply("error")
                    reply.getTag('query').addChild(node=xmlrpc_res)
                    self.myAgent.jabber.send(reply)
                    self.DEBUG("RPC: 404 method not found",'error')
                    return
                    
                service,methodCall = self.myAgent.RPC[name]
                for p in params:
                    if p not in service.getP():
                        xmlrpc_res = xmlrpclib.dumps( xmlrpclib.Fault(500, "missing precondition"))
                        reply = self.msg.buildReply("error")
                        reply.setQueryPayload(xmlrpc_res)
                        self.myAgent.jabber.send(reply)
                        self.DEBUG("RPC: 500 missing precondition",'error')
                        return

                try:
                    result = methodCall()
                    xmlrpc_res = xmlrpclib.dumps( tuple([result]) , methodresponse=True)
                    reply = self.msg.buildReply("result")
                    reply.setQueryPayload(xmlrpc_res)
                    self.myAgent.jabber.send(reply)
                    self.DEBUG("RPC: method succesfully served",'ok')
                except Exception,e:
                    xmlrpc_res = xmlrpclib.dumps( xmlrpclib.Fault(500, "method error: "+str(e)))
                    reply = self.msg.buildReply("error")
                    reply.setQueryPayload(xmlrpc_res)
                    self.myAgent.jabber.send(reply)
                    self.DEBUG("RPC: 500 method error: "+str(e),'error')
                    return
        
        else:
            self.myAgent.DEBUG("RPCServerBehaviour returned with no message", "warn")
            
class RPCClientBehaviour(Behaviour.OneShotBehaviour):
    
    def __init__(self, service):
        self.service = service

    def _process(self):
        self.result=None
        
        #send IQ methodCall
        to = xmpp.protocol.JID(self.service.getOwner().getName())
        iq = xmpp.protocol.Iq(typ='set',queryNS="jabber:iq:rpc",to=to)
                
        params = [service.getP()]
        
        #if agent is a BDIAgent check preconditions
        if "askBelieve" in dir(self.myAgent):
            for p in params:
                if not self.myAgent.askBelieve(p):
                    self.result=False
                    self.myAgent.DEBUG("Precondition "+ str(p) + " is not satisfied. Can't call method "+service.getName(),'error')
                    return
            
        payload = xmlrpclib.dumps( tuple(params) , methodname=service.getName())
        iq.setQueryPayload(payload)
        self.myAgent.jabber.send(iq)
        self.myAgent.DEBUG(service.getName() + " method called. Waiting for response",'ok')
        
        #receive IQ methodResponse
        self.msg = self._receive(True)
        if self.msg != None:
            self.myAgent.DEBUG("Response received for method "+service.getName(),'ok')
            if self.msg.getType() == "result":
                params, method = xmlrpclib.loads("<?xml version='1.0'?>%s" % self.msg)
                self.results = params
                #if agent is a BDIAgent add result params as postconditions
                if "addBelieve" in dir(self.myAgent):
                    for q in params:
                        self.myAgent.addBelieve(q)
                return
        else:
            self.results = False
            return


