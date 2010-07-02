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
                name=name.lower()
                self.myAgent.DEBUG("Params processed: name="+name+" params="+str(params) + " in " + str(self.myAgent.RPC.keys()))
                    
                if not self.myAgent.RPC.has_key(name):
                    self.myAgent.DEBUG("RPC: 404 method not found",'error')
                    xmlrpc_res = xmlrpclib.dumps( xmlrpclib.Fault(404, "method not found"))
                    reply = self.msg.buildReply("error")
                    reply.setQueryPayload([xmpp.simplexml.XML2Node(xmlrpc_res)])
                    reply.setType("result")
                    reply.setFrom(self.myAgent.JID)
                    self.myAgent.send(reply)
                    return
                    
                service,methodCall = self.myAgent.RPC[name]
                
                self.myAgent.DEBUG("service and method: "+ str(service) + " --> " + str(methodCall))
                
                self.myAgent.DEBUG("Comparing service.getP(): "+ str(service.getP()) + " with params--> " + str(params))
                for p in service.getP():
                    if str(p) not in str(params):
                        self.myAgent.DEBUG("RPC: 500 missing precondition: "+str(p)+ " is not in "+str(params),'error')
                        xmlrpc_res = xmlrpclib.dumps( xmlrpclib.Fault(500, "missing precondition"))
                        reply = self.msg.buildReply("error")
                        reply.setQueryPayload([xmpp.simplexml.XML2Node(xmlrpc_res)])
                        reply.setType("result")
                        reply.setFrom(self.myAgent.JID)
                        self.myAgent.send(reply)
                        return
                
                try:
                    self.myAgent.DEBUG("Calling method "+str(methodCall)+" with params "+str(params))
                    if params == (None,):
                        result = methodCall()
                    else:
                        result = methodCall(params)
                    xmlrpc_res = xmlrpclib.dumps( tuple([result]) , methodresponse=True,allow_none=True)
                    reply = self.msg.buildReply("result")
                    reply.setQueryPayload([xmpp.simplexml.XML2Node(xmlrpc_res)])
                    self.myAgent.send(reply)
                    self.myAgent.DEBUG("RPC: method succesfully served: "+ str(reply),'ok')
                except Exception,e:
                    self.myAgent.DEBUG("RPC: 500 method error: "+str(e),'error')
                    xmlrpc_res = xmlrpclib.dumps( xmlrpclib.Fault(500, "method error: "+str(e)))
                    reply = self.msg.buildReply("error")
                    reply.setQueryPayload([xmpp.simplexml.XML2Node(xmlrpc_res)])
                    reply.setType("result")
                    reply.setFrom(self.myAgent.JID)
                    self.myAgent.send(reply)
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
        params = None
        ps     = None
        ps = self.service.getP() #self.service.getDAD().getServices()[0].getProperty("P")
        params = tuple(ps)
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
        iq = xmpp.protocol.Iq(typ='set',queryNS="jabber:iq:rpc",frm=self.myAgent.JID,to=to,attrs={'id':self.num})
        iq.setQueryPayload([payload_node])
        self.myAgent.DEBUG("Calling method with: "+str(iq))
        self.myAgent.send(iq)
        self.myAgent.DEBUG(self.service.getName() + " method called. Waiting for response",'ok')
        
        #receive IQ methodResponse
        self.msg = self._receive(True)
        if self.msg != None:
            self.myAgent.DEBUG("Response received for method "+self.service.getName()+":" +str(self.msg),'ok')
            if self.msg.getType() == "result":
                try:
                    params, method = xmlrpclib.loads("<?xml version='1.0'?>%s" % self.msg)
                    self.DEBUG("Returned params "+str(params),'ok')
                    self.result = [params[0]]
                    #if agent is a BDIAgent add result params as postconditions
                    if "addBelieve" in dir(self.myAgent):
                        for q in params: #[0]:
                            self.myAgent.addBelieve(q)
                    return [params[0]]
                except Exception,e:
                    self.myAgent.DEBUG("Error executing RPC service: "+str(e))
                    self.result = False
                    return False
        else:
            self.result = False
            return False


