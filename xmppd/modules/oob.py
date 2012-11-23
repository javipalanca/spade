# -*- coding: utf-8 -*-

from xmpp import *


class OOB(PlugIn):
    NS = "jabber:iq:oob"

    def plugin(self, server):
        server.Dispatcher.RegisterHandler('iq', self.OOBIqHandler, typ='set', ns="jabber:iq:oob", xmlns=NS_CLIENT)
        server.Dispatcher.RegisterHandler('iq', self.OOBIqHandler, typ='result', ns="jabber:iq:oob", xmlns=NS_CLIENT)
        server.Dispatcher.RegisterHandler('iq', self.OOBIqHandler, typ='error', ns="jabber:iq:oob", xmlns=NS_CLIENT)

    def OOBIqHandler(self, session, stanza):
        self.DEBUG("OOB Iq handler called", "info")
        s = self._owner.getsession(str(stanza['to']))
        if s:
            # Relay stanza
            s.enqueue(stanza)
            self.DEBUG("OOB stanza relayed from %s to %s" % (str(session.peer), str(stanza['to'])), "info")
        raise NodeProcessed
