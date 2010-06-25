import Behaviour
import xmlrpclib
import xmpp

class RPCServerBehaviour(Behaviour.EventBehaviour):

    def _process(self):
        self.result=None
        self.msg = self._receive(False)
        if self.msg != None:
            if self.msg.getType() == "set":
                
                self.myAgent.DEBUG("RPC request received: "+str(self.msg))
                
                mc = self.msg.getTag('query')
                params, name = xmlrpclib.loads("<?xml version='1.0'?>%s" % str(mc))
                self.myAgent.DEBUG("Params processed: name="+name+" params="+str(params) + " in " + str(self.myAgent.RPC.keys()))
                    
                if not self.myAgent.RPC.has_key(name):
                    xmlrpc_res = xmlrpclib.dumps( xmlrpclib.Fault(404, "method not found"))
                    reply = self.msg.buildReply("error")
                    reply.setQueryPayload([xmpp.simplexml.XML2Node(xmlrpc_res)])
                    self.myAgent.jabber.send(reply)
                    self.DEBUG("RPC: 404 method not found",'error')
                    return
                    
                service,methodCall = self.myAgent.RPC[name]
                for p in params:
                    if p not in service.getP():
                        xmlrpc_res = xmlrpclib.dumps( xmlrpclib.Fault(500, "missing precondition"))
                        reply = self.msg.buildReply("error")
                        reply.setQueryPayload([xmpp.simplexml.XML2Node(xmlrpc_res)])
                        self.myAgent.jabber.send(reply)
                        self.myAgent.DEBUG("RPC: 500 missing precondition",'error')
                        return
                
                try:
                    self.myAgent.DEBUG("Calling method "+str(methodCall)+" with params "+str(params))
                    if params == (None,):
                        result = methodCall()
                    else:
                        result = methodCall(params)
                    xmlrpc_res = xmlrpclib.dumps( tuple([result]) , methodresponse=True)
                    reply = self.msg.buildReply("result")
                    reply.setQueryPayload([xmpp.simplexml.XML2Node(xmlrpc_res)])
                    self.myAgent.jabber.send(reply)
                    self.DEBUG("RPC: method succesfully served",'ok')
                except Exception,e:
                    xmlrpc_res = xmlrpclib.dumps( xmlrpclib.Fault(500, "method error: "+str(e)))
                    reply = self.msg.buildReply("error")
                    reply.setQueryPayload([xmpp.simplexml.XML2Node(xmlrpc_res)])
                    self.myAgent.jabber.send(reply)
                    self.DEBUG("RPC: 500 method error: "+str(e),'error')
                    return
        
        else:
            self.myAgent.DEBUG("RPCServerBehaviour returned with no message", "warn")
            
class RPCClientBehaviour(Behaviour.OneShotBehaviour):
    
    def __init__(self, service,num):
        Behaviour.OneShotBehaviour.__init__(self)
        self.service = service
        self.num = num

    def _process(self):
        self.result=None
        
        #send IQ methodCall
        params = [self.service.getP()]
        params = tuple(params,)
        self.myAgent.DEBUG("Params processed: "+str(params))
        
        #if agent is a BDIAgent check preconditions
        if "askBelieve" in dir(self.myAgent):
            for p in params:
                if not self.myAgent.askBelieve(p):
                    self.result=False
                    self.myAgent.DEBUG("Precondition "+ str(p) + " is not satisfied. Can't call method "+self.service.getName(),'error')
                    return
            
        payload = xmlrpclib.dumps( params , methodname=self.service.getName(),allow_none=True)
        self.myAgent.DEBUG("Marshalled "+payload)
        payload_node = xmpp.simplexml.XML2Node(payload)
        to = xmpp.protocol.JID(self.service.getOwner().getName())
        iq = xmpp.protocol.Iq(typ='set',queryNS="jabber:iq:rpc",to=to,attrs={'id':self.num})
        iq.setQueryPayload([payload_node])
        self.myAgent.DEBUG("Calling method with: "+str(iq))
        self.myAgent.jabber.send(iq)
        self.myAgent.DEBUG(self.service.getName() + " method called. Waiting for response",'ok')
        
        #receive IQ methodResponse
        self.msg = self._receive(True)
        if self.msg != None:
            self.myAgent.DEBUG("Response received for method "+self.service.getName(),'ok')
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


