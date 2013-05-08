# -*- coding: utf-8 -*-
import itertools
from Behaviour import MessageTemplate, OneShotBehaviour

from xmpp.protocol import *
from xmpp.simplexml import Node
import uuid


def gen_id():
    return str(uuid.uuid4())

#TODO: Implementar retrieve nodes y discovery

class PubSub(object):

    def __init__(self, agent):  # , msgrecv):
        self._client = agent.getAID().getName()
        #self.msgrecv = msgrecv
        self.myAgent = agent
        self._server = agent.server

    def register(self):
        namespaces = [NS_PUBSUB, NS_PUBSUB_ERRORS, NS_PUBSUB_EVENTS, NS_PUBSUB_OWNER]
        for typ,ns in itertools.product(['set','get','result','error'], namespaces):
            self.myAgent.jabber.RegisterHandler('iq', self.myAgent._jabber_messageCB, typ, ns)

    def _sendAndReceive(self, iq, getContents):
        varid = gen_id()
        t = MessageTemplate(Iq(attrs={'id': varid}))
        iq.setID(varid)
        b = self._sendAndReceiveBehav(iq, getContents)

        if self.myAgent._running:
            self.myAgent.addBehaviour(b, t)
            b.join()
        else:
            self.myAgent.runBehaviourOnce(b, t)

        return b.result

    class _sendAndReceiveBehav(OneShotBehaviour):
            def __init__(self, iq, getContents):
                OneShotBehaviour.__init__(self)
                self.iq = iq
                self.getContents = getContents
                self.timeout = 15
                self.result = (None, None)

            def _process(self):
                #print 'Sending ', str(self.iq)
                self.myAgent.send(self.iq)
                #Wait for the answer
                msg = self._receive(block=True, timeout=self.timeout)
                #print 'Received ', str(msg)
                if msg is None:
                    #Timeout
                    self.result = ('error', ['timeout'])
                    return
                if msg['type'] == 'error':
                    errors = []
                    for error in msg.getTag('error').getChildren():
                        if error.getName() == 'text':
                            continue
                        errors.append(error.getName())
                    self.result = ('error', errors)
                    return
                if msg['type'] == 'result':
                    self.result = ('ok', self.getContents(msg))
                    return

                self.result = ('error', ['unknown'])
                return

    def publish(self, node, event=None):
        """
        Publishes an item to a given node.

        XXX: 'node' here is not an XML node, but the attribute for <publish>

        @type node: string
        @param node: The ID of the pubsub node to publish
        @type event: Event
        @param event: Content to publish
        @rtype: (string , list[string])
        @return: A tuple with the type of answer ('ok','error') and information
            about the answer. In case of 'error', a list with the errors. In case of
            'ok' the name of the created node.
        """
        iq = Iq(
            typ='set',
                queryNS=None,
                attrs={},
                frm=self._client
        )

        pubsub_node = Node(tag='pubsub', attrs={'xmlns': NS_PUBSUB})
        publish_node = Node(tag='publish', attrs={'node': node})
        item_node = Node(tag='item')
        if event is not None:
            item_node.addChild(node=event)
            publish_node.addChild(node=item_node)
        pubsub_node.addChild(node=publish_node)
        iq.addChild(node=pubsub_node)

        def getContents(msg):
            node_publish = msg.getTag('pubsub').getTag('publish')
            #XXX: Server implementation always returns the item id, but XEP-60 does
            #   vim snot require it
            return [node_publish['node'], node_publish.getTag('item')['id']]

        return self._sendAndReceive(iq, getContents)

    def subscribe(self, node, server=None, jid=None):
        """
        Subscribes to the selected node

        @type node: string
        @param node: id of the node to delete
        @type server: string
        @param server: PubSub server
        @rtype: (string , list[string])
        @return: A tuple with the type of answer ('ok','error') and information
            about the answer. In case of 'error', a list with the errors. In case of
            'ok', an empty list.

        """

        if server is None:
            server = self._server

        if jid is None:
            jid = self._client

        iq = Iq(
            typ='set',
            queryNS=None,
            attrs={},
            frm=self._client,
            to=server
        )

        pubsub_node = Node(tag='pubsub', attrs={'xmlns': NS_PUBSUB})
        subscribe_node = Node(tag='subscribe', attrs={'node': node, 'jid': jid})
        pubsub_node.addChild(node=subscribe_node)
        iq.addChild(node=pubsub_node)

        return self._sendAndReceive(iq, lambda msg: [])

    def unsubscribe(self, node, server=None, jid=None):
        """
        Unsubscribe from the selected node

        @type node: string
        @param node: id of the node to unsubscribe
        @type server: string
        @param server: PubSub server
        @rtype: (string , list[string])
        @return: A tuple with the type of answer ('ok','error') and information
            about the answer. In case of 'error', a list with the errors. In case of
            'ok' an empty list.

        """

        if server is None:
            server = self._server

        if jid is None:
            jid = self._client

        iq = Iq(
            typ='set',
            queryNS=None,
            attrs={},
            frm=self._client,
            to=server
        )

        pubsub_node = Node(tag='pubsub', attrs={'xmlns': NS_PUBSUB_OWNER})
        unsubscribe_node = Node(tag='unsubscribe', attrs={'node': node, 'jid': jid})
        pubsub_node.addChild(node=unsubscribe_node)
        iq.addChild(node=pubsub_node)
        return self._sendAndReceive(iq, lambda msg: [])

    def createNode(self, node, server=None, type='leaf', parent=None, access=None):
        """
        Creates a node with the specified parameters.

        @type node: string
        @param node: The ID of the node to create
        @type server: string
        @param server: PubSub server
        @type type: string
        @param type: Type of the node: 'leaf' or 'collection'
        @type parent: string
        @param parent: id of the parent node. None if parent is root
        @type access: string
        @param acccess: Access model of the node
        @rtype: (string , list[string])
        @return: A tuple with the type of answer ('ok','error') and information
            about the answer. In case of 'error', a list with the errors. In case of
            'ok' the name of the created node.
        """
        #TODO: Add suport for node configuration (RECOMMENDED in XEP-60)
        if server is None:
            server = self._server

        iq = Iq(
            typ='set',
            queryNS=None,
            attrs={},
            frm=self._client,
            to=server
        )

        pubsub_node = Node(tag='pubsub', attrs={'xmlns': NS_PUBSUB})
        create_node = Node(tag='create', attrs={} if node is None else {'node': node})

        pubsub_node.addChild(node=create_node)
        iq.addChild(node=pubsub_node)
        if parent is not None or type == 'collection' or access is not None:
            field_nodes = []
            configure_node = Node(tag='configure')
            field_nodes.append(DataField('FORM_TYPE', NS_PUBSUB + '#node_config', 'hidden'))
            if parent is not None:
                field_nodes.append(DataField('pubsub#collection', parent))
                # <field var='pubsub#collection'><value>announcements</value></field>
            if type == 'collection':
                field_nodes.append(DataField('pubsub#node_type', 'collection'))
            if access is not None:
                field_nodes.append(DataField('pubsub#access_model', access))
            x_node = DataForm(typ='submit', data=field_nodes)
            configure_node.addChild(x_node)
            pubsub_node.addChild(configure_node)

        return self._sendAndReceive(iq, lambda msg: [msg.getTag('pubsub').getTag('create')['node']])

    def createInstantNode(self, server=None, type='leaf', parent=None, access=None):
        """
        Creates an instant node without a name. The server will generate id.
        """

        if server is None:
            server = self._server

        return createNode(self, None, server, type, parent, access)

    def deleteNode(self, node, server=None):
        """
        Deletes the selected node.

        @type node: string
        @param node: id of the node to delete
        @type server: string
        @param server: PubSub server
        @rtype: (string , list[string])
        @return: A tuple with the type of answer ('ok','error') and information
            about the answer. In case of 'error', a list with the errors. In case of
            'ok' an empty list.


        """

        #TODO: A method to redirect the subscriptions to the node to another one COULD be implemented

        if server is None:
            server = self._server

        iq = Iq(
            typ='set',
            queryNS=None,
            attrs={},
            frm=self._client,
            to=server,
        )

        pubsub_node = Node(tag='pubsub', attrs={'xmlns': NS_PUBSUB_OWNER})
        pubsub_node.addChild(name='delete', attrs={'node': node})
        iq.addChild(node=pubsub_node)

        return self._sendAndReceive(iq, lambda msg: [])
