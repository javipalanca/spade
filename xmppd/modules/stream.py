# -*- coding: utf-8 -*-
# Distributed under the terms of GPL version 2 or any later
# Copyright (C) Kristopher Tate / BlueBridge Technologies Group 2005
# Copyright (C) Alexey Nezhdanov 2004

# Stream-level features for xmppd.py

from xmpp import *
try:
    from xmppd.xmppd import *
except:
    from xmppd import *
import socket
import thread
from tlslite.api import *
import hashlib


class TLS(PlugIn):
    """ 3.                        <features/>
        4. <starttls/>
        5.                        <proceed/> / <failure/>
        -- NEW STREAM / connection close --
        """
    NS = NS_TLS

    def plugin(self, server):
        server.Dispatcher.RegisterHandler('starttls', self.starttlsHandler, xmlns=NS_TLS)
        server.Dispatcher.RegisterHandler('proceed', self.proceedfailureHandler, xmlns=NS_TLS)
        server.Dispatcher.RegisterHandler('failure', self.proceedfailureHandler, xmlns=NS_TLS)
        server.Dispatcher.RegisterHandler('features', self.FeaturesHandler, xmlns=NS_STREAMS)

    def starttlsHandler(self, session, stanza):
        #print stanza
        if 'tls' in session.features:
            session.send(Node('failure', {'xmlns': NS_TLS}))
            self.DEBUG('TLS startup failure: already started.', 'error')
            session.unfeature(NS_TLS)
            raise NodeProcessed
        if 'sslcertfile' in self._owner.__dict__:
            certfile = self._owner.sslcertfile
        else:
            certfile = None
        if 'sslkeyfile' in self._owner.__dict__:
            keyfile = self._owner.sslkeyfile
        else:
            keyfile = certfile
        try:
            open(certfile)
            open(keyfile)
        except:
            certfile = None
        if not certfile or not keyfile:
            session.send(Node('failure', {'xmlns': NS_TLS}))
            self.DEBUG('TLS startup failure: can\'t find SSL cert/key file[s].', 'error')
            session.unfeature(NS_TLS)    # do not declare TLS anymore
            session.stop_feature(NS_TLS)  # TLS finished, let another features start
        else:
            session.send(Node('proceed', {'xmlns': NS_TLS}))
            self.startservertls(session)
        raise NodeProcessed

    def startservertls(self, session):
        session._owner.unregistersession(session)
        self._startservertls(session)

    def _startservertls(self, session):
        try:
            cert = open(self._owner.sslcertfile).read()
            key = open(self._owner.sslkeyfile).read()
        except:
            session.unfeature(NS_TLS)
            session.terminate_stream(STREAM_INTERNAL_SERVER_ERROR)
            return

        x509 = X509()
        x509.parse(cert)
        certChain = X509CertChain([x509])
        privateKey = parsePEMKey(key, private=True)
        connection = TLSConnection(session._sock)
        try:
            connection.handshakeServer(certChain=certChain, privateKey=privateKey, reqCert=False)
        except:
            session.terminate_stream(unregister=0)
            return

        session._sslObj = connection
        session._recv = connection.read
        session._send = connection.send

        session.feature(NS_TLS)      # TLS enabled, do not declare it anymore
        session.stop_feature(NS_TLS)  # TLS finished, let another features start
        session.StartStream()
        session._owner.registersession(session)

    def proceedfailureHandler(self, session, stanza):
        if stanza.getName() != 'proceed':
            self.DEBUG('TLS can not be started. Giving up.', 'error')
            session.unfeature(NS_TLS)
            raise NodeProcessed
        self.DEBUG('Starting client-mode TLS.', 'ok')
        try:
            session._sslObj = socket.ssl(session._sock, None, None)
        except:
            session.set_socket_state(SOCKET_DEAD)
            self.DEBUG('TLS failed. Terminating session', 'error')
            session.terminate_stream()
            raise NodeProcessed
        session._recv = session._sslObj.read
        session._send = session._sslObj.write

        session.feature(NS_TLS)      # TLS enabled, do not declare it anymore
        session.stop_feature(NS_TLS)  # TLS finished, let another features start
        session.StartStream()
        raise NodeProcessed

    def FeaturesHandler(self, session, stanza):
        if NS_TLS in session.features:
            return     # already started. do nothing
        if session.feature_in_process:
            return     # some other feature is already underway
        if not stanza.getTag('starttls', namespace=NS_TLS):
            self.DEBUG("TLS unsupported by remote server; Doing nothing -- Prob. jabber.org?", 'warn')
            return
        else:
            self.DEBUG("TLS supported by remote server. Requesting TLS start.", 'ok')
            session.start_feature(NS_TLS)
            session.send(Node('starttls', {'xmlns': NS_TLS}))
        raise NodeProcessed

import hashlib
import base64
import random


def HH(some):
    return hashlib.md5(some).hexdigest()


def H(some):
    return hashlib.md5(some).digest()


def C(some):
    return ':'.join(some)


class SASL(PlugIn):
    NS = NS_SASL
    """ 3.                        <features/>
        4. <auth/>
        5.                        <challenge/> / <failure/>
        6. <response/>
        7.                        <challenge/> / <failure/>
        8. <response/> / <abort/>
        9.                        <success/>   / <failure/>
        feature SASL, unfeature TLS
        -- NEW STREAM on success --

        What to do on failure (remote server rejected us)?
        Probably drop the stream, mark this server as unreachable for several hours and notify admin?
        If client supplied wrong credentials allow him to retry (configurable number of times).
        """

    def plugin(self, server):
        server.Dispatcher.RegisterNamespaceHandler(NS_SASL, self.SASLHandler)
#        server.Dispatcher.RegisterHandler('features',self.FeaturesHandler,xmlns=NS_STREAMS)
        self.mechanisms = ['PLAIN']  # ,'DIGEST-MD5']  # for announce in <features/> tag

    """    def startauth(self,session,username,password):
        session.username=username
        session.password=password
        if session.Stream.features:
            try: self.FeaturesHandler(session,session.Stream.features)
            except NodeProcessed: pass

    def FeaturesHandler(self,session,feats):
        if session.feature_in_process: return     # some other feature is already underway
        if not session.__dict__.has_key('username'): return
        if not feats.getTag('mechanisms',namespace=NS_SASL):
            session.unfeature(NS_SASL)
            self.DEBUG('SASL not supported by server','error')
            return
        mecs=[]
        for mec in feats.getTag('mechanisms',namespace=NS_SASL).getTags('mechanism'):
            mecs.append(mec.getData())
        if "DIGEST-MD5" in mecs:
            node=Node('auth',attrs={'xmlns':NS_SASL,'mechanism':'DIGEST-MD5'})
        elif "PLAIN" in mecs:
            sasl_data='%s\x00%s\x00%s'%(self.username+'@'+session.peer,self.username,self.password)
            node=Node('auth',attrs={'xmlns':NS_SASL,'mechanism':'PLAIN'},payload=[base64.encodestring(sasl_data)])
        else:
            session.startsasl='failure'
            self.DEBUG('I can only use DIGEST-MD5 and PLAIN mecanisms.','error')
            return
        session.startsasl='in-process'
        session.send(node)
        raise NodeProcessed
"""
    def commit_auth(self, session, authzid):
        session.send(Node('success', {'xmlns': NS_SASL}))
        session.feature(NS_SASL)
        session.unfeature(NS_TLS)
        session.sasl['next'] = []
        session.StartStream()
        session.peer = authzid.lower()
        if session.xmlns == NS_CLIENT:
            session.set_session_state(SESSION_AUTHED)
        else:
            session.set_session_state(SESSION_BOUND)
        self.DEBUG('Peer %s successfully authenticated' % authzid, 'ok')
        self._owner.activatesession(session, authzid)

    def reject_auth(self, session, authzid='unknown'):
        session.send(Node('failure', {'xmlns': NS_SASL}, [Node('not-authorized')]))
        session.sasl['retries'] = session.sasl['retries'] - 1
        if session.sasl['retries'] <= 0:
            session.terminate_stream()
        self.DEBUG('Peer %s failed to authenticate' % authzid, 'error')

    def SASLHandler(self, session, stanza):
        """simple username: servername _or_ node@servername : 6.1 (6)
        """
        if NS_SASL in session.features:
            self.DEBUG('Already authorized. Ignoring SASL stanza.', 'error')
            raise NodeProcessed
        if 'sasl' not in session.__dict__:
            session.sasl = {'retries': 3}
        if 'next' not in session.sasl:
            session.sasl = {'retries': session.sasl['retries']}
            if session.TYP == 'server':
                session.sasl['next'] = ['auth']
            else:
                session.sasl['next'] = ['challenge', 'success', 'failure']
        if stanza.getName() not in session.sasl['next']:
            # screwed SASL implementation on the other side. terminating stream
            session.terminate_stream(STREAM_BAD_REQUEST)
            raise NodeProcessed
        #=================== preparation ===============================================
        try:
            data = base64.decodestring(stanza.getData())
        except:
            session.terminate_stream(STREAM_BAD_REQUEST)
            raise NodeProcessed
        self.DEBUG('Got challenge: ' + repr(data), 'ok')
        for pair in data.split(','):
            if pair.find('=') == -1:
                session.sasl['otherdata'] = pair
                continue
            key, value = pair.split('=', 1)
            if value[:1] == '"' and value[-1:] == '"': value = value[1:-1]
            if key in ['qop', 'username', 'realm', 'nonce', 'cnonce', 'digest-uri',
                       'nc', 'response', 'charset', 'rspauth', 'algorithm']:
                chal[key] = value
        #=================== SASL begin ===============================================
        if stanza.getName() == 'auth':
            session.sasl['next'] = ['response', 'abort', 'auth']
            # client requested some mechanism. May be ever provided credentials already.
            mec = stanza['mechanism']
            session.sasl['mechanism'] = mec
            if mec == 'PLAIN':
                """The mechanism consists of a single message from the client to the
                   server.  The client sends the authorization identity (identity to
                   login as), followed by a NUL (U+0000) character, followed by the
                   authentication identity (identity whose password will be used),
                   followed by a NUL (U+0000) character, followed by the clear-text
                   password."""
                if 'otherdata' in session.sasl:
                    pack = session.sasl['otherdata'].split('\000')
                else:
                    pack = []
                authzid = session.peer
                if len(pack) != 3:
                    res = 0
                else:
                    authzid, authcid, passwd = pack
                    if not authzid:
                        authzid = authcid
                        if session.xmlns == NS_CLIENT:
                            authzid += '@' + session.ourname
                    username, domain = (authzid.split('@', 1) + [''])[:2]
                    res = (passwd == self._owner.AUTH.getpassword(username, domain))
                if res:
                    self.commit_auth(session, authzid)
                else:
                    self.reject_auth(session, authzid)
            elif mec == 'DIGEST-MD5':
                pass
            else:
                session.terminate_stream(Node('failure', {'xmlns': NS_SASL}, [Node('invalid-mechanism')]))
            raise NodeProcessed
            """elif stanza.getName()=='challenge':
            session.sasl['next']=['challenge','success','failure']
            # DIGEST-MD5 only
            if chal.has_key('qop') and chal['qop']=='auth':
                resp={}
                resp['username']=self.username
                resp['realm']=self._owner.Server
                resp['nonce']=chal['nonce']
                cnonce=''
                for i in range(7):
                    cnonce+=hex(int(random.random()*65536*4096))[2:]
                resp['cnonce']=cnonce
                resp['nc']=('00000001')
                resp['qop']='auth'
                resp['digest-uri']='xmpp/'
                A1=C([H(C([resp['username'],resp['realm'],self.password])),resp['nonce'],resp['cnonce']])
                A2=C(['AUTHENTICATE',resp['digest-uri']])
                response= HH(C([HH(A1),resp['nonce'],resp['nc'],resp['cnonce'],resp['qop'],HH(A2)]))
                resp['response']=response
                resp['charset']='utf-8'
                sasl_data=''
                for key in ['charset','username','realm','nonce','nc','cnonce','digest-uri','response','qop']:
                    if key in ['nc','qop','response','charset']: sasl_data+="%s=%s,"%(key,resp[key])
                    else: sasl_data+='%s="%s",'%(key,resp[key])
                node=Node('response',attrs={'xmlns':NS_SASL},payload=[base64.encodestring(sasl_data[:-1]).replace('\n','')])
                self._owner.send(node)
            elif chal.has_key('rspauth'): self._owner.send(Node('response',attrs={'xmlns':NS_SASL}))
"""
        elif stanza.getName() == 'response':
            session.sasl['next'] = ['response', 'abort']
        elif stanza.getName() == 'abort':
            session.sasl['next'] = ['auth']
        elif stanza.getName() == 'success':
            session.sasl['next'] = []
            session.startsasl = 'success'
            self.DEBUG('Successfully authenticated with remote server.', 'ok')
            session.StartStream()
        elif stanza.getName() == 'failure':
            session.sasl['next'] = ['challenge', 'success', 'failure']
            session.startsasl = 'failure'
            try:
                reason = challenge.getChildren()[0]
            except:
                reason = challenge
            self.DEBUG('Failed SASL authentification: %s' % reason, 'error')
        raise NodeProcessed


class Bind(PlugIn):
    NS = NS_BIND

    def plugin(self, server):
        server.Dispatcher.RegisterHandler('iq', self.bindHandler, typ='set', ns=NS_BIND, xmlns=NS_CLIENT)

    def bindHandler(self, session, stanza):
        if session.xmlns != NS_CLIENT or 'resource' in session.__dict__:
            session.send(Error(stanza, ERR_SERVICE_UNAVAILABLE))
        else:
            if session._session_state < SESSION_AUTHED:
                session.terminate_stream(STREAM_NOT_AUTHORIZED)
                raise NodeProcessed
            resource = stanza.getTag('bind', namespace=NS_BIND).T.resource.getData()
            if not resource:
                resource = session.ID
            fulljid = "%s/%s" % (session.peer, resource)
            session.peer = fulljid
            s = self._owner.deactivatesession(fulljid)
            if s:
                s.terminate_stream(STREAM_CONFLICT)
            rep = stanza.buildReply('result')
            rep.NT.bind.setNamespace(NS_BIND)
            rep.T.bind.NT.jid = fulljid
            session.send(rep)
            session.set_session_state(SESSION_BOUND)
        raise NodeProcessed


class Session(PlugIn):
    NS = NS_SESSION

    def plugin(self, server):
        server.Dispatcher.RegisterHandler('iq', self.sessionHandler, typ='set', ns=NS_SESSION, xmlns=NS_CLIENT)

    def sessionHandler(self, session, stanza):
        if session._session_state < SESSION_AUTHED:
            session.terminate_stream(STREAM_NOT_AUTHORIZED)
            raise NodeProcessed
        if session.xmlns != NS_CLIENT \
            or session._session_state < SESSION_BOUND \
                or self._owner.getsession(session.peer) == session:
            session.send(Error(stanza, ERR_SERVICE_UNAVAILABLE))
        else:
            session.set_session_state(SESSION_OPENED)
            session.send(stanza.buildReply('result'))
        raise NodeProcessed


class Handshake(PlugIn):
    NS = NS_COMPONENT_ACCEPT

    def namespaceChangerAndRedirector(self, session, stanza):
        if stanza.getName() == "handshake":
            self.handshakeHandler(session, stanza)
        if stanza.getName() in ['message', 'iq']:
            self.DEBUG("Redirecting stanza %s to router" % (stanza), "info")
            stanza.setNamespace(NS_CLIENT)
            self.server.Router.routerHandler(session, stanza)
        elif stanza.getName() == "presence":
            self.DEBUG("Redirecting stanza %s to router" % (stanza), "info")
            stanza.setNamespace(NS_CLIENT)
            self.server.Router.presenceHandler(session, stanza)
        return

    def plugin(self, server):
        self.server = server
        server.Dispatcher.RegisterNamespaceHandler(NS_COMPONENT_ACCEPT, self.namespaceChangerAndRedirector)
        #server.Dispatcher.RegisterHandler('handshake',self.handshakeHandler,xmlns=NS_COMPONENT_ACCEPT)
        #server.Dispatcher.RegisterHandler('presence',self.namespaceChangerAndRedirector,xmlns=NS_COMPONENT_ACCEPT)
        #server.Dispatcher.RegisterHandler('message',self.namespaceChangerAndRedirector,xmlns=NS_COMPONENT_ACCEPT)
        #server.Dispatcher.RegisterHandler('iq',self.namespaceChangerAndRedirector,xmlns=NS_COMPONENT_ACCEPT)

    def handshakeHandler(self, session, stanza):
        self.DEBUG('Handshake handler called', 'info')
        if session._session_state >= SESSION_AUTHED:
            session.terminate_stream(STREAM_NOT_AUTHORIZED)
            self.DEBUG('Session already authed', 'warn')
            return

        handshake = str(stanza.getData())
        for k, v in self.server.components.items():
            try:
                truehs = hashlib.sha1(str(session.ID) + v['password']).hexdigest()
                if handshake == truehs:
                    # We have a match!! It's THIS component!!
                    session.peer = v['jid'].lower()
                    self.server.activatesession(session, v['jid'])
                    session.set_session_state(SESSION_AUTHED)
                    session.set_session_state(SESSION_OPENED)
                    node, dom = v["jid"].split(".", 1)
                    self.server.DB.register_user(dom, node, v['password'], v['name'])
                    session.send(Node('handshake'))
                    self.DEBUG('Component %s authenticated' % (v['jid']), 'ok')
                    return
            except:
                self.DEBUG('Error authenticating handshake', 'error')
        self.DEBUG("Unknown component", "warn")
        self.DEBUG("Components: " + str(self.server.components), "warn")
        return
