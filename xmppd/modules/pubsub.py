# -*- coding: utf-8 -*-

from uuid import uuid4
from datetime import datetime

from xmpp import *
from xmpp.protocol import *


class PSNode(object):
    """
    Publish-Subscribe node.

    TODO: Items must retain info about its publisher. We have only implemented
          owners and subscribes, not publishers. So publisher is always the onwer.
    """

    def __init__(self, id, owner, type='leaf', parent=None, children=[], members={}, access_model='presence'):
        """
        Constructs a PSNode.

        @type  id: string
        @param m: node id
        """
        self.id = id
        self.owner = owner
        self.type = type
        self.parent = parent
        self.children = children
        self.members = members
        self.access_model = access_model
        self.item_ids = []
        self.items_timestamp = {}
        self.items = {}

    def addItem(self, id, content):
        try:
            #TODO: Error if ID aready exists.
            if id not in self.item_ids:
                self.item_ids.append(id)
            self.items[id] = content
            self.items_timestamp[id] = datetime.utcnow().isoformat().split('.')[0] + 'Z'
            #print self.items_timestamp[id], self.items[id], id
        except Exception, e:
            self.DEBUG('Exception in addItem: ' + str(e), "error")

    def __repr__(self):
        return 'PSNode(%s, %s)' % (self.id, self.type)

    def __str__(self):
        return self.__repr__()


class PubSubServer(PlugIn):

    NS = NS_PUBSUB

    def plugin(self, server):
        self.name = self._owner.servernames[0]
        self.nodes = {}

        for ns in (NS_PUBSUB, NS_PUBSUB_ERRORS, NS_PUBSUB_EVENTS, NS_PUBSUB_OWNER):
            server.Dispatcher.RegisterHandler('iq', self.PubSubIqHandler, typ='set', ns=ns, xmlns=NS_CLIENT)
            server.Dispatcher.RegisterHandler('iq', self.PubSubIqHandler, typ='set', ns=ns, xmlns=NS_COMPONENT_ACCEPT)

    def _getIqError(self, iq, name, specific=None):
        if specific is None:
            return Error(iq, NS_STANZAS + ' ' + name)
        else:
            error_node = ErrorNode(name)
            error_node.addChild(name=specific, attrs={'xmlns': NS_PUBSUB_ERRORS})
            iq = iq.buildReply('error')
            iq.addChild(node=error_node)
            return iq

    def _sendItem(self, node_id, item_id, frm=None):
        #FIXME: items contents have incorrect xmlns
        try:
            node = self.nodes[node_id]

            #print node.members

            for jid in node.members.keys():
                #print 'Enviando %s a %s' % (item_id,jid)
                msg = Message(frm=self.name, to=jid)
                msg.setID(str(uuid4()))  # TODO: Do this automatically in xmpp.protocol.Protocol
                event_node = Node(tag='event', attrs={'xmlns': NS_PUBSUB_EVENTS})
                items_node = Node(tag='items', attrs={'node': node_id})
                item_node = Node(tag='item', attrs={'id': item_id, 'timestamp': node.items_timestamp[item_id]})
                if frm is not None:
                    item_node['publisher'] = frm
                item_node.addChild(node=node.items[item_id])
                items_node.addChild(node=item_node)
                event_node.addChild(node=items_node)
                msg.addChild(node=event_node)
                s = self._owner.getsession(jid)
                s.send(msg)
        except Exception, e:
            self.DEBUG('Exception in sendItem: ' + str(e), "error")

        #TODO: If we had a maximum, we should remove the first item here. Doing a FIFO.
    def PubSubIqHandler(self, session, stanza):
        """
        XXX: We do not validate. We just get what we want and that is enough.
        """

        try:

            self.DEBUG('PubSub Iq handler called', 'info')

            #if stanza.getType() == 'set':
            pubsub_node = stanza.getTag('pubsub')

            # If no pubsub node, this should have arrive here.
            # TODO: Return an error to the user?
            if pubsub_node is None:
                self.DEBUG('Bad message: %s' % stanza, 'error')
                raise NodeProcessed

            # CREATE NODE
            if pubsub_node.getTag('create') is not None:
                create_node = pubsub_node.getTag('create')
                node_id = create_node.getAttr('node')

                #TODO: If no name, this is an instant node.

                if False:  # TODO: Registro
                    session.send(self._getIqError(stanza, 'registration-required'))
                    raise NodeProcessed

                if False:  # TODO: cuando tengamos privilegios
                    session.send(self._getIqError(stanza, 'forbidden'))
                    raise NodeProcessed

                if node_id in self.nodes:
                    iq = self._getIqError(stanza, 'conflict')
                    session.send(iq)
                    raise NodeProcessed

                if False:  # TODO: Access model
                    session.send(self._getIqError(stanza, 'not-acceptable', 'unsupported-access-model'))
                    raise NodeProcessed

                self.nodes[node_id] = PSNode(id=node_id, owner=stanza.getFrom())

                # Add node
                #print self.nodes
                self.DEBUG('Creating node: %s' % create_node, 'info')

                varid = stanza.getAttr('id')
                if isinstance(stanza, Protocol):
                    stanza = Iq(node=stanza)

                iq = stanza.buildReply('result')
                if varid:
                    iq.setID(varid)
                pubsub_node = Node(tag='pubsub', attrs={'xmlns': NS_PUBSUB})
                pubsub_node.addChild(node=create_node)
                iq.addChild(node=pubsub_node)

                # SUCCESS
                session.send(iq)

            # DELETE NODE
            elif pubsub_node.getTag('delete') is not None:
                self.DEBUG('PubSub Delete Node', 'info')

                node_id = pubsub_node.getTag('delete').getAttr('node')

                if node_id is None:  # FIXME
                    self.DEBUG('Node is Non', 'error')
                    session.send(self._getIqError(stanza, 'item-not-found'))
                    raise NodeProcessed

                if node_id not in self.nodes:
                    self.DEBUG('Node does not exists: %s' % node_id, 'error')
                    session.send(self._getIqError(stanza, 'item-not-found'))
                    raise NodeProcessed

                node = self.nodes[node_id]

                if not node.owner.bareMatch(stanza.getFrom()):
                    self.DEBUG('You are not allowed to delete this node: %s' % node, 'err')
                    session.send(self._getIqError(stanza, 'forbidden'))
                    raise NodeProcessed

                # Delete node
                # Keep in mind that associated items are (and must be) deleted.
                del self.nodes[node_id]

                # SUCCESS
                session.send(stanza.buildReply('result'))
                self.DEBUG('Node was deleted succesfully %s'%str(stanza.buildReply('result')), 'info')

                # Notify no all subscribers
                for jid in node.members.keys():
                    msg = Message(frm=self.name, to=jid)
                    msg.setID(str(uuid4()))  # TODO: Do this automatically in xmpp.protocol.Protocol
                    event_node = Node(tag='event', attrs={'xmlns': NS_PUBSUB + '#event'})
                    event_node.addChild(name='delete', attrs={'node': node_id})
                    msg.addChild(node=event_node)
                    s = self._owner.getsession(jid)
                    s.send(msg)

            # SUBSCRIBE
            elif pubsub_node.getTag('subscribe') is not None:

                #TODO: We do not do multiple subscribe.
                #      So be careful if we duplicate subscriptions.

                subscribe_node = pubsub_node.getTag('subscribe')
                node_id = subscribe_node.getAttr('node')

                jid = JID(subscribe_node.getAttr('jid'))

                #print 'nodes: ', self.nodes
                if node_id is None or jid is None:  # TODO: Que enviar aquí?, además, jid no es None, peta antes
                    self.DEBUG('No node id or jid in subscribe message.', 'error')
                    raise NodeProcessed

                if node_id not in self.nodes:
                    self.DEBUG('Node does not exists: %s' % node_id, 'error')
                    session.send(self._getIqError(stanza, 'item-not-found'))
                    raise NodeProcessed

                if not stanza.getFrom().bareMatch(jid):  # Trying to subscribe a JID different from the real one
                    session.send(self._getIqError(stanza, 'bad-request', 'invalid-jid'))
                    raise NodeProcessed

                node = self.nodes[node_id]
                access_model = node.access_model
                #print 'access_model: ', 'presence'

                if access_model == 'presence':
                    owner_roster = self._owner.DB.db[self.name][node.owner.getNode()]['roster']
                    if jid in owner_roster:
                        if owner_roster[jid.getStripped()]['subscription'] not in ('from', 'both'):
                            if owner_roster[jid.getStripped()]['status'] == 'pending_in':  # XXX: pending_out too?
                                session.send(self._getIqError(stanza, 'not-authorized', 'pending-subscription'))
                                raise NodeProcessed
                            else:
                                session.send(self._getIqError(stanza, 'not-authorized', 'presence-subscription-required'))
                                raise NodeProcessed
                    else:
                        session.send(self._getIqError(stanza, 'not-authorized', 'presence-subscription-required'))
                        raise NodeProcessed

                if False:  # TODO: Roster access_model
                    #TODO: WE DO NOT IMPLEMENT ROSTER ACCESS MODEL EVEN IF IT IS REQUIRED BY XEP-163
                    pass

                if False:  # TODO: Whitelist access_model
                    #TODO: WE DO NOT IMPLEMENT WHITELIST ACCESS MODEL EVEN IF IT IS REQUIRED BY XEP-163
                    pass

                if False:  # TODO: Do not allow subscription from blocked people, even with 'open' access model
                    #TODO: WE DO NOT IMPLEMENT BLOCKING
                    pass

                if False:  # TODO: Establish a max_subscription threshold.
                    #TODO: Let's people of the future care about security.
                    pass

                # SUCESS

                # Add new member to node, with its subid (an UUID)
                node.members[jid] = str(uuid4())

                #TODO: Send last published item (as required by XEP-163 by default
                iq = stanza.buildReply('result')
                pubsub_node = Node(tag='pubsub', attrs={'xmlns': NS_PUBSUB})
                pubsub_node.addChild(name='subscription', attrs={
                    'node': node_id,
                    'jid': jid,
                    'subid': node.members[jid],
                    'subscription': 'subscribed'
                })
                iq.addChild(node=pubsub_node)
                session.send(iq)

            # UNSUBSCRIBE
            elif pubsub_node.getTag('unsubscribe') is not None:
                unsubscribe_node = pubsub_node.getTag('unsubscribe')
                node_id = unsubscribe_node.getAttr('node')
                jid = unsubscribe_node.getAttr('jid')

                if node_id is None or jid is None:  # TODO: Que enviar aquí?
                    self.DEBUG('No node id or jid in subscribe message.', 'error')
                    raise NodeProcessed

                if node_id not in self.nodes:
                    self.DEBUG('Node does not exists: %s' % node_id, 'error')
                    session.send(self._getIqError(stanza, 'item-not-found'))
                    raise NodeProcessed

                if not stanza.getFrom().bareMatch(JID(jid)):  # Trying to subscribe a JID different from the real one
                    session.send(self._getIqError(stanza, 'bad-request', 'invalid-jid'))
                    raise NodeProcessed

                node = self.nodes[node_id]

                if jid not in node.members:
                    #XXX: Owner is not a member, so he would trigger this error too if he is stupid.
                    session.send(self._getIqError(stanza, 'unexpected-request', 'not-subscribed'))
                    raise NodeProcessed

                del node.members[jid]

                # SUCESS
                session.send(stanza.buildReply('result'))

            # PUBLISH ITEM
            elif pubsub_node.getTag('publish') is not None:
                publish_node = pubsub_node.getTag('publish')
                node_id = publish_node['node']

                if node_id is None:  # TODO: Que enviar aquí?
                    self.DEBUG('No node id or jid in subscribe message.', 'error')
                    raise NodeProcessed

                item_node = publish_node.getTag('item')

                if item_node is None:  # TODO: Que enviar aquí?
                    self.DEBUG('No item', 'error')
                    raise NodeProcessed

                if node_id not in self.nodes:
                    # XEP-60 defines auto-create, XEP-163 enforces it.
                    self.nodes[node_id] = PSNode(id=node_id, owner=stanza.getFrom())

                node = self.nodes[node_id]

                # TODO: Change once we implement additional publishers (not only owner).
                if not node.owner.bareMatch(stanza.getFrom()):
                    session.send(self._getIqError(stanza, 'forbidden'))
                    raise NodeProcessed

                item_id = item_node['id']
                if item_id is None:
                    item_id = str(uuid4())

                #print item_node.getChildren()
                self.nodes[node_id].addItem(item_id, item_node.getChildren()[0])

                # SUCESS

                iq = stanza.buildReply('result')
                pubsub_node = Node(tag='pubsub', attrs={'xmlns': NS_PUBSUB})
                publish_node = Node(tag='publish', attrs={'node': node_id})
                publish_node.addChild(name='item', attrs={'id': item_id})
                pubsub_node.addChild(node=publish_node)
                iq.addChild(node=pubsub_node)
                session.send(iq)

                # Send item to all subscriptors.
                self._sendItem(node_id, item_id, stanza.getFrom())

            # NON-IMPLEMENTED ACTION
            else:
                self.DEBUG('Not implemented: %s' % create_node, 'info')

            raise NodeProcessed
        except NodeProcessed:
            raise NodeProcessed
        except Exception, e:
            self.DEBUG("Exception in PubSub Handler: " + str(e), "error")
