import aioxmpp
from aioxmpp import PresenceState, PresenceShow


class ContactNotFound(Exception):
    pass


class PresenceManager(object):
    def __init__(self, agent):
        self.agent = agent
        self.client = agent.client
        self.roster = self.client.summon(aioxmpp.RosterClient)
        self.presenceclient = self.client.summon(aioxmpp.PresenceClient)
        self.presenceserver = self.client.summon(aioxmpp.PresenceServer)

        self._contacts = {}

        self.approve_all = False

        self.presenceclient.on_bare_available.connect(self._on_bare_available)
        self.presenceclient.on_available.connect(self._on_available)
        self.presenceclient.on_bare_unavailable.connect(self._on_bare_unavailable)
        self.presenceclient.on_unavailable.connect(self._on_unavailable)
        self.presenceclient.on_changed.connect(self._on_changed)

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

    def is_available(self):
        """
        Returns the available flag from the state
        :return: wether the agent is available or not
        :rtype: bool
        """
        return self.state.available

    def set_available(self, show=None):
        """
        Sets the agent availability to True.
        :param show: the show state of the presence (optional)
        :type show: :class:`aioxmpp.PresenceShow`
        """
        show = self.state.show if show is None else show
        self.set_presence(PresenceState(available=True, show=show))

    def set_unavailable(self):
        """
        Sets the agent availability to False.
        """
        show = PresenceShow.NONE
        self.set_presence(PresenceState(available=False, show=show))

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
        for jid, item in self.roster.items.items():
            try:
                self._contacts[jid.bare()].update(item.export_as_json())
            except KeyError:
                self._contacts[jid.bare()] = item.export_as_json()

        return self._contacts

    def get_contact(self, jid):
        """
        Returns a contact
        :param jid: jid of the contact
        :type jid: :class:`aioxmpp.JID`
        :return: the roster of contacts
        :rtype: :class:`dict`
        """
        try:
            return self.get_contacts()[jid.bare()]
        except KeyError:
            raise ContactNotFound
        except AttributeError:
            raise AttributeError("jid must be an aioxmpp.JID object")

    def _update_roster_with_presence(self, stanza):
        if stanza.from_.bare() == self.agent.jid.bare():
            return
        try:
            self._contacts[stanza.from_.bare()].update({"presence": stanza})
        except KeyError:
            self._contacts[stanza.from_.bare()] = {"presence": stanza}

    def subscribe(self, peer_jid):
        """
        Asks for subscription
        :param peer_jid: the JID you ask for subscriptiion
        :type peer_jid: :class:`str`
        """
        self.roster.subscribe(aioxmpp.JID.fromstr(peer_jid).bare())

    def unsubscribe(self, peer_jid):
        """
        Asks for unsubscription
        :param peer_jid: the JID you ask for unsubscriptiion
        :type peer_jid: :class:`str`
        """
        self.roster.unsubscribe(aioxmpp.JID.fromstr(peer_jid).bare())

    def approve(self, peer_jid):
        """
        Approve a subscription request from jid
        :param peer_jid: the JID to approve
        :type peer_jid: :class:`str`
        """
        self.roster.approve(aioxmpp.JID.fromstr(peer_jid).bare())

    def _on_bare_available(self, stanza):
        self._update_roster_with_presence(stanza)
        self.on_available(str(stanza.from_), stanza)

    def _on_available(self, full_jid, stanza):
        self._update_roster_with_presence(stanza)
        self.on_available(str(stanza.from_), stanza)

    def _on_unavailable(self, full_jid, stanza):
        self._update_roster_with_presence(stanza)
        self.on_unavailable(str(stanza.from_), stanza)

    def _on_bare_unavailable(self, stanza):
        self._update_roster_with_presence(stanza)
        self.on_unavailable(str(stanza.from_), stanza)

    def _on_changed(self, from_, stanza):
        self._update_roster_with_presence(stanza)

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

    def on_subscribe(self, peer_jid):
        """
        Callback called when a subscribe query is received.
        To ve overloaded by user.
        :param peer_jid: the JID of the agent asking for subscription
        :type peer_jid: :class:`str`
        """
        pass  # pragma: no cover

    def on_subscribed(self, peer_jid):
        """
        Callback called when a subscribed message is received.
        To ve overloaded by user.
        :param peer_jid: the JID of the agent that accepted subscription
        :type peer_jid: :class:`str`
        """
        pass  # pragma: no cover

    def on_unsubscribe(self, peer_jid):
        """
        Callback called when an unsubscribe query is received.
        To ve overloaded by user.
        :param peer_jid: the JID of the agent asking for unsubscription
        :type peer_jid: :class:`str`
        """
        pass  # pragma: no cover

    def on_unsubscribed(self, peer_jid):
        """
        Callback called when an unsubscribed message is received.
        To ve overloaded by user.
        :param peer_jid: the JID of the agent that unsubscribed
        :type peer_jid: :class:`str`
        """
        pass  # pragma: no cover

    def on_available(self, peer_jid, stanza):
        """
        Callback called when a contact becomes available.
        To ve overloaded by user.
        :param peer_jid: the JID of the agent that is available
        :type peer_jid: :class:`str`
        :param stanza: The presence message containing type, show, priority and status values.
        :type stanza: :class:`aioxmpp.Presence`
        """
        pass  # pragma: no cover

    def on_unavailable(self, peer_jid, stanza):
        """
        Callback called when a contact becomes unavailable.
        To ve overloaded by user.
        :param peer_jid: the JID of the agent that is unavailable
        :type peer_jid: :class:`str`
        :param stanza: The presence message containing type, show, priority and status values.
        :type stanza: :class:`aioxmpp.Presence`
        """
        pass  # pragma: no cover
