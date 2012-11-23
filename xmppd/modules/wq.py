# -*- coding: utf-8 -*-

from xmpp import *
import types
import copy


class ItemNotFound(Exception):
    def __init__(self):
        pass


class Conflict(Exception):
    def __init__(self):
        pass


class Group:
    """
    A XEP-142 Workgroup
    """
    def __init__(self, gname, wq, users=[]):
        self.name = gname
        self.wq = wq

        self.users = dict()
        self.agents = dict()  # An "agent" here is a client that "works" in the group and assists users

        for u in users:
            self.users[u] = None
        self.DEBUG = self.wq.DEBUG
        self.DEBUG("Group %s created" % (self.name), "ok")

    def fullJID(self):
        return str(self.name) + '@' + str(self.wq.jid)

    def dispatch(self, session, stanza):
        """
        Mini-dispatcher for the jabber stanzas that arrive to the group
        """
        self.DEBUG("Group '" + self.getName() + "' dispatcher called")
        if stanza.getName() == 'iq':
            self.IQ_cb(session, stanza)
        elif stanza.getName() == 'presence':
            self.Presence_cb(session, stanza)
        elif stanza.getName() == 'message':
            self.Message_cb(session, stanza)
        # TODO: Implement the rest of protocols

    def IQ_cb(self, session, stanza):
        """
        IQ Callback for a group
        """
        self.DEBUG("IQ callback of group %s called" % (self.getName()), "info")
        join_queue = stanza.getTag('join-queue')
        depart_queue = stanza.getTag('depart-queue')
        queue_status = stanza.getTag('queue_status')
        frm = str(session.peer)
        if join_queue:
            self.DEBUG("Join-queue", "info")
            ns = join_queue.getNamespace()
            typ = stanza.getType()
            queue_notifications = join_queue.getTag('queue-notifications')
            if ns == "http://jabber.org/protocol/workgroup" and typ == 'set' and queue_notifications:
                # User requests to join the group
                try:
                    if self.addUser(JID(frm).getStripped()):
                        # The joining is succesful
                        reply = stanza.buildReply(typ="result")
                        session.enqueue(reply)
                        return
                except Conflict:
                    # User already in group
                    self.DEBUG("User tried to join the same group again", "warn")
                    reply = stanza.buildReply(typ="error")
                    err = Node('error', {'code': '409', 'type': 'cancel'})
                    conflict = Node('conflict', {'xmlns': 'urn:ietf:params:xml:ns:xmpp-stanzas'})
                    err.addChild(node=conflict)
                    reply.addChild(node=err)
                    session.enqueue(reply)
                    return
                except Exception, e:
                    self.DEBUG("Unknown exception when user was joining a group", "error")
                    return
        elif depart_queue:
            self.DEBUG("Depart-queue", "info")
            ns = depart_queue.getNamespace()
            typ = stanza.getType()
            jid = depart_queue.getTag('jid')
            if ns == "http://jabber.org/protocol/workgroup" and typ == 'set':
                # User requests departing a group
                if jid:
                    # TODO: Authenticate user for being able to remove other jid than own
                    user = jid.getData()
                else:
                    user = JID(frm).getStripped()
                try:
                    if self.delUser(user):
                        # The departing is succesful
                        reply = stanza.buildReply(typ="result")
                        session.enqueue(reply)
                        m = Message(frm=self.fullJID(), to=frm)
                        dq = m.setTag("depart-queue", {"xmlns": "http://jabber.org/protocol/workgroup"})
                        session.enqueue(m)
                        return
                except ItemNotFound:
                    # The user was not in the group
                    self.DEBUG("User not in the group", "warn")
                    reply = stanza.buildReply(typ="error")
                    err = Node('error', {'code': '404', 'type': 'cancel'})
                    conflict = Node('item-not-found', {'xmlns': 'urn:ietf:params:xml:ns:xmpp-stanzas'})
                    err.addChild(node=conflict)
                    reply.addChild(node=err)
                    session.enqueue(reply)
                    return

                except Exception, e:
                    self.DEBUG("Unknown exception when user was departing a group", "error")
                    return
        elif queue_status:
            self.DEBUG("Queue-status", "info")
            ns = queue_status.getNamespace()
            typ = stanza.getType()
            if ns == "http://jabber.org/protocol/workgroup" and typ == 'get':
                # User Status Poll
                reply = stanza.buildReply(typ="result")
                p = Node("position")
                p.setData("0")
                queue_status.addChild(node=p)
                t = Node("time")
                t.setData("0")
                queue_status.addChild(node=t)
                reply.addChild(node=queue_status)
                session.enqueue(reply)
                return

    def addUser(self, barejid):
        if barejid not in self.users.keys():
            self.users[barejid] = None
            self.DEBUG("User %s joined group %s" % (barejid, self.getName()), "ok")
            return True
        else:
            raise Conflict

    def delUser(self, barejid):
        if barejid in self.users.keys():
            del self.users[barejid]
            self.DEBUG("User %s departed group %s" % (barejid, self.getName()), "ok")
            return True
        else:
            raise ItemNotFound

    def updateAgent(self, barejid, pres):
        self.agents[barejid] = pres
        self.DEBUG("Agent %s joined group %s" % (barejid, self.getName()), "ok")
        return True

    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name
        return


class WQ(PlugIn):
    """
    The Workgroup Queues component
    """
    NS = ''

    def plugin(self, server):
        self.server = server
        try:
            self.jid = server.plugins['WQ']['jid']
            self.name = server.plugins['WQ']['name']
        except:
            self.DEBUG("Could not find MUC jid or name", "error")
            return

        self.groups = dict()

        # Test stuff
        g = Group("test", self)
        self.addGroup(g)

        self.DEBUG("Created WQ: '%s' '%s'" % (self.name, str(self.jid)), "warn")

    def addGroup(self, group, name=""):
        if not group and not name:
            # WTF
            self.DEBUG("addGroup called without parameters", "warn")
            return False
        elif not group and name:
            group = Group(name, self)
        elif group:
            if group.getName() in self.groups.keys():
                return False
            else:
                self.groups[group.getName()] = group
                self.DEBUG("Added group %s to Workgroup Queues" % (group.getName()), "ok")
                return True

    def addUser(self, barejid, gname):
        if gname not in self.groups.keys():
            # Group does not exist
            raise ItemNotFound
        else:
            # User tries to join group
            self.groups[gname].addUser(barejid)

    def dispatch(self, session, stanza):
        """
        Mini-dispatcher for the jabber stanzas that arrive to the WQ
        """
        self.DEBUG("WQ dispatcher called", "warn")
        try:
            to = stanza['to']
            gname = to.getNode()
            domain = to.getDomain()
        except:
            self.DEBUG("There was no 'to'", 'warn')

        # No group name. Stanza directed to the WQ
        if gname == '' and domain == str(self.jid):
            if stanza.getName() == 'iq':
                self.IQ_cb(session, stanza)
            elif stanza.getName() == 'presence':
                self.Presence_cb(session, stanza)
            # TODO: Implement the rest of protocols
        # Stanza directed to a specific group
        if gname in self.groups.keys() and domain == str(self.jid):
            self.groups[gname].dispatch(session, stanza)
        else:
            # The room does not exist
            self.notExist_cb(session, stanza)
