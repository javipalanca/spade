# -*- coding: utf-8 -*-
# Distributed under the terms of GPL version 2 or any later
# Copyright (C) Kristopher Tate/BlueBridge technologies, 2005
# Roster module for xmppd.py

from xmpp import *


class ROSTER(PlugIn):
    NS = NS_ROSTER

    def plugin(self, server):
        server.Dispatcher.RegisterHandler('iq', self.RosterIqHandler, typ='set', ns=NS_ROSTER, xmlns=NS_CLIENT)
        server.Dispatcher.RegisterHandler('iq', self.RosterIqHandler, typ='get', ns=NS_ROSTER, xmlns=NS_CLIENT)

    def RosterAdd(self, session, stanza, ask_subscribe=False):
        s_split_jid = session.getSplitJID()
        the_roster = session.getRoster()
        if stanza.getType() == 'set' and stanza.getTag('query').kids != []:
            for kid in stanza.getTag('query').kids:
                split_jid = self._owner.tool_split_jid(kid.getAttr('jid'))
                if split_jid is None:
                    raise NodeProcessed
                if kid.getName() == 'item' and kid.getAttr('subscription') != 'remove':
                    info = {}
                    name = kid.getAttr('name')
                    if name is not None:
                        info.update({'name': name})

                    subscription = kid.getAttr('subscription')
                    if subscription is not None:
                        info.update({'subscription': subscription})
                    elif kid.getAttr('jid') not in the_roster.keys() or ('subscription' in the_roster[kid.getAttr('jid')]) is False:
                        self.DEBUG('Wow, subscription is not active -- better create one pronto!', 'warn')
                        #kid.setAttr('subscription','none')
                        info.update({'subscription': 'none'})

                    ask = kid.getAttr('ask')
                    if ask is not None or ask_subscribe is True:
                        info.update({'ask': ask})
                    elif ask == 'InternalDelete':
                        kid.delAttr('ask')
                        self._owner.DB.del_from_roster_jid(s_split_jid[1], s_split_jid[0], split_jid[0] + '@' + split_jid[1], 'ask')

                    #self.DEBUG(unicode(info).encode('utf-8'),'error')
                    self._owner.DB.save_to_roster(s_split_jid[1], s_split_jid[0], split_jid[0] + '@' + split_jid[1], info)
                    #WARNING: When no group is defined, we remove the membership to any group
                    #Not sure if this is XMPP complaint
                    #if kid.kids != []:
                    group_list = []
                    for grandkid in kid.kids:
                        if grandkid.getName() == 'group':
                            group_list += [grandkid.getData()]
                    self._owner.DB.save_groupie(s_split_jid[1], s_split_jid[0], split_jid[0] + '@' + split_jid[1], group_list)

    def RosterRemove(self, session, stanza):
        s_split_jid = session.getSplitJID()
        if stanza.getType() == 'set' and stanza.getTag('query').kids != []:
            for kid in stanza.getTag('query').kids:
                if kid.getName() == 'item' and kid.getAttr('subscription') == 'remove':
                    #split_jid = self._owner.tool_split_jid(kid.getAttr('jid'))
                    self.DEBUG("Removing contact from " + str(session.getBareJID()) + " to " + str(kid.getAttr('jid')), 'ok')
                    p = Presence(to=kid.getAttr('jid'), frm=session.getBareJID(), typ='unsubscribe')
                    session.dispatch(p)
                    #split_jid = self._owner.tool_split_jid(kid.getAttr('jid'))
                    p = Presence(to=kid.getAttr('jid'), frm=session.getBareJID(), typ='unsubscribed')
                    session.dispatch(p)

                    session.enqueue(stanza)

                    self._owner.DB.del_from_roster(s_split_jid[1], s_split_jid[0], kid.getAttr('jid'))
                    self._owner.DB.del_groupie(s_split_jid[1], s_split_jid[0], kid.getAttr('jid'))

                    #Tell 'em we just road-off into the sunset
                    #split_jid = self._owner.tool_split_jid(kid.getAttr('jid'))
                    p = Presence(to=kid.getAttr('jid'), frm=session.peer, typ='unavailable')
                    session.dispatch(p)

    def RosterPushOneToClient(self, contact, to, to_session=None, mode='set', options=None):
        self.DEBUG('#ROSTER#: Pushing one out to client!', 'warn')
        #Stanza Stuff
        to = JID(to)
        if not to:
            return  # Not for us.
        if to_session:
            session = to_session
        else:
            session = self._owner.getsession(str(to))

        to_node = to.getNode()
        #if not to_node: return # Yep, not for us.
        to_domain = to.getDomain()
        if not self._owner.Router.isFromOutside(to_domain):
        #if to_domain in self._owner.servernames:
            #bareto=to_node+'@'+to_domain
            #to_roster=self._owner.DB.get(to_domain,to_node,'roster')
            item = self._owner.DB.pull_roster(to_domain, to_node, str(contact))
            """
            <iq type='set'>
              <query xmlns='jabber:iq:roster'>
                <item
                    jid='contact@example.org'
                    subscription='none'
                    ask='subscribe'
                    name='MyContact'>
                  <group>MyBuddies</group>
                </item>
              </query>
            </iq>
            """
            out = Iq(typ=mode)
            out.NT.query.setNamespace(NS_ROSTER)
            atag = out.T.query.NT.item
            atag.setAttr('jid', str(contact))
            if item:
                for key, value in item.items():
                    if key != 'state':
                        try:
                            atag.setAttr(key, value)
                        except:
                            pass
            """
            try:
                    for x,y in session.getRoster()[bareto].iteritems():
                        atag.setAttr(x,y)
            except:
                pass
            """

            barejid = session.getBareJID()
            try:
                for resource in self._owner.Router._data[barejid].keys():
                    s = self._owner.getsession(barejid + '/' + resource)
                    s.send(out)
            except:
                pass

        self.DEBUG('#ROSTER#: Pushing one out to client %s! [COMPLETE]' % (barejid), 'warn')

    def RosterPushOne(self, session, stanza, mode='set', options=None):
        self.DEBUG('#ROSTER#: Pushing one out!', 'warn')
        #Stanza Stuff
        to = stanza['to']
        if not to:
            return  # Not for us.
        to_node = to.getNode()
        if not to_node:
            return  # Yep, not for us.
        to_domain = to.getDomain()
        if not self._owner.Router.isFromOutside(to_domain):
        #if to_domain in self._owner.servernames:
            bareto = to_node + '@' + to_domain
            to_roster = self._owner.DB.get(to_domain, to_node, 'roster')
            """
            <iq type='set'>
              <query xmlns='jabber:iq:roster'>
                <item
                    jid='contact@example.org'
                    subscription='none'
                    ask='subscribe'
                    name='MyContact'>
                  <group>MyBuddies</group>
                </item>
              </query>
            </iq>
            """
            out = Iq(typ=mode)
            out.NT.query.setNamespace(NS_ROSTER)
            atag = out.T.query.NT.item
            s_split_jid = session.getSplitJID()
            split_jid = self._owner.tool_split_jid(bareto)
            name = self._owner.DB.get(split_jid[1], split_jid[0], 'name')
            groups = session.getGroups()
            atag.setAttr('jid', bareto)
            try:
                for x, y in session.getRoster()[bareto].iteritems():
                    atag.setAttr(x, y)
            except:
                pass
            if options == {} and 'attr' in options:
                for ok, od in options['attr']:
                    atag.setAttr(ok, od)
            if atag.getAttr('name') is None and name is not None:
                atag.setAttr('name', name)

            ask = atag.getAttr('ask')
            if ask == 'InternalDelete':
                atag.delAttr('ask')
                self._owner.DB.del_from_roster_jid(s_split_jid[1], s_split_jid[0], bareto, 'ask')

            if groups is not None:
                for gn, gm in groups.iteritems():
                    if bareto in gm:
                        atag.T.group.setData(gn)
                        break
            else:
                atag.T.group.setData('My Friends')
            barejid = session.getBareJID()
            for resource in self._owner.Router._data[barejid].keys():
                s = self._owner.getsession(barejid + '/' + resource)
                s.send(out)
        self.DEBUG('#ROSTER#: Pushing one out! [COMPLETE]', 'warn')

    def RosterPush(self, session, stanza, mode='result'):
        rep = stanza.buildReply(mode)
        the_roster_guy = session.getRoster()
        if the_roster_guy is None:
            return
        for k, v in the_roster_guy.items():
            try:
                atag = rep.T.query.NT.item
                split_jid = self._owner.tool_split_jid(k)
                if split_jid is not None:
                    name = self._owner.DB.get(split_jid[1], split_jid[0], 'name')
                else:
                    name = None
                groups = session.getGroups()
                atag.setAttr('jid', k)
                for x, y in v.items():
                    atag.setAttr(x, y)
                if atag.getAttr('name') is None and name is not None:
                    atag.setAttr('name', name)
                if groups is not None:
                    for gn, gm in groups.items():
                        for igm in gm:
                            if igm == k:
                                atag.NT.group.setData(gn)
                                break
                else:
                    atag.NT.group.setData('My Friends')
            except Exception, e:
                self.DEBUG("Exception in RosterPush: " + str(e), 'err')
        self.DEBUG("RosterPush sending " +str(rep), 'info')
        session.send(rep)

    def RosterPushToClient(self, bareto, to_session=None):
        if not to_session:
            session = self._owner.getsession(bareto)
        else:
            session = to_session

        if not session:
            self.DEBUG("Could not find suitable 'to' session", "error")
            return

        if self._owner.Router.isFromOutside(JID(bareto).getDomain()):
        #if JID(bareto).getDomain() not in self._owner.servernames:
            self.DEBUG("Client not in a local server. Returning", "warn")
            return

        rep = Iq(typ="set", queryNS=NS_ROSTER)
        the_roster_guy = session.getRoster()
        if the_roster_guy is None:
            return
        #for k,v in the_roster_guy.iteritems():
        for k, v in the_roster_guy.items():
            atag = rep.T.query.NT.item
            split_jid = self._owner.tool_split_jid(k)
            if split_jid is not None:
                name = self._owner.DB.get(split_jid[1], split_jid[0], 'name')
            else:
                name = None
            groups = session.getGroups()
            atag.setAttr('jid', k)
            for x, y in v.iteritems():
                atag.setAttr(x, y)
            if atag.getAttr('name') is None and name is not None:
                atag.setAttr('name', name)

            if groups is not None:
                for gn, gm in groups.iteritems():
                    for igm in gm:
                        if igm == k:
                            atag.T.group.setData(gn)
                            break
            else:
                atag.T.group.setData('My Friends')
        session.send(rep)

    def RosterIqHandler(self, session, stanza):
        self.DEBUG("Roster Iq handler called", "info")
        #print "session info:", dir(session)
        s_split_jid = self._owner.tool_split_jid(session.peer)
        if stanza.getType() == 'set' and stanza.getTag('query').kids != []:
            for kid in stanza.getTag('query').kids:
                split_jid = self._owner.tool_split_jid(kid.getAttr('jid'))
                if kid.getName() == 'item' and kid.getAttr('subscription') != 'remove':
                    self.RosterAdd(session, stanza)
                elif kid.getName() == 'item' and kid.getAttr('subscription') == 'remove':
                    self.RosterRemove(session, stanza)
            self.RosterPush(session, stanza, 'set')  # Push it out, will ya?
            IQ = Iq(typ='result', to=session.peer)
            IQ.setAttr('id', stanza.getID())
            session.send(IQ)
        elif stanza.getType() == 'get' and stanza.getTag('query').kids == []:
            self.RosterPush(session, stanza, 'result')  # How's the result???

        raise NodeProcessed
