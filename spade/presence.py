import aioxmpp


class PresenceManager(object):
    def __init__(self, agent):
        self.agent = agent
        self.client = agent.client
        self.roster = self.client.summon(aioxmpp.RosterClient)
        self.presenceclient = self.client.summon(aioxmpp.PresenceClient)
        self.presenceserver = self.client.summon(aioxmpp.PresenceServer)

        self.approve_all = False

        self.presenceclient.on_bare_available.connect(self._on_available)
        self.presenceclient.on_bare_unavailable.connect(self._on_unavailable)

        self.roster.on_subscribe.connect(self._on_subscribe)
        self.roster.on_subscribed.connect(self._on_subscribed)
        self.roster.on_unsubscribe.connect(self._on_unsubscribe)
        self.roster.on_unsubscribed.connect(self._on_unsubscribed)

    @property
    def state(self):
        """
        The currently set presence state (as :class:`aioxmpp.PresenceState`)
        which is broadcast when the client connects and when the presence is
        re-emitted.

        This attribute cannot be written. It does not reflect the actual
        presence seen by others. For example when the client is in fact
        offline, others will see unavailable presence no matter what is set
        here.
        """
        return self.presenceserver.state

    @property
    def status(self):
        """
        The currently set textual presence status which is broadcast when the
        client connects and when the presence is re-emitted.

        This attribute cannot be written. It does not reflect the actual
        presence seen by others. For example when the client is in fact
        offline, others will see unavailable presence no matter what is set
        here.
        """
        return self.presenceserver.status

    @property
    def priority(self):
        """
        The currently set priority which is broadcast when the client connects
        and when the presence is re-emitted.

        This attribute cannot be written. It does not reflect the actual
        presence seen by others. For example when the client is in fact
        offline, others will see unavailable presence no matter what is set
        here.
        """
        return self.presenceserver.priority

    def set_presence(self, state=None, status=None, priority=None):
        """
        Change the presence broadcast by the client.

        :param state: New presence state to broadcast
        :type state: :class:`aioxmpp.PresenceState`
        :param status: New status information to broadcast
        :type status: :class:`dict` or :class:`str`
        :param priority: New priority for the resource
        :type priority: :class:`int`

        If the client is currently connected, the new presence is broadcast
        immediately.
        """
        state = state if state is not None else self.state
        status = status if status is not None else self.status
        priority = priority if priority is not None else self.priority
        self.presenceserver.set_presence(state, status, priority)

    def get_contacts(self):
        """
        Returns list of contacts
        :return: the roster of contacts
        :rtype: :class:`dict`
        """
        return self.roster.items

    def subscribe(self, jid):
        """
        Asks for subscription
        :param jid: the JID you ask for subscriptiion
        :type jid: :class:`str`
        """
        self.roster.subscribe(aioxmpp.JID.fromstr(jid).bare())

    def unsubscribe(self, jid):
        """
        Asks for unsubscription
        :param jid: the JID you ask for unsubscriptiion
        :type jid: :class:`str`
        """
        self.roster.unsubscribe(aioxmpp.JID.fromstr(jid).bare())

    def approve(self, jid):
        """
        Approve a subscription request from jid
        :param jid: the JID to approve
        :type jid: :class:`str`
        """
        self.roster.approve(aioxmpp.JID.fromstr(jid).bare())

    def _on_available(self, stanza):
        self.on_available(str(stanza.from_), stanza)

    def _on_unavailable(self, stanza):
        self.on_unavailable(str(stanza.from_), stanza)

    def _on_subscribe(self, stanza):
        if self.approve_all:
            self.roster.approve(stanza.from_.bare())
        else:
            self.on_subscribe(str(stanza.from_))

    def _on_subscribed(self, stanza):
        self.on_subscribed(str(stanza.from_))

    def _on_unsubscribe(self, stanza):
        if self.approve_all:
            self.client.stream.enqueue(
                aioxmpp.Presence(type_=aioxmpp.structs.PresenceType.UNSUBSCRIBED,
                                 to=stanza.from_.bare())
            )
        else:
            self.on_unsubscribe(str(stanza.from_))

    def _on_unsubscribed(self, stanza):
        self.on_unsubscribed(str(stanza.from_))

    def on_subscribe(self, jid):
        """
        Callback called when a subscribe query is received.
        To ve overloaded by user.
        :param jid: the JID of the agent asking for subscription
        :type jid: :class:`str`
        """
        pass

    def on_subscribed(self, jid):
        """
        Callback called when a subscribed message is received.
        To ve overloaded by user.
        :param jid: the JID of the agent that accepted subscription
        :type jid: :class:`str`
        """
        pass

    def on_unsubscribe(self, jid):
        """
        Callback called when an unsubscribe query is received.
        To ve overloaded by user.
        :param jid: the JID of the agent asking for unsubscription
        :type jid: :class:`str`
        """
        pass

    def on_unsubscribed(self, jid):
        """
        Callback called when an unsubscribed message is received.
        To ve overloaded by user.
        :param jid: the JID of the agent that unsubscribed
        :type jid: :class:`str`
        """
        pass

    def on_available(self, jid, stanza):
        """
        Callback called when a contact becomes available.
        To ve overloaded by user.
        :param jid: the JID of the agent that is available
        :type jid: :class:`str`
        :param stanza: The presence message containing type, show, priority and status values.
        :type stanza: :class:`aioxmpp.Presence`
        """
        pass

    def on_unavailable(self, jid, stanza):
        """
        Callback called when a contact becomes unavailable.
        To ve overloaded by user.
        :param jid: the JID of the agent that is unavailable
        :type jid: :class:`str`
        :param stanza: The presence message containing type, show, priority and status values.
        :type stanza: :class:`aioxmpp.Presence`
        """
        pass
