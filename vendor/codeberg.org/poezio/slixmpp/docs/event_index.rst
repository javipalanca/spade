Event Index
===========

Slixmpp relies on events and event handlers to act on received data from
the server. Some of those events come from the very base of Slixmpp such
as :class:`~.BaseXMPP` or :class:`~.XMLStream`, while most of them are
emitted from plugins which add their own listeners.

There are often multiple events running for a single stanza, with
different levels of granularity, so code must take care of not
processing the same stanza twice.


.. glossary::
    :sorted:

    connected
        - **Data:** ``{}``
        - **Source:** :py:class:`~.xmlstream.XMLstream`

        Signal that a connection has been made with the XMPP server, but a session
        has not yet been established.

    connection_failed
        - **Data:** ``{}`` or ``Failure Stanza`` if available
        - **Source:** :py:class:`~.xmlstream.XMLstream`

        Signal that a connection can not be established after number of attempts.

    changed_status
        - **Data:** :py:class:`~.Presence`
        - **Source:** :py:class:`~.roster.item.RosterItem`

        Triggered when a presence stanza is received from a JID with a show type
        different than the last presence stanza from the same JID.

    changed_subscription
        - **Data:** :py:class:`~.Presence`
        - **Source:** :py:class:`~.BaseXMPP`

        Triggered whenever a presence stanza with a type of ``subscribe``,
        ``subscribed``, ``unsubscribe``, or ``unsubscribed`` is received.

        Note that if the values ``xmpp.auto_authorize`` and ``xmpp.auto_subscribe``
        are set to ``True`` or ``False``, and not ``None``, then  will
        either accept or reject all subscription requests before your event handlers
        are called. Set these values to ``None`` if you wish to make more complex
        subscription decisions.

    chatstate_active
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0085`

        When a message containing an ``<active/>`` chatstate is received.

    chatstate_composing
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0085`

        When a message containing a ``<composing/>`` chatstate is received.

    chatstate_gone
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0085`

        When a message containing a ``<gone/>`` chatstate is received.

    chatstate_inactive
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0085`

        When a message containing an ``<inactive/>`` chatstate is received.

    chatstate_paused
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0085`

        When a message containing a ``<paused/>`` chatstate is received.

    disco_info
        - **Data:** :py:class:`~.DiscoInfo`
        - **Source:** :py:class:`~.disco.XEP_0030`

        Triggered whenever a ``disco#info`` result stanza is received.

    disco_items
        - **Data:** :py:class:`~.DiscoItems`
        - **Source:** :py:class:`~.disco.XEP_0030`

        Triggered whenever a ``disco#items`` result stanza is received.

    disconnected
        - **Data:** ``Union[str, Exception]``, the reason for the disconnect (if any). If a textual reason is not provided and an exception is the cause, it will be given to the event handler.
        - **Source:** :py:class:`~.XMLstream`

        Signal that the connection with the XMPP server has been lost.

    failed_auth
        - **Data:** ``{}``
        - **Source:** :py:class:`~.ClientXMPP`, :py:class:`~.XEP_0078`

        Signal that the server has rejected the provided login credentials.

    gmail_notify
        - **Data:** ``{}``
        - **Source:** :py:class:`~.plugins.gmail_notify.gmail_notify`

        Signal that there are unread emails for the Gmail account associated with the current XMPP account.

    gmail_messages
        - **Data:** :py:class:`~.Iq`
        - **Source:** :py:class:`~.plugins.gmail_notify.gmail_notify`

        Signal that there are unread emails for the Gmail account associated with the current XMPP account.

    got_online
        - **Data:** :py:class:`~.Presence`
        - **Source:** :py:class:`~.roster.item.RosterItem`

        If a presence stanza is received from a JID which was previously marked as
        offline, and the presence has a show type of '``chat``', '``dnd``', '``away``',
        or '``xa``', then this event is triggered as well.

    got_offline
        - **Data:** :py:class:`~.Presence`
        - **Source:** :py:class:`~.roster.item.RosterItem`

        Signal that an unavailable presence stanza has been received from a JID.

    groupchat_invite
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0045`

        When a Mediated MUC invite is received.


    groupchat_direct_invite
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0249`

        When a Direct MUC invite is received.

    groupchat_message
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0045`

        Triggered whenever a message is received from a multi-user chat room.

    groupchat_presence
        - **Data:** :py:class:`~.Presence`
        - **Source:** :py:class:`~.XEP_0045`

        Triggered whenever a presence stanza is received from a user in a multi-user chat room.

    groupchat_subject
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0045`

        Triggered whenever the subject of a multi-user chat room is changed, or announced when joining a room.

    killed
        - **Data:** ``{}``
        - **Source:** :class:`~.XMLStream`

        When the stream is aborted.

    message
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`BaseXMPP <.BaseXMPP>`

        Makes the contents of message stanzas that include <body> tags available
        whenever one is received.
        Be sure to check the message type to handle error messages appropriately.

    message_error
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`BaseXMPP <.BaseXMPP>`

        Makes the contents of message stanzas available whenever one is received.
        Only handler messages with an ``error`` type.

    message_form
        - **Data:** :py:class:`~.Form`
        - **Source:** :py:class:`~.XEP_0004`

        Currently the same as :term:`message_xform`.

    message_xform
        - **Data:** :py:class:`~.Form`
        - **Source:** :py:class:`~.XEP_0004`

        Triggered whenever a data form is received inside a message.

    muc::[room]::got_offline
        - **Data:** :py:class:`~.Presence`
        - **Source:** :py:class:`~.XEP_0045`
        - **Name parameters:** ``room``, the room this is coming from.

        Triggered whenever we receive an unavailable presence from a MUC occupant.

    muc::[room]::got_online
        - **Data:** :py:class:`~.Presence`
        - **Source:** :py:class:`~.XEP_0045`
        - **Name parameters:** ``room``, the room this is coming from.

        Triggered whenever we receive a presence from a MUC occupant
        we do not have in the local cache.

    muc::[room]::message
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0045`
        - **Name parameters:** ``room``, the room this is coming from.

        Triggered whenever we receive a message from a MUC we are in.

    muc::[room]::presence
        - **Data:** :py:class:`~.Presence`
        - **Source:** :py:class:`~.XEP_0045`
        - **Name parameters:** ``room``, the room this is coming from.

    muc::[room]::self-presence
        - **Data:** :class:`~.Presence`
        - **Source:** :class:`~.XEP_0045`
        - **Name parameters:** ``room``, the room this is coming from.

        Triggered whenever we receive a presence with status code ``110``
        (for example on MUC join, or nick change).

    muc::[room]::presence-error
        - **Data:** :class:`~.Presence`
        - **Source:** :class:`~.XEP_0045`
        - **Name parameters:** ``room``, the room this is coming from.

        Triggered whenever we receive a presence of ``type="error"`` from
        a MUC.

    presence_available
        - **Data:** :py:class:`~.Presence`
        - **Source:** :py:class:`~.BaseXMPP`

        A presence stanza with a type of '``available``' is received.

    presence_error
        - **Data:** :py:class:`~.Presence`
        - **Source:** :py:class:`~.BaseXMPP`

        A presence stanza with a type of '``error``' is received.

    presence_form
        - **Data:** :py:class:`~.Form`
        - **Source:** :py:class:`~.XEP_0004`

        This event is present in the XEP-0004 plugin code, but is currently not used.

    presence_probe
        - **Data:** :py:class:`~.Presence`
        - **Source:** :py:class:`~.BaseXMPP`

        A presence stanza with a type of '``probe``' is received.

    presence_subscribe
        - **Data:** :py:class:`~.Presence`
        - **Source:** :py:class:`~.BaseXMPP`

        A presence stanza with a type of '``subscribe``' is received.

    presence_subscribed
        - **Data:** :py:class:`~.Presence`
        - **Source:** :py:class:`~.BaseXMPP`

        A presence stanza with a type of '``subscribed``' is received.

    presence_unavailable
        - **Data:** :py:class:`~.Presence`
        - **Source:** :py:class:`~.BaseXMPP`

        A presence stanza with a type of '``unavailable``' is received.

    presence_unsubscribe
        - **Data:** :py:class:`~.Presence`
        - **Source:** :py:class:`~.BaseXMPP`

        A presence stanza with a type of '``unsubscribe``' is received.

    presence_unsubscribed
        - **Data:** :py:class:`~.Presence`
        - **Source:** :py:class:`~.BaseXMPP`

        A presence stanza with a type of '``unsubscribed``' is received.

    roster_update
        - **Data:** :py:class:`~.Roster`
        - **Source:** :py:class:`~.ClientXMPP`

        An IQ result containing roster entries is received.

    sent_presence
        - **Data:** ``{}``
        - **Source:** :py:class:`~.roster.multi.Roster`

        Signal that an initial presence stanza has been written to the XML stream.

    session_end
        - **Data:** ``{}``
        - **Source:** :py:class:`~.xmlstream.XMLstream`

        Signal that a connection to the XMPP server has been lost and the current
        stream session has ended. Equivalent to :term:`disconnected`, unless the
        `XEP-0198: Stream Management <http://xmpp.org/extensions/xep-0198.html>`_
        plugin is loaded.

        Plugins that maintain session-based state should clear themselves when
        this event is fired.

    session_start
        - **Data:** ``{}``
        - **Source:** :py:class:`.ClientXMPP`,
          :py:class:`~.ComponentXMPP`,
          :py:class:`~.XEP-0078`

        Signal that a connection to the XMPP server has been made and a session has been established.

    session_resumed
        - **Data:** ``{}``
        - **Source:** :class:`~.XEP_0198`

        When Stream Management manages to resume an ongoing session
        after reconnecting.

    socket_error
        - **Data:** ``Socket`` exception object
        - **Source:** :py:class:`~.xmlstream.XMLstream`

    stream_error
        - **Data:** :py:class:`~.StreamError`
        - **Source:** :py:class:`~.BaseXMPP`

    reactions
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0444`

        When a message containing reactions is received.

    carbon_received
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0280`

        When a carbon for a received message is received.

    carbon_sent
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0280`

        When a carbon for a sent message (from another of our resources) is received.

    marker
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0333`

        Whenever a chat marker is received (any of them).

    marker_received
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0333`

        Whenever a ``<received/>`` chat marker is received.

    marker_displayed
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0333`

        Whenever a ``<displayed/>`` chat marker is received.

    marker_acknowledged
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0333`

        Whenever an ``<acknowledged/>`` chat marker is received.

    attention
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0224`

        Whenever a message containing an attention payload is received.

    message_correction
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0308`

        Whenever a message containing a correction is received.

    receipt_received
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0184`

        Whenever a message receipt is received.

    jingle_message_propose
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0353`

    jingle_message_retract
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0353`

    jingle_message_accept
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0353`

    jingle_message_proceed
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0353`

    jingle_message_reject
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0353`

    room_activity
        - **Data:** :py:class:`~.Presence`
        - **Source:** :py:class:`~.XEP_0437`

        When a room activity stanza is received by a client.

    room_activity_bare
        - **Data:** :py:class:`~.Presence`
        - **Source:** :py:class:`~.XEP_0437`

        When an empty room activity stanza is received
        (typically by a component).

    sm_enabled
        - **Data:** :py:class:`~.stanza.Enabled`
        - **Source:** :py:class:`~.XEP_0198`

        When Stream Management is successfully enabled.

    sm_disabled
        - **Data:** ``{}``
        - **Source:** :py:class:`~.XEP_0198`

        When Stream Management gets disabled (when disconnected).

    ibb_stream_start
        - **Data:** :py:class:`~.stream.IBBBytestream`
        - **Source:** :py:class:`~.XEP_0047`

        When a stream is successfully opened with a remote peer.

    ibb_stream_end
        - **Data:** :py:class:`~.stream.IBBBytestream`
        - **Source:** :py:class:`~.XEP_0047`

        When an opened stream closes.

    ibb_stream_data
        - **Data:** :py:class:`~.stream.IBBBytestream`
        - **Source:** :py:class:`~.XEP_0047`

        When data is received on an opened stream.

    stream:[stream id]:[peer jid]
        - **Data:** :py:class:`~.stream.IBBBytestream`
        - **Source:** :py:class:`~.XEP_0047`
        - **Name parameters:** ``stream id``, the id of the stream,
          and ``peer jid`` the JID of the entity the stream is established
          with.

        When a stream is opened (with specific sid and jid parameters).

    command
        - **Data:** :py:class:`~.Iq`
        - **Source:** :py:class:`~.XEP_0050`

        When an ad-hoc command is received.

    command_[action]
        - **Data:** :py:class:`~.Iq`
        - **Source:** :py:class:`~.XEP_0050`
        - **Name parameters:** ``action``, the action referenced in
          the command payload.

        When a command with the specific action is received.

    pubsub_publish
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0060`

        When a pubsub event of type ``publish`` is received.

    pubsub_retract
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0060`

        When a pubsub event of type ``retract`` is received.

    pubsub_purge
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0060`

        When a pubsub event of type ``purge`` is received.

    pubsub_delete
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0060`

        When a pubsub event of type ``delete`` is received.

    pubsub_config
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0060`

        When a pubsub event of type ``config`` is received.

    pubsub_subscription
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0060`

        When a pubsub event of type ``subscription`` is received.

    call_invite
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0482`

    call_retract
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0482`

    call_reject
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0482`

    call_leave
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0482`

    call_left
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0482`

    muc_ping_changed
        - **Data:** ``dict(key: Tuple[JID, JID], previous: PingStatus, result: PingStatus)``
        - **Source:** :py:class:`~.XEP_0410`

    legacy_login
        - **Data:** :py:class:`~.Presence`
        - **Source:** :py:class:`~.XEP_0100`

    legacy_logout
        - **Data:** :py:class:`~.Presence`
        - **Source:** :py:class:`~.XEP_0100`

    legacy_presence_unavailable
        - **Data:** :py:class:`~.Presence`
        - **Source:** :py:class:`~.XEP_0100`

    legacy_message
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0100`

    gateway_message
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0100`

    moderated_message
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0425`

    retracted_message
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0424`


Dedicated PubSub Events
=======================

The :class:`~.XEP_0060` plugin (and :class:`~.XEP_0163` plugin, which uses
the former) allows other plugins to map specific namespaces in
PubSub notifications to a dedicated name prefix.


The current list of plugin prefixes is the following:

- ``bookmarks``: :class:`~.XEP_0048`
- ``user_location``: :class:`~.XEP_0080`
- ``avatar_metadata``: :class:`~.XEP_0084`
- ``avatar_data``: :class:`~.XEP_0084`
- ``user_mood``: :class:`~.XEP_0107`
- ``user_activity``: :class:`~.XEP_0108`
- ``user_tune``: :class:`~.XEP_0118`
- ``reachability``: :class:`~.XEP_0152`
- ``user_nick``: :class:`~.XEP_0172`
- ``user_gaming``: :class:`~.XEP_0196`
- ``mix_participant_info``: :class:`~.XEP_0369`
- ``mix_channel_info``: :class:`~.XEP_0369`


.. glossary::
    :sorted:


    [plugin]_publish
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0060`

        When a pubsub event of type ``publish`` is received.

    [plugin]_retract
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0060`

        When a pubsub event of type ``retract`` is received.

    [plugin]_purge
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0060`

        When a pubsub event of type ``purge`` is received.

    [plugin]_delete
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0060`

        When a pubsub event of type ``delete`` is received.

    [plugin]_config
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0060`

        When a pubsub event of type ``config`` is received.

    [plugin]_subscription
        - **Data:** :py:class:`~.Message`
        - **Source:** :py:class:`~.XEP_0060`

        When a pubsub event of type ``subscription`` is received.
