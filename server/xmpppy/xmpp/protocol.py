##   protocol.py 
##
##   Copyright (C) 2003-2004 Alexey "Snake" Nezhdanov
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

# $Id: protocol.py,v 1.36 2004/10/23 07:58:03 snakeru Exp $

from simplexml import Node,ustr
import time

NS_AGENTS       ='jabber:iq:agents'
NS_AMP          ='http://jabber.org/protocol/amp'
NS_AUTH         ='jabber:iq:auth'
NS_BIND         ='urn:ietf:params:xml:ns:xmpp-bind'
NS_BROWSE       ='jabber:iq:browse'
NS_CLIENT       ='jabber:client'
NS_DATA         ='jabber:x:data'                                # JEP-0004
NS_DELAY        ='jabber:x:delay'
NS_DIALBACK     ='jabber:server:dialback'
NS_DISCO_INFO   ='http://jabber.org/protocol/disco#info'
NS_DISCO_ITEMS  ='http://jabber.org/protocol/disco#items'
NS_GROUPCHAT    ='gc-1.0'
NS_IBB          ='http://jabber.org/protocol/ibb'
NS_INVISIBLE    ='presence-invisible'                           # jabberd2
NS_IQ           ='iq'                                           # jabberd2
NS_LAST         ='jabber:iq:last'
NS_MESSAGE      ='message'                                      # jabberd2
NS_OFFLINE      ='http://www.jabber.org/jeps/jep-0030.html'     # JEP-0013   
NS_PRESENCE     ='presence'                                     # jabberd2
NS_PRIVACY      ='jabber:iq:privacy'
NS_PRIVATE      ='jabber:iq:private'
NS_REGISTER     ='jabber:iq:register'
NS_ROSTER       ='jabber:iq:roster'
NS_RPC          ='jabber:iq:rpc'                                # JEP-0009
NS_SASL         ='urn:ietf:params:xml:ns:xmpp-sasl'
NS_SEARCH       ='jabber:iq:search'
NS_SERVER       ='jabber:server'
NS_SESSION      ='urn:ietf:params:xml:ns:xmpp-session'
NS_STANZAS      ='urn:ietf:params:xml:ns:xmpp-stanzas'
NS_STREAMS      ='http://etherx.jabber.org/streams'
NS_TIME         ='jabber:iq:time'
NS_TLS          ='urn:ietf:params:xml:ns:xmpp-tls'
NS_VACATION     ='http://jabber.org/protocol/vacation'
NS_VCARD        ='vcard-temp'
NS_VERSION      ='jabber:iq:version'
NS_XMPP_STREAMS ='urn:ietf:params:xml:ns:xmpp-streams'

xmpp_stream_error_conditions="""
bad-format --  --  -- The entity has sent XML that cannot be processed.
bad-namespace-prefix --  --  -- The entity has sent a namespace prefix that is unsupported, or has sent no namespace prefix on an element that requires such a prefix.
conflict --  --  -- The server is closing the active stream for this entity because a new stream has been initiated that conflicts with the existing stream.
connection-timeout --  --  -- The entity has not generated any traffic over the stream for some period of time.
host-gone --  --  -- The value of the 'to' attribute provided by the initiating entity in the stream header corresponds to a hostname that is no longer hosted by the server.
host-unknown --  --  -- The value of the 'to' attribute provided by the initiating entity in the stream header does not correspond to a hostname that is hosted by the server.
improper-addressing --  --  -- A stanza sent between two servers lacks a 'to' or 'from' attribute (or the attribute has no value).
internal-server-error --  --  -- The server has experienced a misconfiguration or an otherwise-undefined internal error that prevents it from servicing the stream.
invalid-from -- cancel --  -- The JID or hostname provided in a 'from' address does not match an authorized JID or validated domain negotiated between servers via SASL or dialback, or between a client and a server via authentication and resource authorization.
invalid-id --  --  -- The stream ID or dialback ID is invalid or does not match an ID previously provided.
invalid-namespace --  --  -- The streams namespace name is something other than "http://etherx.jabber.org/streams" or the dialback namespace name is something other than "jabber:server:dialback".
invalid-xml --  --  -- The entity has sent invalid XML over the stream to a server that performs validation.
not-authorized --  --  -- The entity has attempted to send data before the stream has been authenticated, or otherwise is not authorized to perform an action related to stream negotiation.
policy-violation --  --  -- The entity has violated some local service policy.
remote-connection-failed --  --  -- The server is unable to properly connect to a remote resource that is required for authentication or authorization.
resource-constraint --  --  -- The server lacks the system resources necessary to service the stream.
restricted-xml --  --  -- The entity has attempted to send restricted XML features such as a comment, processing instruction, DTD, entity reference, or unescaped character.
see-other-host --  --  -- The server will not provide service to the initiating entity but is redirecting traffic to another host.
system-shutdown --  --  -- The server is being shut down and all active streams are being closed.
undefined-condition --  --  -- The error condition is not one of those defined by the other conditions in this list.
unsupported-encoding --  --  -- The initiating entity has encoded the stream in an encoding that is not supported by the server.
unsupported-stanza-type --  --  -- The initiating entity has sent a first-level child of the stream that is not supported by the server.
unsupported-version --  --  -- The value of the 'version' attribute provided by the initiating entity in the stream header specifies a version of XMPP that is not supported by the server.
xml-not-well-formed --  --  -- The initiating entity has sent XML that is not well-formed."""
xmpp_stanza_error_conditions="""
bad-request -- 400 -- modify -- The sender has sent XML that is malformed or that cannot be processed.
conflict -- 409 -- cancel -- Access cannot be granted because an existing resource or session exists with the same name or address.
feature-not-implemented -- 501 -- cancel -- The feature requested is not implemented by the recipient or server and therefore cannot be processed.
forbidden -- 403 -- auth -- The requesting entity does not possess the required permissions to perform the action.
gone -- 302 -- modify -- The recipient or server can no longer be contacted at this address.
internal-server-error -- 500 -- wait -- The server could not process the stanza because of a misconfiguration or an otherwise-undefined internal server error.
item-not-found -- 404 -- cancel -- The addressed JID or item requested cannot be found.
jid-malformed -- 400 -- modify -- The value of the 'to' attribute in the sender's stanza does not adhere to the syntax defined in Addressing Scheme.
not-acceptable -- 406 -- cancel -- The recipient or server understands the request but is refusing to process it because it does not meet criteria defined by the recipient or server.
not-allowed -- 405 -- cancel -- The recipient or server does not allow any entity to perform the action.
not-authorized -- 401 -- auth -- The sender must provide proper credentials before being allowed to perform the action, or has provided improper credentials.
payment-required -- 402 -- auth -- The requesting entity is not authorized to access the requested service because payment is required.
recipient-unavailable -- 404 -- wait -- The intended recipient is temporarily unavailable.
redirect -- 302 -- modify -- The recipient or server is redirecting requests for this information to another entity.
registration-required -- 407 -- auth -- The requesting entity is not authorized to access the requested service because registration is required.
remote-server-not-found -- 404 -- cancel -- A remote server or service specified as part or all of the JID of the intended recipient does not exist.
remote-server-timeout -- 504 -- wait -- A remote server or service specified as part or all of the JID of the intended recipient could not be contacted within a reasonable amount of time.
resource-constraint -- 500 -- wait -- The server or recipient lacks the system resources necessary to service the request.
service-unavailable -- 503 -- cancel -- The server or recipient does not currently provide the requested service.
subscription-required -- 407 -- auth -- The requesting entity is not authorized to access the requested service because a subscription is required.
undefined-condition -- 500 --  -- 
unexpected-request -- 400 -- wait -- The recipient or server understood the request but was not expecting it at this time (e.g., the request was out of order)."""
sasl_error_conditions="""
aborted --  --  -- The receiving entity acknowledges an <abort/> element sent by the initiating entity; sent in reply to the <abort/> element.
incorrect-encoding --  --  -- The data provided by the initiating entity could not be processed because the [BASE64]Josefsson, S., The Base16, Base32, and Base64 Data Encodings, July 2003. encoding is incorrect (e.g., because the encoding does not adhere to the definition in Section 3 of [BASE64]Josefsson, S., The Base16, Base32, and Base64 Data Encodings, July 2003.); sent in reply to a <response/> element or an <auth/> element with initial response data.
invalid-authzid --  --  -- The authzid provided by the initiating entity is invalid, either because it is incorrectly formatted or because the initiating entity does not have permissions to authorize that ID; sent in reply to a <response/> element or an <auth/> element with initial response data.
invalid-mechanism --  --  -- The initiating entity did not provide a mechanism or requested a mechanism that is not supported by the receiving entity; sent in reply to an <auth/> element.
mechanism-too-weak --  --  -- The mechanism requested by the initiating entity is weaker than server policy permits for that initiating entity; sent in reply to a <response/> element or an <auth/> element with initial response data.
not-authorized --  --  -- The authentication failed because the initiating entity did not provide valid credentials (this includes but is not limited to the case of an unknown username); sent in reply to a <response/> element or an <auth/> element with initial response data.
temporary-auth-failure --  --  -- The authentication failed because of a temporary error condition within the receiving entity; sent in reply to an <auth/> element or <response/> element."""

ERRORS,_errorcodes={},{}
for ns,errname,errpool in [(NS_XMPP_STREAMS,'STREAM',xmpp_stream_error_conditions),
                           (NS_STANZAS     ,'ERR'   ,xmpp_stanza_error_conditions),
                           (NS_SASL        ,'SASL'  ,sasl_error_conditions)]:
    for err in errpool.split('\n')[1:]:
        cond,code,typ,text=err.split(' -- ')
        name=errname+'_'+cond.upper().replace('-','_')
        locals()[name]=ns+' '+cond
        ERRORS[ns+' '+cond]=[code,typ,text]
        if code: _errorcodes[code]=cond
del ns,errname,errpool,err,cond,code,typ,text

def isResultNode(node): return node and node.getType()=='result'
def isErrorNode(node): return node and node.getType()=='error'

class NodeProcessed(Exception): pass

class JID:
    def __init__(self, jid, node='', domain='', resource=''):
        if not jid: raise ValueError('JID must contain at least domain name')
        elif type(jid)==type(self): self.node,self.domain,self.resource=jid.node,jid.domain,jid.resource
        elif domain: self.node,self.domain,self.resource=node,domain,resource
        else:
            if jid.find('@')+1: self.node,jid=jid.split('@',1)
            else: self.node=''
            if jid.find('/')+1: self.domain,self.resource=jid.split('/',1)
            else: self.domain,self.resource=jid,''
    def getNode(self): return self.node
    def setNode(self,node): self.node=node.lower()
    def getDomain(self): return self.domain
    def setDomain(self,domain): self.domain=domain.lower()
    def getResource(self): return self.resource
    def setResource(self,resource): self.resource=resource
    def getStripped(self): return self.__str__(0)
    def __eq__(self, other):
        try: other=JID(other)
        except ValueError: return 0
        return self.resource==other.resource and self.__str__(0) == other.__str__(0)
    def __ne__(self, other): return not self.__eq__(other)
    def bareMatch(self, other): return self.__str__(0) == JID(other).__str__(0)
    def __str__(self,wresource=1):
        if self.node: jid=self.node+'@'+self.domain
        else: jid=self.domain
        if wresource and self.resource: return jid+'/'+self.resource
        return jid
    def __hash__(self): return hash(self.__str__())

class Protocol(Node):
    def __init__(self, name=None, to=None, typ=None, frm=None, attrs={}, payload=[], timestamp=None, xmlns=NS_CLIENT, node=None):
        if not attrs: attrs={}
        if to: attrs['to']=to
        if frm: attrs['from']=frm
        if typ: attrs['type']=typ
        Node.__init__(self, tag=name, attrs=attrs, payload=payload, node=node)
        if not node: self.setNamespace(xmlns)
        if self['to']: self.setTo(self['to'])
        if self['from']: self.setFrom(self['from'])
        if node and type(self)==type(node) and self.__class__==node.__class__ and self.attrs.has_key('id'): del self.attrs['id']
        self.timestamp=None
        for x in self.getTags('x',namespace=NS_DELAY):
            try:
                if x.getAttr('stamp')>self.getTimestamp(): self.setTimestamp(x.getAttr('stamp'))
            except: pass
        if timestamp is not None: self.setTimestamp(timestamp)  # To auto-timestamp stanza just pass timestamp=''
    def getTo(self):
        try: return self['to']
        except: return None
    def getFrom(self):
        try: return self['from']
        except: return None
    def getTimestamp(self): return self.timestamp
    def getID(self): return self.getAttr('id')
    def setTo(self,val): self.setAttr('to', JID(val))
    def getType(self): return self.getAttr('type')
    def setFrom(self,val): self.setAttr('from', JID(val))
    def setType(self,val): self.setAttr('type', val)
    def setID(self,val): self.setAttr('id', val)
    def getError(self):
        errtag=self.getTag('error')
        if errtag:
            for tag in errtag.getChildren():
                if tag.getName()<>'text': return tag.getName()
            return errtag.getData()
    def getErrorCode(self): return self.getTagAttr('error','code')
    def setError(self,error,code=None):
        if code:
            if str(code) in _errorcodes.keys(): error=ErrorNode(_errorcodes[str(code)],text=error)
            else: error=ErrorNode(ERR_UNDEFINED_CONDITION,code=code,typ='cancel',text=error)
        elif type(error) in [type(''),type(u'')]: error=ErrorNode(error)
        self.setType('error')
        self.addChild(node=error)
    def setTimestamp(self,val=None):
        if not val: val=time.strftime('%Y%m%dT%H:%M:%S', time.gmtime())
        self.timestamp=val
        self.setTag('x',{'stamp':self.timestamp},namespace=NS_DELAY)
    def getProperties(self):
        props=[]
        for child in self.getChildren():
            prop=child.getNamespace()
            if prop not in props: props.append(prop)
        return props
    def __setitem__(self,item,val):
        if item in ['to','from']: val=JID(val)
        return self.setAttr(item,val)

class Message(Protocol):
    def __init__(self, to=None, body=None, typ=None, subject=None, attrs={}, frm=None, payload=[], timestamp=None, xmlns=NS_CLIENT, node=None):
        Protocol.__init__(self, 'message', to=to, typ=typ, attrs=attrs, frm=frm, payload=payload, timestamp=timestamp, xmlns=xmlns, node=node)
        if body: self.setBody(body)
        if subject: self.setSubject(subject)
    def getBody(self): return self.getTagData('body')
    def getSubject(self): return self.getTagData('subject')
    def getThread(self): return self.getTagData('thread')
    def setBody(self,val): self.setTagData('body',val)
    def setSubject(self,val): self.setTagData('subject',val)
    def setThread(self,val): self.setTagData('thread',val)
    def buildReply(self,text=None): return Message(to=self.getFrom(),frm=self.getTo(),body=text,node=self)

class Presence(Protocol):
    def __init__(self, to=None, typ=None, priority=None, show=None, status=None, attrs={}, frm=None, timestamp=None, payload=[], xmlns=NS_CLIENT, node=None):
        Protocol.__init__(self, 'presence', to=to, typ=typ, attrs=attrs, frm=frm, payload=payload, timestamp=timestamp, xmlns=xmlns, node=node)
        if priority: self.setPriority(priority)
        if show: self.setShow(show)
        if status: self.setStatus(status)
    def getPriority(self): return self.getTagData('priority')
    def getShow(self): return self.getTagData('show')
    def getStatus(self): return self.getTagData('status')
    def setPriority(self,val): self.setTagData('priority',val)
    def setShow(self,val): self.setTagData('show',val)
    def setStatus(self,val): self.setTagData('status',val)

class Iq(Protocol): 
    def __init__(self, typ=None, queryNS=None, attrs={}, to=None, frm=None, payload=[], xmlns=NS_CLIENT, node=None):
        Protocol.__init__(self, 'iq', to=to, typ=typ, attrs=attrs, frm=frm, xmlns=xmlns, node=node)
        if payload: self.setQueryPayload(payload)
        if queryNS: self.setQueryNS(queryNS)
    def getQueryNS(self):
        tag=self.getTag('query')
        if tag: return tag.getNamespace()
    def getQuerynode(self): return self.getTagAttr('query','node')
    def getQueryPayload(self):
        tag=self.getTag('query')
        if tag: return tag.getPayload()
    def getQueryChildren(self):
        tag=self.getTag('query')
        if tag: return tag.getChildren()
    def setQueryNS(self,namespace): self.setTag('query').setNamespace(namespace)
    def setQueryPayload(self,payload): self.setTag('query').setPayload(payload)
    def setQuerynode(self,node): self.setTagAttr('query','node',node)
    def buildReply(self,typ):
        iq=Iq(typ,to=self.getFrom(),frm=self.getTo(),attrs={'id':self.getID()})
        if self.getTag('query'): iq.setQueryNS(self.getQueryNS())
        return iq

class ErrorNode(Node):
    def __init__(self,name,code=None,typ=None,text=None):
        """ Mandatory parameter: name
            Optional parameters: code, typ, text."""
        if ERRORS.has_key(name):
            cod,type,txt=ERRORS[name]
            ns=name.split()[0]
        else: cod,ns,type,txt='500',NS_STANZAS,'cancel',''
        if typ: type=typ
        if code: cod=code
        if text: txt=text
        Node.__init__(self,'error',{},[Node(name)])
        if type: self.setAttr('type',type)
        if not cod: self.setName('stream:error')
        if txt: self.addChild(node=Node(ns+' text',{},[txt]))
        if cod: self.setAttr('code',cod)

class Error(Protocol):
    def __init__(self,node,error,reply=1):
        if reply: Protocol.__init__(self,to=node.getFrom(),frm=node.getTo(),node=node)
        else: Protocol.__init__(self,node=node)
        self.setError(error)
        if node.getType()=='error': self.__str__=self.__dupstr__
    def __dupstr__(self,dup1=None,dup2=None): return ''

class DataField(Node):
    def __init__(self,name=None,value=None,typ=None,required=0,desc=None,options=[],node=None):
        Node.__init__(self,'field',node=node)
        if name: self.setVar(name)
        if type(value) in [list,tuple]: self.setValues(value)
        elif value: self.setValue(value)
        if typ: self.setType(typ)
        elif not typ and not node: self.setType('text-single')
        if required: self.setRequired(required)
        if desc: self.setDesc(desc)
        if options: self.setOptions(options)
    def setRequired(self,req=1):
        if req: self.setTag('required')
        else:
            try: self.delChild('required')
            except ValueError: return
    def isRequired(self): return self.getTag('required')
    def setDesc(self,desc): self.setTagData('desc',desc)
    def getDesc(self): return self.getTagData('desc')
    def setValue(self,val): self.setTagData('value',val)
    def getValue(self): return self.getTagData('value')
    def setValues(self,lst):
        while self.getTag('value'): self.delChild('value')
        for val in lst: self.addValue(val)
    def addValue(self,val): self.addChild('value',{},[val])
    def getValues(self):
        ret=[]
        for tag in self.getTags('value'): ret.append(tag.getData())
        return ret
    def getOptions(self):
        ret=[]
        for tag in self.getTags('option'): ret.append([tag.getAttr('label'),tag.getTagData('value')])
        return ret
    def setOptions(self,lst):
        while self.getTag('option'): self.delChild('option')
        for opt in lst: self.addOption(opt)
    def addOption(self,opt):
        if type(opt) in [str,unicode]: self.addChild('option').setTagData('value',opt)
        else: self.addChild('option',{'label':opt[0]}).setTagData('value',opt[1])
    def getType(self): return self.getAttr('type')
    def setType(self,val): return self.setAttr('type',val)
    def getVar(self): return self.getAttr('var')
    def setVar(self,val): return self.setAttr('var',val)

class DataForm(Node):
    """ X-Data relevant JEPs: 0004, 0068, 0122 """
    def __init__(self, typ=None, data=[], title=None, node=None):
        """
            title and instructions: optional. SHOULD NOT contain newlines.
            Several instructions MAY be present.
            type={ form | submit | cancel | result } # iq: { result | set | set | result }
            'cancel' form contains no fields. Other forms contains AT LEAST one field.
            title MAY be included in forms of type "form|result"
        """
        Node.__init__(self,'x',node=node)
        if node:
            newkids=[]
            for n in self.getChildren():
                if n.getName()=='field': newkids.append(DataField(node=n))
                else: newkids.append(n)
            self.kids=newkids
        if typ: self.setType(typ)
        self.setNamespace(NS_DATA)
        if title: self.setTitle(title)
        if type(data)==type({}):
            newdata=[]
            for name in data.keys(): newdata.append(DataField(name,data[name]))
            data=newdata
        for child in data:
            if type(child) in [type(''),type(u'')]: self.addInstructions(child)
            elif child.__class__.__name__=='DataField': self.kids.append(child)
            else: self.kids.append(DataField(node=child))
    def getType(self): return self.getAttr('type')
    def setType(self,typ): self.setAttr('type',typ)
    def getTitle(self): return self.getTagData('title')
    def setTitle(self,text): self.setTagData('title',text)
    def getInstructions(self): return self.getTagData('instructions')
    def setInstructions(self,text): self.setTagData('instructions',text)
    def addInstructions(self,text): self.addChild('instructions',{},[text])
    def getField(self,name): return self.getTag('field',attrs={'var':name})
    def setField(self,name):
        f=self.getField(name)
        if f: return f
        return self.addChild(node=DataField(name))
    def asDict(self):
        ret={}
        for field in self.getTags('field'):
            name=field.getAttr('var')
            typ=field.getType()
            if type(typ) in [type(''),type(u'')] and typ[-6:]=='multi':
                val=[]
                for i in field.getTags('value'): val.append(i.getData())
            else: val=field.getTagData('value')
            ret[name]=val
        return ret
    def __getitem__(self,name):
        item=self.getField(name)
        if item: return item.getValue()
        raise IndexError('No such field')
    def __setitem__(self,name,val): return self.setField(name).setValue(val)
