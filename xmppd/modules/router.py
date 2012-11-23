# -*- coding: utf-8 -*-
# Distributed under the terms of GPL version 2 or any later
# Copyright (C) Alexey Nezhdanov 2004
# Copyright (C) Kristopher Tate / BlueBridge Technologies Group 2005
# Copyright (C) Javier Palanca & Gustavo Aranda/ Computer Technology Group 2006
# router, presence tracker and probes responder for xmppd.py


import copy
from xmpp import *
from xmppd import *
#try: from xmppd import xmppd
#except: pass

# XMPP-session flags
# From the server
SESSION_NOT_AUTHED = 1
SESSION_AUTHED = 2
SESSION_BOUND = 3
SESSION_OPENED = 4


class Router(PlugIn):
    """ The first entity that gets access to arrived stanza. """
    NS = 'presence'

    def plugin(self, server):
        self._data = {}
        server.Dispatcher.RegisterHandler('presence', self.presenceHandler, xmlns=NS_CLIENT)
        server.Dispatcher.RegisterHandler('presence', self.presenceHandler, xmlns=NS_SERVER)
        #server.Dispatcher.RegisterNamespaceHandler(NS_CLIENT,self.routerHandler)
        server.Dispatcher.RegisterHandler('message', self.routerHandler, xmlns=NS_CLIENT)
        server.Dispatcher.RegisterHandler('message', self.routerHandler, xmlns=NS_SERVER)
        #server.Dispatcher.RegisterHandler('iq',self.routerHandler,xmlns=NS_SERVER)
        server.Dispatcher.RegisterHandler('iq', self.routerHandler, xmlns=NS_CLIENT)
        server.Dispatcher.RegisterHandler('iq', self.routerHandler, ns=NS_DISCO_INFO, xmlns=NS_CLIENT)
        server.Dispatcher.RegisterHandler('iq', self.routerHandler, ns=NS_DISCO_INFO, xmlns=NS_SERVER)
        server.Dispatcher.RegisterHandler('iq', self.routerHandler, ns=NS_DISCO_ITEMS, xmlns=NS_CLIENT)
        server.Dispatcher.RegisterHandler('iq', self.routerHandler, ns=NS_DISCO_ITEMS, xmlns=NS_SERVER)
        # MUC namespaces
        server.Dispatcher.RegisterHandler('iq', self.routerHandler, ns='http://jabber.org/protocol/muc')
        server.Dispatcher.RegisterHandler('iq', self.routerHandler, ns='http://jabber.org/protocol/muc#user')
        server.Dispatcher.RegisterHandler('iq', self.routerHandler, ns='http://jabber.org/protocol/muc#admin')
        server.Dispatcher.RegisterHandler('iq', self.routerHandler, ns='http://jabber.org/protocol/muc#owner')
        server.Dispatcher.RegisterHandler('iq', self.routerHandler, ns="http://jabber.org/protocol/muc#roominfo")
        server.Dispatcher.RegisterHandler('iq', self.routerHandler, ns="http://jabber.org/protocol/muc#traffic")
        server.Dispatcher.RegisterHandler('iq', self.routerHandler, ns="http://jabber.org/protocol/muc#roomconfig")
        server.Dispatcher.RegisterHandler('iq', self.routerHandler, ns="http://jabber.org/protocol/muc#register")
        # Stream Initiation
        server.Dispatcher.RegisterHandler('iq', self.routerHandler, ns='http://jabber.org/protocol/si')

        server.Dispatcher.RegisterNamespaceHandler(NS_SERVER, self.routerHandler)

    def isFromOutside(self, domain):
        for servername in self._owner.servernames:
            if str(domain).endswith(servername):
                return False
        return True

    def pluginRelay(self, session, stanza):
        """
        Relays a stanza to a plugin dispatcher if such plugin is the correct receiver of the stanza
        """

        to = stanza['to']
        if not to:
            return False
        for k, p in self._owner.plugins.items():
            if 'jid' in p.keys() and p['jid'] == to.getDomain():
                try:
                    self.DEBUG("Dispatching stanza to %s plugin" % (k), "info")
                    exec("self._owner." + k + ".dispatch(session,stanza)")
                except:
                    self.DEBUG("Could not dispatch stanza to plugin " + k, "error")
                    return False
                return True
        return False

    def presenceHandler(self, session, stanza, raiseFlag=True, fromLocal=False):
        self.DEBUG('Presence handler called (%s::%s)' % (session.peer, str(stanza.getType())), 'info')
        #filter out presences that should not influate our 'roster'
        #This is presences, that's addressed:
        #1) any other server
        #2) any user
        to = stanza['to']
        internal = stanza.getAttr('internal')
        fromOutside = False
        #<presence to="test3@172.16.0.2" from="test2@172.16.1.34/Adium" type="probe" />

        #component_jids = []
        #for v in self._owner.components.values():
        #    if v.has_key('jid'):
        #        component_jids.append(v['jid'])

        if self.pluginRelay(session, stanza) and raiseFlag:
            raise NodeProcessed

        if to and self.isFromOutside(to.getDomain()) and internal != 'True':
            #self.DEBUG("Presence stanza has an invalid recipient","warn")
            #return
            self.DEBUG("Presence stanza has an external or component receiver: %s" % (to.getDomain()), "warn")

        typ = stanza.getType()
        jid = session.peer  # 172.16.1.34
        if not jid:
            raise NodeProcessed
        fromOutside = False
        try:
            barejid = ""
            #barejid,resource=jid.split('/')
            #jlist =str(jid).split('/')
            #if len(jlist) > 0: barejid  = jlist[0]
            #if len(jlist) > 1: resource = jlist[1]
            barejid = JID(jid).getStripped()
            resource = JID(jid).getResource()
            domain = JID(jid).getDomain()
            supposed_from = stanza.getFrom()
            if (barejid and supposed_from) and (barejid == supposed_from.getDomain()):
                barejid = str(supposed_from)

            fromOutside = self.isFromOutside(JID(barejid).getDomain())

            """
            if not JID(barejid).getDomain() in self._owner.servernames:
                self.DEBUG("Presence from Outside","info")
                fromOutside = True
            """

            self.DEBUG("The real from seems to be " + barejid, "info")
        except:
            #self.DEBUG('Presence: Could not set barejid from jid: %s, fromOutside=True'%(str(jid)),'error')
            self.DEBUG('Presence: Could not set barejid from jid: %s' % (str(jid)), 'error')

        """
        if fromOutside == True:
            if typ in ['subscribe','subscribed','unsubscribe','unsubscribed']:
                self.DEBUG("Redirecting stanza to subscriber", "warn")
                self.subscriber(session,stanza)
            else:
                # Find each session
                s = None
            # If it's our server
            if to.getDomain() in self._owner.servernames:
                s = self._owner.getsession(str(to))
                if s == None:
                    # TODO: Store if it's real user
                    self.DEBUG("Could not find session for "+str(to),"error")
                    return
                # Enqueue the message to the receiver
                self.DEBUG("Redirecting stanza to receiver", "info")
                p = Presence(to=s.peer,frm=stanza.getFrom(),typ=stanza.getType())


                for child in stanza.getChildren():
                    if child.getName() == 'status' or child.getName() == 'Status':
                        p.setStatus(child.getData())
                    elif child.getName() == 'show' or child.getName() == 'Show':
                        p.setShow(child.getData())
                    elif child.getName() == 'priority' or child.getName() == 'Priority':
                        p.setPriority(child.getData())

                s.enqueue(p)
                raise NodeProcessed
            else:
                self.DEBUG("Stupid situation: from and to are outsiders. WTF?","error")
                return
        """

        if not typ or typ == 'available':  # and fromOutside == False:
            if fromOutside:
                # Find each session
                s = None
                s = self._owner.getsession(str(to))
                if s is None:
                    # TODO: Store if it's real user
                    self.DEBUG("Could not find session for " + str(to), "warn")
                    return
                stanza.setNamespace(NS_CLIENT)
                s.enqueue(stanza)
                raise NodeProcessed

            else:

                if barejid not in self._data.keys():
                    self._data[barejid] = {}
                if resource not in self._data[barejid].keys():
                    self._data[barejid][resource] = Presence(frm=jid, typ=typ)
                bp = self._data[barejid][resource]

                try:
                    priority = int(stanza.getTagData('priority'))
                except:
                    priority = 0
                bp.T.priority = str(priority)
                self._owner.activatesession(session)

                show = stanza.getTag('show')
                if show:
                    bp.T.show = show
                else:
                    bp.T.show = ''
                status = stanza.getTag('status')
                if status:
                    bp.T.status = status
                else:
                    bp.T.status = ''
                for x in bp.getTags('x', namespace='jabber:x:delay'):
                    bp.delChild(x)
                bp.setTimestamp()
                self.update(barejid)

                self.DEBUG("available presence " + str(bp), 'info')

                self.broadcastAvailable(session)  # Pass onto broadcaster!

            if self._owner._socker is not None:
                self._owner._socker.add_data_root({'jid': {barejid: self._data[barejid].keys()}})
                self._owner._socker.add_data({'jid': {barejid: self._data[barejid].keys()}})

        elif (typ == 'unavailable' or typ == 'error'):  # and fromOutside == False:

            if not fromOutside:
                jid_info = self._owner.tool_split_jid(barejid)
                contacts = session.getRoster()
                for k, v in contacts.iteritems():
                    if v['subscription'] in ['from', 'both']:
                        self.DEBUG('Un-Presence attempt for contact "%s":' % k, 'warn')
                        p = Presence(to=k, frm=session.peer, typ='unavailable')
                        status = stanza.getTag('status')
                        if status:
                            p.T.show = status
                        else:
                            p.T.show = 'Logged Out'
                        #self._owner.Dispatcher.dispatch(p,session)

                        k_jid = JID(k)
                        # Find each session
                        s = None
                        # If it's our server
                        if k_jid.getDomain() in self._owner.servernames or k in self._owner.servernames:
                            s = self._owner.getsession(k)
                            if s is None:
                                # TODO: Store
                                pass
                        else:
                            s = self._owner.S2S(session.ourname, k_jid.getDomain())

                        # Send the presence
                        if s is not None:
                            s.enqueue(p)
                        else:
                            self.DEBUG('Could not find active session for contact %s' % (k), 'warn')

            else:
                # Find each session
                s = None
                s = self._owner.getsession(str(to))
                if s is None:
                # TODO: Store if it's real user
                    self.DEBUG("Could not find session for " + str(to), "warn")
                    return
                stanza.setNamespace(NS_CLIENT)
                s.enqueue(stanza)
                raise NodeProcessed

            self.DEBUG('Finished for "%s"' % k, 'info')

            if self._owner._socker is not None:
                self._owner._socker.remove_data_root(['jid', barejid])
                self._owner._socker.remove_data(['jid', barejid])

            if barejid not in self._data.keys() and raiseFlag is True:
                raise NodeProcessed
            #if self._data[barejid].has_key(resource): del self._data[barejid][resource]
            #self.update(barejid)
            #if not self._data[barejid]: del self._data[barejid]
            #self._owner.deactivatesession(session.peer)

        elif typ == 'invisible' and fromOutside is False:

            jid_info = self._owner.tool_split_jid(barejid)
            contacts = session.getRoster()
            for k, v in contacts.iteritems():
                self.DEBUG('Un-Presence attempt for contact [INVISIBLE!!!]"%s":' % k, 'warn')
                p = Presence(to=k, frm=session.peer, typ='unavailable')
                status = stanza.getTag('status')
                if status:
                    p.T.show = status
                else:
                    p.T.show = 'Logged Out'
                session.dispatch(p)
                self.DEBUG('Finished for "%s" [INVISIBLE!!!]' % k, 'info')

        elif typ == 'probe':
            self.DEBUG('Probe activated!', 'info')
            if stanza.getTo() in self._owner.servernames:
                session.enqueue(Presence(to=stanza.getFrom(), frm=stanza.getTo()))
                raise NodeProcessed
            if stanza.getAttr('internal') == 'True':
                self.DEBUG('Internal Probe activated!', 'info')
                try:
                    resources = [stanza.getTo().getResource()]
                    if not resources[0]:
                        resources = self._data[stanza.getTo()].keys()
                    flag = 1
                    for resource in resources:
                        p = Presence(to=stanza.getFrom(), frm='%s/%s' % (stanza.getTo(), resource), node=self._data[stanza.getTo()][resource])
                        if flag:
                        #self._owner.Privacy(session,p)  # Desactivado de momento
                            flag = None
                        session.enqueue(p)
                except KeyError:
                    pass  # Wanted session is not active! #session.enqueue(Presence(to=stanza.getTo(),frm=jid,typ='unavailable'))
            else:
                if not self.isFromOutside(stanza.getTo().getDomain()):
                        #TODO: test if contact is authorized to know its presence
                    bareto = stanza.getTo().getStripped()
                    #resourceto = stanza.getTo().getResource()
                    if bareto in self._data.keys():
                        #if self._data[bareto].has_key(resourceto):
                        for resourceto in self._data[bareto].keys():
                            p = copy.copy(self._data[bareto][resourceto])
                            p.setTo(barejid)
                            s = None
                            if not fromOutside:
                                s = self._owner.getsession(barejid)
                            else:
                                s = self._owner.S2S(session.ourname, domain)
                            if s:
                                s.enqueue(p)
                                self.DEBUG('Probe ' + str(p) + ' sent', 'info')
                                raise NodeProcessed
                    session.enqueue(Presence(to=stanza.getFrom(), frm=stanza.getTo(), typ='unavailable'))
                    self.DEBUG('Probe "unavailable" sent', 'info')
                    raise NodeProcessed
                else:
                    self.DEBUG("Probe message ignored", 'warn')

        elif typ in ['subscribe', 'subscribed', 'unsubscribe', 'unsubscribed']:
            self.DEBUG("Redirecting stanza to subscriber", "warn")
            self.subscriber(session, stanza)

        else:
            self.DEBUG('Woah, nothing to call???', 'warn')
            if raiseFlag:
                raise NodeProcessed

    def broadcastAvailable(self, session, to=None):
        try:
            #barejid,resource=session.peer.split('/')
            barejid = JID(session.peer).getStripped()
            resource = JID(session.peer).getResource()
        except:
            fromOutside = True
            self.DEBUG('Presence: Could not set barejid, fromOutside=True', 'warn')

        contacts = session.getRoster()
        if contacts is None:
            return

        #print "MY CONTACTS: "+ str(contacts)

        #for x,y in contacts.iteritems():
        for x, y in contacts.items():
            #x_split = self._owner.tool_split_jid(x)
            j = JID(x)
            name = j.getNode()
            domain = j.getDomain()
            self.DEBUG('Presence attempt for contact "%s":' % x, 'warn')
            #print str(y['subscription'])
            try:
                if y['subscription'] in ['from', 'both']:
                    #if x_split[1] not in self._owner.servernames \
                    #or self._owner.DB.pull_roster(x_split[1],x_split[0],barejid) != None:
                    if self.isFromOutside(domain) \
                            or self._owner.DB.pull_roster(domain, name, barejid) is not None:
                        if (x in self._owner.servernames):
                            self.DEBUG("Contact %s is the server. returning" % (str(x)), 'warn')
                            return
                        self.DEBUG('Contact "%s" has from/both' % x, 'warn')
                        ###session.dispatch(Presence(to=x,frm=session.peer,node=self._data[barejid][session.getResource()]))

                        # Find each session
                        s = None
                        # If it's our server
                        #if x_split[1] in self._owner.servernames or x in self._owner.servernames:
                        pres = Presence(to=x, frm=session.peer, node=self._data[barejid][session.getResource()])
                        if not self.isFromOutside(domain) or x in self._owner.servernames:
                            s = self._owner.getsession(x)
                            if s is None:
                            # TODO: Store
                                pass
                        else:
                            #s=self._owner.S2S(session.ourname,x_split[1])
                            s = self._owner.S2S(session.ourname, domain)
                            #pres.setNamespace(NS_SERVER)

                        # Send the presence
                        if s is not None:
                            s.enqueue(pres)
                            self.DEBUG('Finished for "%s" (from/both)' % x, 'info')

                if y['subscription'] in ['to', 'both']:
                        #if (x_split == None and x in self._owner.servernames) \
                        #or x_split[1] not in self._owner.servernames          \
                        #or self._owner.DB.pull_roster(x_split[1],x_split[0],barejid) != None:
                    if (x in self._owner.servernames) \
                        or self.isFromOutside(domain) \
                            or self._owner.DB.pull_roster(domain, name, barejid) is not None:
                        self.DEBUG('Contact "%s" has to/both' % x, 'warn')
                        #p = Presence(to=x,frm=session.peer,typ='probe')
                        #p.setAttr('type','probe')
                        #session.dispatch(p)
                        if str(x) in self._data.keys():
                            # Send the presence information of this client
                            for res in self._data[str(x)].keys():
                                session.enqueue(self._data[x][res])
                        elif x in self._owner.servernames or str(x) in self._owner.servernames:
                            # Generate an 'available' presence on our behalf (the server is always available)
                            session.enqueue(Presence(to=session.peer, frm=str(x), typ='available'))
                        elif self.isFromOutside(domain):
                            s = self._owner.S2S(session.ourname, domain)
                            if s:
                                s.enqueue(Presence(to=x, frm=session.peer, typ='probe'))
                        else:
                            # Generate an 'unavailable' presence on behalf of this client
                            session.enqueue(Presence(to=session.peer, frm=str(x), typ='unavailable'))

                        self.DEBUG('Finished for "%s" (to/both)' % x, 'info')

            except Exception, err:
                self.DEBUG("PRESENCE_BROADCAST_ERR: %s\nx:%s\ny:%s" % (err, x, y), 'error')

    def update(self, barejid):
        self.DEBUG("Router update", "info")
        pri = -1
        s = None
        for resource in self._data[barejid].keys():
            rpri = int(self._data[barejid][resource].getTagData('priority'))
            if rpri > pri:
                s = self._owner.getsession(barejid + '/' + resource)
        if s:
            self._owner.activatesession(s, barejid)
        else:
            self._owner.deactivatesession(barejid)

    def safeguard(self, session, stanza):
        if stanza.getNamespace() not in [NS_CLIENT, NS_SERVER]:
            return  # this is not XMPP stanza

        if session._session_state < SESSION_AUTHED:  # NOT AUTHED yet (stream's stuff already done)
            session.terminate_stream(STREAM_NOT_AUTHORIZED)
            raise NodeProcessed

        frm = stanza['from']
        to = stanza['to']
        if stanza.getNamespace() == NS_SERVER:
            if not frm or not to \
                or frm.getDomain() != session.peer \
                    or to.getDomain() != session.ourname:
                session.terminate_stream(STREAM_IMPROPER_ADDRESSING)
                raise NodeProcessed
        else:
            if frm and frm != session.peer:   # if the from address specified and differs
                if frm.getResource() or not frm.bareMatch(session.peer):  # ...it can differ only while comparing inequally
                    session.terminate_stream(STREAM_INVALID_FROM)
                    raise NodeProcessed

            if session._session_state < SESSION_BOUND:  # NOT BOUND yet (bind stuff already done)
                if stanza.getType() != 'error':
                    session.send(Error(stanza, ERR_NOT_AUTHORIZED))
                raise NodeProcessed

            if name == 'presence' and session._session_state < SESSION_OPENED:
                if stanza.getType() != 'error':
                    session.send(Error(stanza, ERR_NOT_ALLOWED))
                raise NodeProcessed
            stanza.setFrom(session.peer)

    def subscriber(self, session, stanza):
        """
        Subscription manager that actually works (cough, cough, BoP, cough, cough ;-)

        0. COMMON TASKS
            0.1 Get 'from' and 'to'
            0.2 Get the session of the receiver
        """

        try:
            supposed_from = JID(session.peer)
            if supposed_from.getNode() == '':  # and supposed_from.getDomain() not in self._owner.servernames:
                fromOutside = self.isFromOutside(JID(supposed_from).getDomain())
                if fromOutside:
                    frm = str(stanza.getFrom())
                else:
                    frm = str(JID(session.peer).getStripped())
            else:
                frm = str(JID(session.peer).getStripped())
                fromOutside = False
            #print "### JID FOUND = %s"%(str(frm))
        except:
            self.DEBUG('Could not state real from', 'error')
            raise NodeProcessed

        to = stanza['to']
        session_jid = [to.getNode(), to.getDomain()]
        jfrom_node = JID(session.peer).getNode()
        jfrom_domain = JID(session.peer).getDomain()

        # Construct correct bareto
        if session_jid[0] == '':
            bareto = session_jid[1]     # OMG it's a component!
        else:
            bareto = session_jid[0] + '@' + session_jid[1]  # It's a regular client

        # 0.2 Get the session of the receiver
        s = None
        s = self._owner.getsession(bareto)
        if s is None:
            if self.isFromOutside(to.getDomain()):
                s = self._owner.S2S(session.ourname, to.getDomain())

            if s is None:
                self.DEBUG("DANGER! There is still no session for the receiver", "error")
                # There was no session for the receiver
                # TODO: Store the stanza and relay it later
                raise NodeProcessed

        if not fromOutside:
            contact = self._owner.DB.pull_roster(str(jfrom_domain), str(jfrom_node), str(bareto))
            #print "### CONTACT: " + str(contact)
        else:
            contact = None

        # Inbound-Outbound Shit
        if not self.isFromOutside(to.getDomain()):
            inbound = True
            inbound_contact = self._owner.DB.pull_roster(to.getDomain(), to.getNode(), frm)
            self.DEBUG("Inbound Contact: %s : %s" % (bareto, str(inbound_contact)), "warn")
        else:
            inbound = False

        if not self.isFromOutside(jfrom_domain):
            outbound = True
            outbound_contact = self._owner.DB.pull_roster(str(jfrom_domain), str(jfrom_node), str(bareto))
            self.DEBUG("Outbound Contact: %s : %s" % (frm, str(outbound_contact)), "warn")
        else:
            outbound = False

        if stanza.getType() == "subscribe":
            #print "### IT'S SUBSCRIBE"
            pass
            """
            1. SUBSCRIBE
                1.2 Modify and push the sender's roster
                1.3 Relay the presence stanza to the receiver
                1.4 Do the victory dance and raise NodeProcessed
            """

            """
            self.DEBUG("Checking if contact is already subscribed","info")
            try:
                if contact and contact['subscription'] in ['both', 'to']:
                    # We're ALREADY subscribed, we should dismiss this request to prevent
                    # infinite loops of presence stanzas
                    print "### CONTACT ALREADY SUBSCRIBED"
                    raise NodeProcessed
            except KeyError:
                # This contact wasn't in the roster or the subscription wasn't done
                self.DEBUG("This contact wasn't in the roster or the subscription wasn't done","warn")
            except AttributeError:
                self.DEBUG("The subscription wasn't done","warn")
            """

            #self.DEBUG("Contact is not subscribed yet. jfrom = %s %s"%(str(jfrom_node),str(jfrom_domain)),"info")
            # 1.2 Modify and push the sender's roster (if it's a client of this server)
            #if str(jfrom_domain) in self._owner.servernames:
            route = False
            if inbound:

                """
                if contact and not fromOutside:
                    # Add 'ask' key to the roster
                    contact.update({'ask':'subscribe'})
                    self._owner.DB.save_to_roster(jfrom_domain, jfrom_node, bareto, contact)
                elif not fromOutside:
                """

                # Create roster for this contact
                #print "### JFROM = %s %s  ;  BARETO = %s"%(jfrom_node, jfrom_node, bareto)
                # F?CKING inbound-outbound control schema
                if inbound_contact and 'subscription' in inbound_contact.keys():
                    subs = inbound_contact['subscription']
                else:
                    subs = "none"
                if inbound_contact and 'state' in inbound_contact.keys():
                    state = inbound_contact['state']
                else:
                    state = ""

                #print "subs",subs,state,route

                route = True
                if   subs == "none" and not state:
                    state = "pending_in"
                elif subs == "none" and state == "pending_out":
                    state = "pending_out_in"
                elif subs == "to" and not state:
                    state = "pending_in"
                else:
                    route = False

                #print "subs",subs,state,route

                if subs in ['from', 'both']:
                    session.enqueue(Presence(frm=bareto, typ='subscribed', to=frm))  # Auto-Reply
                    raise NodeProcessed

                try:
                    if not inbound_contact:
                        inbound_contact = {}
                    inbound_contact.update({'subscription': subs})
                    inbound_contact.update({'state': state})
                    self._owner.DB.save_to_roster(to.getDomain(), to.getNode(), frm, inbound_contact)

                    self._owner.ROSTER.RosterPushOneToClient(contact=frm, to=bareto, to_session=s)
                    #print "route: ",route,outbound

                except:
                    self.DEBUG("Could not create roster for client " + str(bareto), 'error')

            if outbound:
                try:
                    # F?CKING inbound-outbound control schema
                    if outbound_contact and 'subscription' in outbound_contact.keys():
                        subs = outbound_contact['subscription']
                    else:
                        subs = "none"
                    if outbound_contact and 'state' in outbound_contact.keys():
                        state = outbound_contact['state']
                    else:
                        state = ""

                    if   subs == "none" and not state:
                        state = "pending_out"
                    elif subs == "none" and state == "pending_in":
                        state = "pending_out_in"
                    elif subs == "from" and not state:
                        state = "pending_out"

                    if not outbound_contact:
                        outbound_contact = {}
                    outbound_contact.update({'subscription': subs})
                    outbound_contact.update({'state': state})
                    if not subs or subs == "none":
                        outbound_contact.update({'ask': 'subscribe'})
                    self._owner.DB.save_to_roster(jfrom_domain, jfrom_node, bareto, outbound_contact)

                    self._owner.ROSTER.RosterPushOneToClient(contact=bareto, to=frm, to_session=session)

                except:
                    self.DEBUG("Could not create roster for client " + str(frm), 'error')

            # 1.3 Relay the presence stanza to the receiver
            if outbound or route:
                self.DEBUG("Routing stanza to receiver: " + str(bareto), "info")
                stanza.setFrom(frm)
                stanza.setNamespace(NS_CLIENT)
                s.enqueue(stanza)

            # 1.4 Do the victory dance
            #   o
            #  \|/
            #   A
            #  / \
            raise NodeProcessed

        elif stanza.getType() == "subscribed":
            #print "### IT'S SUBSCRIBED"
            """
            2. SUBSCRIBED
                2.1 Relay the presence stanza to the receiver
                2.2 Modify and push the receiver's roster
                    2.2.2 Modify and push the sender's roster ??
                2.3 Send a presence probe on behalf of the sender
            """
            route = False
            if inbound:
                #print "### JFROM = %s %s  ;  BARETO = %s"%(jfrom_node, jfrom_node, bareto)
                try:
                    # F?CKING inbound-outbound control schema
                    if inbound_contact and 'subscription' in inbound_contact.keys():
                        subs = inbound_contact['subscription']
                    else:
                        subs = "none"
                    if inbound_contact and 'state' in inbound_contact.keys():
                        state = inbound_contact['state']
                    else:
                        state = ""

                    route = True
                    if subs == "none" and state == "pending_out":
                        subs = "to"
                        state = ""
                    elif subs == "none" and state == "pending_out_in":
                        subs = "to"
                        state = "pending_in"
                    elif subs == "from" and state == "pending_out":
                        subs = "both"
                        state = ""
                    elif subs == "from" and not state:
                        subs = "both"  # this is not standard
                    else:
                        route = False

                    if not inbound_contact:
                        inbound_contact = {}
                    inbound_contact.update({'subscription': subs})
                    inbound_contact.update({'state': state})
                    if 'ask' in inbound_contact.keys():
                        del inbound_contact['ask']
                    self._owner.DB.save_to_roster(to.getDomain(), to.getNode(), frm, inbound_contact)

                    #self._owner.ROSTER.RosterPushOne(session,stanza)
                    self._owner.ROSTER.RosterPushOneToClient(contact=frm, to=bareto, to_session=s)

                except:
                    self.DEBUG("Could not create roster for client " + str(bareto), 'error')

            if outbound:
                try:
                    # F?CKING inbound-outbound control schema
                    if outbound_contact and 'subscription' in outbound_contact.keys():
                        subs = outbound_contact['subscription']
                    else:
                        subs = None
                    if outbound_contact and 'state' in outbound_contact.keys():
                        state = outbound_contact['state']
                    else:
                        state = None

                    if subs == "none" and state == "pending_in":
                        subs = "from"
                        state = ""
                        route = True
                    elif subs == "none" and state == "pending_out_in":
                        subs = "from"
                        state = "pending_out"
                        route = True
                    elif subs == "to" and state == "pending_in":
                        subs = "both"
                        state = ""
                        route = True

                    if not outbound_contact:
                        outbound_contact = {}
                    outbound_contact.update({'subscription': subs})
                    outbound_contact.update({'state': state})
                    self._owner.DB.save_to_roster(jfrom_domain, jfrom_node, bareto, outbound_contact)

                    #self._owner.ROSTER.RosterPushOne(session,stanza)
                    self._owner.ROSTER.RosterPushOneToClient(contact=bareto, to=frm, to_session=session)

                except:
                    self.DEBUG("Could not create roster for client " + str(frm), 'error')

            if route:
                stanza.setFrom(frm)
                stanza.setNamespace(NS_CLIENT)
                s.enqueue(stanza)
                self.DEBUG("Subscribed-stanza relied to proper client", "ok")

            # 2.3 Send an available presence probe on behalf of the one who allows subscription
            try:
                barefrom = JID(frm).getStripped()
                if barefrom in self._data.keys():
                    for pres in self._data[barefrom].values():
                        pres_c = copy.copy(pres)
                        pres_c.setType('available')
                        pres_c.setTo(bareto)
                        s.enqueue(pres_c)
            except Exception, e:
                print "### EXCEPTION " + str(e)

            #print "### PRESENCE STANZA ON BEHALF OF " + barefrom
            #self._owner.DB.print_database()

            raise NodeProcessed

        elif stanza.getType() == "unsubscribe":
            #print "### IT'S UNSUBSCRIBE"
            """
            3. UNSUBSCRIBE
                3.1 Check if the contact is already subscribed
                3.2 Modify and push the sender's roster
                3.3 Relay the presence stanza to the receiver
                3.4 Send the sender (wow) an 'unsubscribed' presence probe on behalf of the receiver
                3.5 Send the sender (wowwow) probes of 'unavailable' on behalf of the receiver
            """

            route = False
            if inbound:

                #print "### JFROM = %s %s  ;  BARETO = %s"%(jfrom_node, jfrom_node, bareto)
                try:
                    # F?CKING inbound-outbound control schema
                    if inbound_contact and 'subscription' in inbound_contact.keys():
                        subs = inbound_contact['subscription']
                    else:
                        subs = "none"
                    if inbound_contact and 'state' in inbound_contact.keys():
                        state = inbound_contact['state']
                    else:
                        state = ""

                    if   subs == "none" and state == "pending_in":
                        state = ""
                        route = True
                    elif subs == "none" and state == "pending_out_in":
                        state = "pending_out"
                        route = True
                    elif   subs == "to" and state == "pending_in":
                        state = ""
                        route = True
                    elif   subs == "from" and not state:
                        subs = "none"
                        route = True
                    elif   subs == "from" and state == "pending_out":
                        subs = "none"
                        route = True
                    elif   subs == "both" and not state:
                        subs = "to"
                        route = True

                    if not inbound_contact:
                        inbound_contact = {}
                    inbound_contact.update({'subscription': subs})
                    inbound_contact.update({'state': state})
                    self._owner.DB.save_to_roster(to.getDomain(), to.getNode(), frm, inbound_contact)

                    self._owner.ROSTER.RosterPushOneToClient(contact=frm, to=bareto, to_session=s)

                except:
                    self.DEBUG("Could not create roster for client " + str(bareto), 'error')

            if outbound:
                try:
                    # F?CKING inbound-outbound control schema
                    if outbound_contact and 'subscription' in outbound_contact.keys():
                        subs = outbound_contact['subscription']
                    else:
                        subs = "none"
                    if outbound_contact and 'state' in outbound_contact.keys():
                        state = outbound_contact['state']
                    else:
                        state = ""

                    if    subs == "none" and state == "pending_out":
                        state = ""  # ; route = True
                    elif  subs == "none" and state == "pending_out_in":
                        state = "pending_in"  # ; route = True
                    elif  subs == "to" and not state:
                        subs = "none"  # ; route = True
                    elif  subs == "to" and state == "pending_in":
                        subs = "none"  # ; route = True
                    elif  subs == "from" and state == "pending_out":
                        state = ""  # ; route = True
                    elif  subs == "both" and not state:
                        subs = "from"  # ; route = True

                    if not outbound_contact:
                        outbound_contact = {}
                    outbound_contact.update({'subscription': subs})
                    outbound_contact.update({'state': state})
                    self._owner.DB.save_to_roster(jfrom_domain, jfrom_node, bareto, outbound_contact)

                    self._owner.ROSTER.RosterPushOneToClient(contact=bareto, to=frm, to_session=session)

                except:
                    self.DEBUG("Could not create roster for client " + str(frm), 'error')

            # 1.3 Relay the presence stanza to the receiver
            if outbound or route:
                stanza.setFrom(frm)
                stanza.setNamespace(NS_CLIENT)
                s.enqueue(stanza)
                if route:
                    session.enqueue(Presence(to=frm, frm=bareto, typ="unsubscribed"))

            raise NodeProcessed

            # 3.5 Send the sender (wowwow) probes of 'unavailable' on behalf of the receiver
            """
            for pres in self._data[bareto].values():
                p = copy.copy(pres)
                p.setType('unavailable')
                p.setTo(frm)
                session.enqueue(p)
            """

            raise NodeProcessed

        elif stanza.getType() == "unsubscribed":
            pass
            #print "### IT'S UNSUBSCRIBED"
            """
            4. UNSUBSCRIBED
                4.1 Relay the presence stanza to the receiver
                4.2 Modify and push the receiver and sender rosters
            """

            route = False
            if inbound:
                #print "### JFROM = %s %s  ;  BARETO = %s"%(jfrom_node, jfrom_node, bareto)
                try:
                    # F?CKING inbound-outbound control schema
                    if inbound_contact and 'subscription' in inbound_contact.keys():
                        subs = inbound_contact['subscription']
                    else:
                        subs = "none"
                    if inbound_contact and 'state' in inbound_contact.keys():
                        state = inbound_contact['state']
                    else:
                        state = ""

                    if subs == "none" and state == "pending_out":
                        subs = "none"
                        state = ""
                        route = True
                    elif subs == "none" and state == "pending_out_in":
                        subs = "none"
                        state = "pending_in"
                        route = True
                    elif subs == "to" and not state:
                        subs = "none"
                        route = True
                    elif subs == "to" and state == "pending_in":
                        subs = "none"
                        route = True
                    elif subs == "from" and state == "pending_out":
                        subs = "from"
                        route = True
                    elif subs == "both" and not state:
                        subs = "from"
                        route = True

                    if not inbound_contact:
                        inbound_contact = {}
                    inbound_contact.update({'subscription': subs})
                    inbound_contact.update({'state': state})
                    self._owner.DB.save_to_roster(to.getDomain(), to.getNode(), frm, inbound_contact)

                    #self._owner.ROSTER.RosterPushOne(session,stanza)
                    self._owner.ROSTER.RosterPushOneToClient(contact=frm, to=bareto, to_session=s)

                except:
                    self.DEBUG("Could not create roster for client " + str(bareto), 'error')

            if outbound:
                try:
                    # F?CKING inbound-outbound control schema
                    if outbound_contact and 'subscription' in outbound_contact.keys():
                        subs = outbound_contact['subscription']
                    else:
                        subs = "none"
                    if outbound_contact and 'state' in outbound_contact.keys():
                        state = outbound_contact['state']
                    else:
                        state = ""

                    if subs == "none" and state == "pending_in":
                        state = ""
                        route = True
                    elif subs == "none" and state == "pending_out_in":
                        state = "pending_out"
                        route = True
                    elif subs == "to" and state == "pending_in":
                        state = ""
                        route = True
                    elif subs == "from" and not state:
                        subs = "none"
                        route = True
                    elif subs == "from" and state == "pending_out":
                        subs = "none"
                        route = True
                    elif subs == "both" and not state:
                        subs = "to"
                        route = True

                    if not outbound_contact:
                        outbound_contact = {}
                    outbound_contact.update({'subscription': subs})
                    outbound_contact.update({'state': state})
                    self._owner.DB.save_to_roster(jfrom_domain, jfrom_node, bareto, outbound_contact)

                    #self._owner.ROSTER.RosterPushOne(session,stanza)
                    self._owner.ROSTER.RosterPushOneToClient(contact=bareto, to=frm, to_session=session)

                except:
                    self.DEBUG("Could not create roster for client " + str(frm), 'error')

            if route:
                stanza.setFrom(frm)
                stanza.setNamespace(NS_CLIENT)
                s.enqueue(stanza)

            """
            # 4.3 Send the receiver probes of 'unavailable' on behalf of the sender
            # This is highly optional, so we don't do it
            self.DEBUG("Now, we are going to send 'unavailable' probes on behalf of the client "+str(frm), 'warn')
            for pres in self._data[frm].values():
                    pres.setType('unavailable')
                    s.enqueue(pres)
            """

            raise NodeProcessed

    """
    def balance_of_presence(self,session,stanza):
        "Figures-out what should be done to a particular contact"
        self.DEBUG('###BoP: SYSTEM PASS-THROUGH INSTIGATED [%s]'%unicode(stanza).encode('utf-8'),'warn')
        #Predefined settings
        #["subscribe", "subscribed", "unsubscribe", "unsubscribed"]

        #Stanza Stuff
        try:
            frm=stanza['from']
            frm_node=frm.getNode()
            frm_domain=frm.getDomain()
            outfrom=frm_node+'@'+frm_domain
            self.DEBUG('###BoP: RECIEVED STANZA WITH \'FROM\' ATTR','warn')
        except:
            frm = None
            self.DEBUG('###BoP: RECIEVED STANZA WITHOUT \'FROM\' ATTR','warn')


        component = False
        session_jid = session.getSplitJID()
        to=stanza['to']
        if not to: return # Not for us.
        to_node=to.getNode()
        #if not to_node: return # Yep, not for us.
        to_domain=to.getDomain()
        if str(to_domain) in self._owner.components.keys(): component = True
        if not component or (component and to_node): bareto=to_node+'@'+to_domain
        else: bareto = to_domain

        if component:
            s = self._owner.getsession(to)
            if s:
                s.enqueue(stanza)
            raise NodeProcessed

        #bareto=to_node+'@'+to_domain

    # 1. If the user wants to request a subscription to the contact's presence information,
    #    the user's client MUST send a presence stanza of type='subscribe' to the contact:

        if stanza.getType() == 'subscribe':
            if not self.isFromOutside(session_jid[1]) and frm == None:
                self.DEBUG('###BoP: TYP=SUBSCRIBE;U->C','warn')

    # 2. As a result, the user's server MUST initiate a second roster push to all of the user's
    #    available resources that have requested the roster, setting the contact to the pending
    #    sub-state of the 'none' subscription state; this pending sub-state is denoted by the
    #    inclusion of the ask='subscribe' attribute in the roster item:
    #
    #    Note: If the user did not create a roster item before sending the subscription request,
    #          the server MUST now create one on behalf of the user:

                '''
                <iq type='set' id='set1'>
                  <query xmlns='jabber:iq:roster'>
                    <item
                        jid='contact@example.org'
                        subscription='none'
                        ask='subscribe'>
                    </item>
                  </query>
                </iq>
                '''


                rsess = Iq(typ='set')
                rsess.T.query.setNamespace(NS_ROSTER)
                newitem = rsess.T.query.NT.item
                newitem.setAttr('jid',bareto)
                newitem.setAttr('ask','subscribe')
                # Subscription?
                #Dispatch?
                session.dispatch(rsess)
                self._owner.ROSTER.RosterAdd(session,rsess) #add to roster!

                #{'attr':{'ask':'subscribe'}}
                self._owner.ROSTER.RosterPushOne(session,stanza) #We'll let roster services take the bullet.

        # 3. The user's server MUST also stamp the presence stanza of type "subscribe" with the user's
        #    bare JID (i.e., <user@example.com>) as the 'from' address (if the user provided a 'from'
        #    address set to the user's full JID, the server SHOULD remove the resource identifier). If
        #    the contact is served by a different host than the user, the user's server MUST route the
        #    presence stanza to the contact's server for delivery to the contact (this case is assumed
        #    throughout; however, if the contact is served by the same host, then the server can simply
        #    deliver the presence stanza directly):

                stanza.setFrom(session.getBareJID())
                self.DEBUG('###BoP: TYP=SUBSCRIBE;U->C [DONE]','warn')
            elif not self.isFromOutside(to_domain) and frm != None:
                self.DEBUG('###BoP: THE UN-EXPECTED WAS TRIGGERED','warn')
                pass
        elif stanza.getType() == 'subscribed':

        # 5. As a result, the contact's server (1) MUST initiate a roster push to all available resources
        #    associated with the contact that have requested the roster, containing a roster item for the
        #    user with the subscription state set to 'from' (the server MUST send this even if the contact
        #    did not perform a roster set); (2) MUST return an IQ result to the sending resource indicating
        #    the success of the roster set; (3) MUST route the presence stanza of type "subscribed" to the user,
        #    first stamping the 'from' address as the bare JID (<contact@example.org>) of the contact; and
        #    (4) MUST send available presence from all of the contact's available resources to the user:
            '''
            <iq type='set' to='contact@example.org/resource'>
              <query xmlns='jabber:iq:roster'>
                <item
                    jid='user@example.com'
                    subscription='from'
                    name='SomeUser'>
                  <group>SomeGroup</group>
                </item>
              </query>
            </iq>
            '''
            if not self.isFromOutside(session_jid[1]) and frm != None:
                self.DEBUG('###BoP: TYP=SUBSCRIBED;C->U','warn')
                roster = self._owner.DB.pull_roster(session_jid[1],session_jid[0],bareto)
                if roster == None:
                    self.DEBUG('###BoP: TYP=SUBSCRIBED;U->C [NO ROSTER; KILLING NODEPROCESS!','error')
                    raise NodeProcessed
                rsess = Iq(typ='set')
                rsess.NT.query.setNamespace(NS_ROSTER)
                newitem = rsess.T.query.NT.item
                newitem.setAttr('jid',bareto)
                self.DEBUG('###BoP: TYP=SUBSCRIBED;U->C SUBSCRIPTION=%s'%roster['subscription'],'warn')
                if roster['subscription'] != 'to':
                    self.DEBUG('###BoP: TYP=SUBSCRIBED;U->C [TO IS NOT ACTIVE!]','warn')
                    newitem.setAttr('subscription','from')
                else:
                    self.DEBUG('###BoP: TYP=SUBSCRIBED;U->C [TO IS ACTIVE!]','warn')
                    newitem.setAttr('subscription','both')
                newitem.setAttr('ask','InternalDelete')
                self._owner.ROSTER.RosterAdd(session,rsess) #add to roster!

                self._owner.ROSTER.RosterPushOne(session,stanza) #,{'attr':{'ask':'subscribe'}})
                barejid = session.getBareJID()
                stanza.setFrom(barejid)
                session.dispatch(stanza)
                s=None
                for resource in self._data[barejid].keys():
                    s=self._owner.getsession(barejid+'/'+resource)
                    if s: self.broadcastAvailable(s)
                self.DEBUG('###BoP: TYP=SUBSCRIBED;C->U [DONE]','warn')
                self.DEBUG('###BoP: PASS-THROUGH COMPLETE','warn')
                raise NodeProcessed
                return session,stanza

        # 6. Upon receiving the presence stanza of type "subscribed" addressed to the user, the user's
        #    server MUST first verify that the contact is in the user's roster with either of the following
        #    states: (a) subscription='none' and ask='subscribe' or (b) subscription='from' and ask='subscribe'.
        #    If the contact is not in the user's roster with either of those states, the user's server MUST
        #    silently ignore the presence stanza of type "subscribed" (i.e., it MUST NOT route it to the user,
        #    modify the user's roster, or generate a roster push to the user's available resources). If the
        #    contact is in the user's roster with either of those states, the user's server (1) MUST deliver
        #    the presence stanza of type "subscribed" from the contact to the user; (2) MUST initiate a roster
        #    push to all of the user's available resources that have requested the roster, containing an updated
        #    roster item for the contact with the 'subscription' attribute set to a value of "to"; and (3) MUST
        #    deliver the available presence stanza received from each of the contact's available resources to
        #    each of the user's available resources:
            elif not self.isFromOutside(to_domain) and frm == None:
                self.DEBUG('###BoP: TYP=SUBSCRIBED;U->C','warn')
                roster = self._owner.DB.pull_roster(to_domain,to_node,outfrom)
                if roster == None: raise NodeProcessed
                ask_good = False
                subscription_good = False
                from_active = False
                for x,y in roster.iteritems():
                    if x=='ask' and y=='subscribe': ask_good = True
                    if x=='subscription' and y in ['none','from']: subscription_good = True
                    if y == 'from': from_active = True
                    if subscription_good==True and ask_good==True: break

                if subscription_good!=True and ask_good!=True: raise NodeProcessed

                rsess = Iq(typ='set')
                rsess.T.query.setNamespace(NS_ROSTER)
                newitem = rsess.T.query.NT.item
                newitem.setAttr('jid',outfrom)
                if from_active == True:
                    self.DEBUG('###BoP: TYP=SUBSCRIBED;U->C [FROM IS ACTIVE!]','warn')
                    newitem.setAttr('subscription','both')
                else:
                    self.DEBUG('###BoP: TYP=SUBSCRIBED;U->C [FROM IS NOT ACTIVE!]','warn')
                    newitem.setAttr('subscription','to')
                newitem.setAttr('ask','InternalDelete')
                self._owner.ROSTER.RosterAdd(session,rsess) #add to roster!

                self._owner.ROSTER.RosterPushOne(session,stanza) #,{'attr':{'ask':'subscribe'}})
                self.DEBUG('###BoP: TYP=SUBSCRIBED;U->C [DONE]','warn')
        elif stanza.getType() == 'unsubscribe':

            if not self.isFromOutside(session_jid[1]) and frm == None:
                self.DEBUG('###BoP: TYP=UNSUBSCRIBE;U->C','warn')
                roster = self._owner.DB.pull_roster(session_jid[1],session_jid[0],bareto)
                if roster == None: raise NodeProcessed
                rsess = Iq(typ='set')
                rsess.T.query.setNamespace(NS_ROSTER)
                newitem = rsess.T.query.NT.item
                newitem.setAttr('jid',outfrom)
                if roster['subscription'] == 'both':
                    newitem.setAttr('subscription','from')
                else:
                    newitem.setAttr('subscription','none')
                newitem.setAttr('ask','InternalDelete')
                self._owner.ROSTER.RosterAdd(session,rsess) #add to roster!

                self._owner.ROSTER.RosterPushOne(session,stanza) #,{'attr':{'ask':'subscribe'}})
                self.DEBUG('###BoP: TYP=UNSUBSCRIBE;U->C [DONE]','warn')

            if not self.isFromOutside(to_domain) and frm != None:
                self.DEBUG('###BoP: TYP=UNSUBSCRIBE;C->U','warn')
                roster = self._owner.DB.pull_roster(to_domain,to_node,outfrom)
                if roster == None: raise NodeProcessed
                rsess = Iq(typ='set')
                rsess.T.query.setNamespace(NS_ROSTER)
                newitem = rsess.T.query.NT.item
                newitem.setAttr('jid',outfrom)
                if roster['subscription'] == 'both':
                    newitem.setAttr('subscription','to')
                else:
                    newitem.setAttr('subscription','none')
                newitem.setAttr('ask','InternalDelete')
                self._owner.ROSTER.RosterAdd(session,rsess) #add to roster!

                self._owner.ROSTER.RosterPushOne(session,stanza) #,{'attr':{'ask':'subscribe'}})
                self.DEBUG('###BoP: TYP=UNSUBSCRIBE;C->U [DONE]','warn')
        elif stanza.getType() == 'unsubscribed':
            self.DEBUG('###BoP: TYP=UNSUBSCRIBED','warn')

        # 1. If the contact wants to refuse the request, the contact's client MUST send a presence stanza of
        #    type "unsubscribed" to the user (instead of the presence stanza of type "subscribed" sent in Step
        #    6 of Section 8.2):

        # 2. As a result, the contact's server MUST route the presence stanza of type "unsubscribed" to the user,
        #    first stamping the 'from' address as the bare JID (<contact@example.org>) of the contact:
            if not self.isFromOutside(session_jid[1]) and frm == None:
                stanza.setFrom(session.getBareJID())

        #   Note: If the contact's server previously added the user to the contact's roster for tracking purposes,
        #         it MUST remove the relevant item at this time.
                self._owner.DB.del_from_roster(session_jid[1],session_jid[0],bareto)

        # 3. Upon receiving the presence stanza of type "unsubscribed" addressed to the user, the user's server
        #    (1) MUST deliver that presence stanza to the user and (2) MUST initiate a roster push to all of the
        #    user's available resources that have requested the roster, containing an updated roster item for the
        #    contact with the 'subscription' attribute set to a value of "none" and with no 'ask' attribute:

            if not self.isFromOutside(to_domain) and frm != None:
                self.DEBUG('###BoP: TYP=UNSUBSCRIBED;C->U','warn')
                roster = self._owner.DB.pull_roster(to_domain,to_node,outfrom)
                if roster == None: raise NodeProcessed
                rsess = Iq(typ='set')
                rsess.T.query.setNamespace(NS_ROSTER)
                newitem = rsess.T.query.NT.item
                newitem.setAttr('jid',outfrom)
                if roster['subscription'] == 'to':
                    newitem.setAttr('subscription','none')
                elif roster['subscription'] == 'both':
                    newitem.setAttr('subscription','from')
                else:
                    newitem.setAttr('subscription','none')
                newitem.setAttr('ask','InternalDelete')
                self._owner.ROSTER.RosterAdd(session,rsess) #add to roster!

                self._owner.ROSTER.RosterPushOne(session,stanza) #,{'attr':{'ask':'subscribe'}})
                p=Presence(to=outfrom,frm=bareto,typ='unavailable')
                p.setNamespace(NS_CLIENT)
                session.dispatch(p)
                self.DEBUG('###BoP: TYP=UNSUBSCRIBED;C->U [DONE]','warn')

        self.DEBUG('###BoP: PASS-THROUGH COMPLETE','warn')
        return session,stanza
    """

    def karmatize_me_captain(self, s, stanza):
        karma = s.getKarma()
        data_len = len(unicode(stanza))
        if karma is not None and time.time() - karma['last_time'] >= 60:  # reset counters and stuff!
            karma['last_time'] == time.time()
            karma['tot_up'] = 0
            karma['tot_down'] = 0
        if karma is not None and karma['tot_up'] + data_len > karma['up']:
            s.send(Error(stanza, ERR_NOT_ALLOWED))
            raise NodeProcessed
        else:
            if karma is not None:
                karma['tot_up'] += data_len
                s.updateKarma(karma)

    def intra_route(self, stanza):
        getsession = self._owner.getsession
        internal_router = getsession('__ir__@127.0.0.1/ROUTER')
        if internal_router:
            internal_router.enqueue(stanza)

    def routerHandler(self, session, stanza, raiseFlag=True):
        """ XMPP-Core 9.1.1 rules """

        name = stanza.getName()
        self.DEBUG('Router handler called', 'info')
        #self.DEBUG('Recent Errors', "error")

        if name == "presence":
            # They won't catch me alive !
            return

        try:
            self.DEBUG('with stanza %s' % (str(stanza)), 'info')
        except:
            self.DEBUG('with UNKNOWN stanza', 'info')
#        try: print stanza
#        except: pass

        #print "### ROUTES: %s"%(self._owner.routes)
        #print stanza
        """
        # Sometimes, a presence stanza arrives here. Let's redirect it to presenceHandler
        if name == "presence" and stanza.getNamespace() == NS_SERVER:
        """

        to = stanza['to']
        if stanza.getNamespace() == NS_CLIENT and \
            (not to or to == session.ourname) and \
                stanza.props in ([NS_AUTH], [NS_REGISTER], [NS_BIND], [NS_SESSION]):
            return

        try:
            if not session.trusted and session.peer != '__ir__@127.0.0.1/ROUTER':
                self.safeguard(session, stanza)
        except:
            self.DEBUG("NOT SAFEGUARD", "error")

        if not to:  # return
            stanza.setTo(session.ourname)
            to = stanza['to']
            #print "### SESSION.OURNAME = " + str(session.ourname)

        if self.pluginRelay(session, stanza) and raiseFlag:
            raise NodeProcessed
        self.DEBUG("Stanza not for a plugin", "warn")

        #Karma stuff!
        #if name != 'presence': self.karmatize_me_captain(session,stanza)

        domain = to.getDomain()
        #print "DOMAIN:",domain

        component = False
        """
        component_jids = []
        try:
            for v in self._owner.components.values():
                print "V: "+ str(v)
                if v.has_key('jid'):
                    component_jids.append(v['jid'])
        except Exception, e:
            print str(e)
        """

        getsession = self._owner.getsession
        if not self.isFromOutside(domain):
        #if domain in self._owner.servernames or domain in self._owner.components.keys():
            for v in self._owner.components.values():
                try:
                    #if domain in v['jid']:
                    if v['jid'] in domain:
                        component = True
                        break
                except:
                    pass

            #if domain in self._owner.components.keys(): component = True
            node = to.getNode()
            if not node and not component:
                return
            #self._owner.Privacy(session,stanza) # it will if raiseFlag: raise NodeProcessed if needed  # Desactivado de momento
            if not component or (component and node):
                bareto = node + '@' + domain
            else:
                bareto = domain
            resource = to.getResource()

            #print "***BARETO:",bareto

# 1. If the JID is of the form <user@domain/resource> and an available resource matches the full JID,
#    the recipient's server MUST deliver the stanza to that resource.
            try:
                rpri = int(self._data[bareto][resource].getTagData('priority'))
                if rpri < 0:
                    session.enqueue(Error(stanza, ERR_SERVICE_UNAVAILABLE))
                    return
            except:
                rpri = None
            if resource and rpri is not None and rpri > -1:
                to = bareto + '/' + resource
                s = getsession(to)
                if s:
                    s.enqueue(stanza)
                    if raiseFlag:
                        raise NodeProcessed
#            else:
##                print "SPOOOOOTTTTTTTSPOOOOOTTTTTTT 1"
#                self.intra_route(stanza)
#                raise NodeProcessed
# 2. Else if the JID is of the form <user@domain> or <user@domain/resource> and the associated user account
#    does not exist, the recipient's server (a) SHOULD silently ignore the stanza (i.e., neither deliver it
#    nor return an error) if it is a presence stanza, (b) MUST return a <service-unavailable/> stanza error
#    to the sender if it is an IQ stanza, and (c) SHOULD return a <service-unavailable/> stanza error to the
#    sender if it is a message stanza.
            if component:
                node, domain = domain.split(".", 1)
            if not self._owner.AUTH.isuser(node, domain):
                if name in ['iq', 'message']:
                    if stanza.getType() != 'error':
                        session.enqueue(Error(stanza, ERR_SERVICE_UNAVAILABLE))
                if raiseFlag:
                    raise NodeProcessed
# 3. Else if the JID is of the form <user@domain/resource> and no available resource matches the full JID,
#    the recipient's server (a) SHOULD silently ignore the stanza (i.e., neither deliver it nor return an
#    error) if it is a presence stanza, (b) MUST return a <service-unavailable/> stanza error to the sender
#    if it is an IQ stanza, and (c) SHOULD treat the stanza as if it were addressed to <user@domain> if it
#    is a message stanza.
            if resource and name != 'message':
                self.intra_route(stanza)  # Maybe there is one elsewhere?
                if name == 'iq' and stanza.getType() != 'error':
                    session.enqueue(Error(stanza, ERR_SERVICE_UNAVAILABLE))
                if raiseFlag:
                    raise NodeProcessed
# 4. Else if the JID is of the form <user@domain> and there is at least one available resource available
#    for the user, the recipient's server MUST follow these rules:

            pri = -1
            highest_pri = {'pri': 0, 's': None}
            s = None
            try:
                for resource in self._data[bareto].keys():
                    rpri = int(self._data[bareto][resource].getTagData('priority'))
                    if rpri > pri and rpri >= highest_pri['pri']:
                        highest_pri['pri'] = rpri
                        highest_pri['s'] = self._owner.getsession(bareto + '/' + resource)

                if highest_pri['s'] is not None:
                    s = highest_pri['s']
                else:
                    s = getsession(to)
            except:
                s = getsession(to)
            if s:
#       1. For message stanzas, the server SHOULD deliver the stanza to the highest-priority available
#          resource (if the resource did not provide a value for the <priority/> element, the server SHOULD
#          consider it to have provided a value of zero). If two or more available resources have the same
#          priority, the server MAY use some other rule (e.g., most recent connect time, most recent
#          activity time, or highest availability as determined by some hierarchy of <show/> values)
#          to choose between them or MAY deliver the message to all such resources. However, the server
#          MUST NOT deliver the stanza to an available resource with a negative priority; if the only
#          available resource has a negative priority, the server SHOULD handle the message as if there
#          were no available resources (defined below). In addition, the server MUST NOT rewrite the 'to'
#          attribute (i.e., it MUST leave it as <user@domain> rather than change it to <user@domain/resource>).
                if name == 'message':
                    s.enqueue(stanza)
                    if raiseFlag:
                        raise NodeProcessed
#       2. For presence stanzas other than those of type "probe", the server MUST deliver the stanza to all
#          available resources; for presence probes, the server SHOULD reply based on the rules defined in
#          Presence Probes. In addition, the server MUST NOT rewrite the 'to' attribute (i.e., it MUST leave
#          it as <user@domain> rather than change it to <user@domain/resource>).
                # elif name=='presence' and stanza.getType() == 'probe': # differ to Presence Handler!
                #    return self.presenceHandler(session,stanza,raiseFlag)
                elif name == 'presence':
                    self.DEBUG('Presence stanza detected! (%s)' % stanza['to'], 'warn')
                    if stanza.getType() == 'probe' and stanza['to'].getDomain() in self._owner.servernames:
                        stanza.setAttr('internal', 'True')
                        self.presenceHandler(session, stanza, raiseFlag)

                    if stanza.getType() in ["subscribe", "subscribed", "unsubscribe", "unsubscribed"]:
                        #session,stanza = self.balance_of_presence(session,stanza)
                        session, stanza = self.subscriber(session, stanza)

                    # all probes already processed so safely assuming "other" type
                    ps = None
                    for resource in self._data[bareto].keys():
                        ps = getsession(bareto + '/' + resource)
                        if ps:
                            ps.enqueue(stanza)
                    if raiseFlag:
                        raise NodeProcessed
#       3. For IQ stanzas, the server itself MUST reply on behalf of the user with either an IQ result or an
#          IQ error, and MUST NOT deliver the IQ stanza to any of the available resources. Specifically, if
#          the semantics of the qualifying namespace define a reply that the server can provide, the server
#          MUST reply to the stanza on behalf of the user; if not, the server MUST reply with a
#          <service-unavailable/> stanza error.
#	UPDATE: Or not.
                if name == 'iq':
                    s.enqueue(stanza)
                    if raiseFlag:
                        raise NodeProcessed
                return
# 5. Else if the JID is of the form <user@domain> and there are no available resources associated with
#    the user, how the stanza is handled depends on the stanza type:
            else:
                self.intra_route(stanza)  # Try to outsource this guy!

#       1. For presence stanzas of type "subscribe", "subscribed", "unsubscribe", and "unsubscribed",
#          the server MUST maintain a record of the stanza and deliver the stanza at least once (i.e., when
#          the user next creates an available resource); in addition, the server MUST continue to deliver
#          presence stanzas of type "subscribe" until the user either approves or denies the subscription
#          request (see also Presence Subscriptions).
                if name == 'presence':
                    if stanza.getType() == 'probe' and stanza['to'].getDomain() in self._owner.servernames:
                        stanza.setAttr('internal', 'True')
                        self.presenceHandler(session, stanza, raiseFlag)

                    if stanza.getType() in ["subscribe", "subscribed", "unsubscribe", "unsubscribed"]:
                        #session,stanza = self.balance_of_presence(session,stanza)
                        session, stanza = self.subscriber(session, stanza)
                    #elif stanza.getType() == 'probe': # differ to Presence Handler!
                #   return self.presenceHandler(session,stanza,raiseFlag)
#       2. For all other presence stanzas, the server SHOULD silently ignore the stanza by not storing it
#          for later delivery or replying to it on behalf of the user.
                    if raiseFlag:
                        raise NodeProcessed
#       3. For message stanzas, the server MAY choose to store the stanza on behalf of the user and deliver
#          it when the user next becomes available, or forward the message to the user via some other means
#          (e.g., to the user's email account). However, if offline message storage or message forwarding
#          is not enabled, the server MUST return to the sender a <service-unavailable/> stanza error. (Note:
#          Offline message storage and message forwarding are not defined in XMPP, since they are strictly a
#          matter of implementation and service provisioning.)
                elif name == 'message':
                    #self._owner.DB.store(domain,node,stanza)
#                    if stanza.getType()<>'error': session.enqueue(Error(stanza,ERR_RECIPIENT_UNAVAILABLE))
                    if raiseFlag:
                        raise NodeProcessed
#       4. For IQ stanzas, the server itself MUST reply on behalf of the user with either an IQ result or
#          an IQ error. Specifically, if the semantics of the qualifying namespace define a reply that the
#          server can provide, the server MUST reply to the stanza on behalf of the user; if not, the server
 #          MUST reply with a <service-unavailable/> stanza error.
                return
        else:
            s = getsession(domain)
            if not s:
                s = self._owner.S2S(session.ourname, domain)

            s.enqueue(stanza)
            if raiseFlag:
                raise NodeProcessed
