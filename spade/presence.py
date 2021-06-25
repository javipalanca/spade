import aioxmpp
from aioxmpp import PresenceState, PresenceShow


class ContactNotFound(Exception):
    """ """

    pass


class PresenceManager(object):
    """ """

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
        The currently set presence state (as aioxmpp.PresenceState)
        which is broadcast when the client connects and when the presence is
        re-emitted.

        This attribute cannot be written. It does not reflect the actual
        presence seen by others. For example when the client is in fact
        offline, others will see unavailable presence no matter what is set
        here.

        Returns:
            aioxmpp.PresenceState: the presence state of the agent
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

        Returns:
            dict: a dict with the status in different languages (default key is None)
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

        Returns:
            int: the priority of the connection
        """
        return self.presenceserver.priority

    def is_available(self):
        """
        Returns the available flag from the state

        Returns:
          bool: wether the agent is available or not

        """
        return self.state.available

    def set_available(self, show=PresenceShow.NONE):
        """
        Sets the agent availability to True.

        Args:
          show (aioxmpp.PresenceShow, optional): the show state of the presence (Default value = PresenceShow.NONE)

        """
        show = self.state.show if show is PresenceShow.NONE else show
        self.set_presence(PresenceState(available=True, show=show))

    def set_unavailable(self):
        """Sets the agent availability to False."""
        show = PresenceShow.NONE
        self.set_presence(PresenceState(available=False, show=show))

    def set_presence(self, state=None, status=None, priority=None):
        """
        Change the presence broadcast by the client.
        If the client is currently connected, the new presence is broadcast immediately.

        Args:
          state(aioxmpp.PresenceState, optional): New presence state to broadcast (Default value = None)
          status(dict or str, optional): New status information to broadcast (Default value = None)
          priority (int, optional): New priority for the resource (Default value = None)

        """
        state = state if state is not None else self.state
        status = status if status is not None else self.status
        priority = priority if priority is not None else self.priority
        self.presenceserver.set_presence(state, status, priority)

    def get_contacts(self):
        """
        Returns list of contacts

        Returns:
          dict: the roster of contacts

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

        Args:
          jid (aioxmpp.JID): jid of the contact

        Returns:
          dict: the roster of contacts

        """
        try:
            return self.get_contacts()[jid.bare()]
        except KeyError:
            raise ContactNotFound
        except AttributeError:
            raise AttributeError("jid must be an aioxmpp.JID object")

    def _update_roster_with_presence(self, stanza):
        """ """
        if stanza.from_.bare() == self.agent.jid.bare():
            return
        try:
            self._contacts[stanza.from_.bare()].update({"presence": stanza})
        except KeyError:
            self._contacts[stanza.from_.bare()] = {"presence": stanza}

    def subscribe(self, peer_jid):
        """
        Asks for subscription

        Args:
          peer_jid (str): the JID you ask for subscriptiion

        """
        self.roster.subscribe(aioxmpp.JID.fromstr(peer_jid).bare())

    def unsubscribe(self, peer_jid):
        """
        Asks for unsubscription

        Args:
          peer_jid (str): the JID you ask for unsubscriptiion

        """
        self.roster.unsubscribe(aioxmpp.JID.fromstr(peer_jid).bare())

    def approve(self, peer_jid):
        """
        Approve a subscription request from jid

        Args:
          peer_jid (str): the JID to approve

        """
        self.roster.approve(aioxmpp.JID.fromstr(peer_jid).bare())

    def _on_bare_available(self, stanza):
        """ """
        self._update_roster_with_presence(stanza)
        self.on_available(str(stanza.from_), stanza)

    def _on_available(self, full_jid, stanza):
        """ """
        self._update_roster_with_presence(stanza)
        self.on_available(str(stanza.from_), stanza)

    def _on_unavailable(self, full_jid, stanza):
        """ """
        self._update_roster_with_presence(stanza)
        self.on_unavailable(str(stanza.from_), stanza)

    def _on_bare_unavailable(self, stanza):
        """ """
        self._update_roster_with_presence(stanza)
        self.on_unavailable(str(stanza.from_), stanza)

    def _on_changed(self, from_, stanza):
        """ """
        self._update_roster_with_presence(stanza)

    def _on_subscribe(self, stanza):
        """ """
        if self.approve_all:
            self.roster.approve(stanza.from_.bare())
        else:
            self.on_subscribe(str(stanza.from_))

    def _on_subscribed(self, stanza):
        """ """
        self.on_subscribed(str(stanza.from_))

    def _on_unsubscribe(self, stanza):
        """ """
        if self.approve_all:
            self.client.stream.enqueue(
                aioxmpp.Presence(
                    type_=aioxmpp.structs.PresenceType.UNSUBSCRIBED,
                    to=stanza.from_.bare(),
                )
            )
        else:
            self.on_unsubscribe(str(stanza.from_))

    def _on_unsubscribed(self, stanza):
        """ """
        self.on_unsubscribed(str(stanza.from_))

    def on_subscribe(self, peer_jid):
        """
        Callback called when a subscribe query is received.
        To ve overloaded by user.

        Args:
          peer_jid (str): the JID of the agent asking for subscription

        """
        pass  # pragma: no cover

    def on_subscribed(self, peer_jid):
        """
        Callback called when a subscribed message is received.
        To ve overloaded by user.

        Args:
          peer_jid (str): the JID of the agent that accepted subscription

        """
        pass  # pragma: no cover

    def on_unsubscribe(self, peer_jid):
        """
        Callback called when an unsubscribe query is received.
        To ve overloaded by user.

        Args:
          peer_jid (str): the JID of the agent asking for unsubscription

        """
        pass  # pragma: no cover

    def on_unsubscribed(self, peer_jid):
        """
        Callback called when an unsubscribed message is received.
        To ve overloaded by user.

        Args:
          peer_jid (str): the JID of the agent that unsubscribed

        """
        pass  # pragma: no cover

    def on_available(self, peer_jid, stanza):
        """
        Callback called when a contact becomes available.
        To ve overloaded by user.

        Args:
          peer_jid (str): the JID of the agent that is available
          stanza (aioxmpp.Presence): The presence message containing type, show, priority and status values.

        """
        pass  # pragma: no cover

    def on_unavailable(self, peer_jid, stanza):
        """
        Callback called when a contact becomes unavailable.
        To ve overloaded by user.

        Args:
          peer_jid (str): the JID of the agent that is unavailable
          stanza (aioxmpp.Presence): The presence message containing type, show, priority and status values.

        """
        pass  # pragma: no cover
