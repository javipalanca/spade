
# slixmpp.clientxmpp
# ~~~~~~~~~~~~~~~~~~~~
# This module provides XMPP functionality that
# is specific to client connections.
# Part of Slixmpp: The Slick XMPP Library
# :copyright: (c) 2011 Nathanael C. Fritz
# :license: MIT, see LICENSE for more details
import asyncio
import logging
from typing import Optional, Any, Callable, Tuple, Dict, Set, List

from slixmpp.jid import JID
from slixmpp.stanza import StreamFeatures, Iq
from slixmpp.basexmpp import BaseXMPP
from slixmpp.exceptions import XMPPError
from slixmpp.roster.single import RosterNode
from slixmpp.types import JidStr
from slixmpp.xmlstream import XMLStream
from slixmpp.xmlstream.stanzabase import StanzaBase
from slixmpp.xmlstream.matcher import StanzaPath, MatchXPath
from slixmpp.xmlstream.handler import Callback, CoroutineCallback


log = logging.getLogger(__name__)


class ClientXMPP(BaseXMPP):

    """
    Slixmpp's client class. (Use only for good, not for evil.)

    Typical use pattern:

    .. code-block:: python

        xmpp = ClientXMPP('user@server.tld/resource', 'password')
        # ... Register plugins and event handlers ...
        xmpp.connect()
        asyncio.get_event_loop().run_forever()

    :param jid: The JID of the XMPP user account.
    :param password: The password for the XMPP user account.
    :param plugin_config: A dictionary of plugin configurations.
    :param plugin_whitelist: A list of approved plugins that
                    will be loaded when calling
                    :meth:`~slixmpp.basexmpp.BaseXMPP.register_plugins()`.
    :param escape_quotes: **Deprecated.**
    """

    client_roster: RosterNode

    def __init__(self, jid: JidStr, password: str, plugin_config=None,
                 plugin_whitelist=None, escape_quotes=True, sasl_mech=None,
                 lang='en', **kwargs):
        if not plugin_whitelist:
            plugin_whitelist = []
        if not plugin_config:
            plugin_config = {}

        BaseXMPP.__init__(self, jid, 'jabber:client', **kwargs)

        self.escape_quotes = escape_quotes
        self.plugin_config = plugin_config
        self.plugin_whitelist = plugin_whitelist
        self.default_port = 5222
        self.default_domain = self.boundjid.host
        self.default_lang = lang

        self.credentials: Dict[str, str] = {}

        self.password = password

        self.stream_header = "<stream:stream to='%s' %s %s %s %s>" % (
                self.boundjid.host,
                "xmlns:stream='%s'" % self.stream_ns,
                "xmlns='%s'" % self.default_ns,
                "xml:lang='%s'" % self.default_lang,
                "version='1.0'")
        self.stream_footer = "</stream:stream>"

        self.features: Set[str] = set()
        self._stream_feature_handlers: Dict[str, Tuple[Callable, bool]] = {}
        self._stream_feature_order: List[Tuple[int, str]] = []

        self.tls_services = {'xmpps-client'}
        self.starttls_services = {'xmpp-client'}

        #TODO: Use stream state here
        self.authenticated = False
        self.sessionstarted = False
        self.bound = False
        self.bindfail = False

        self.add_event_handler('connected', self._reset_connection_state)
        self.add_event_handler('session_bind', self._handle_session_bind)
        self.add_event_handler('roster_update', self._handle_roster)

        self.register_stanza(StreamFeatures)

        self.register_handler(
            CoroutineCallback(
                'Stream Features',
                MatchXPath('{%s}features' % self.stream_ns),
                self._handle_stream_features,  # type: ignore
            )
        )

        def roster_push_filter(iq: StanzaBase) -> None:
            from_ = iq['from']
            if from_ and from_ != JID('') and from_ != self.boundjid.bare:
                reply = iq.reply()
                reply['type'] = 'error'
                reply['error']['type'] = 'cancel'
                reply['error']['code'] = 503
                reply['error']['condition'] = 'service-unavailable'
                reply.send()
                return
            self.event('roster_update', iq)
        self.register_handler(
                Callback('Roster Update',
                         StanzaPath('iq@type=set/roster'),
                         roster_push_filter))

        # Setup default stream features
        self.register_plugin('feature_starttls')
        self.register_plugin('feature_bind')
        self.register_plugin('feature_session')
        self.register_plugin('feature_rosterver')
        self.register_plugin('feature_preapproval')
        self.register_plugin('feature_mechanisms')

        if sasl_mech:
            self['feature_mechanisms'].use_mech = sasl_mech

    @property
    def password(self) -> str:
        return self.credentials.get('password', '')

    @password.setter
    def password(self, value: str) -> None:
        self.credentials['password'] = value

    def connect(self, host: Optional[str] = None, port: Optional[int] = None) -> asyncio.Future:
        """Connect to the XMPP server.

        When no address is given, a SRV lookup for the server will
        be attempted. If that fails, the server used in the JID
        will be used.

        :param host: A custom host to connect to (requires port as well)
        :param port: A custom port to connect to (requires host as well)
        """

        # If an address was provided, disable using DNS SRV lookup;
        # otherwise, use the domain from the client JID with the standard
        # XMPP client port and allow SRV lookup.
        if not (host and port):
            host, port = None, None

        self.init_plugins()

        return XMLStream.connect(self, host=host, port=port)

    def register_feature(self, name: str, handler: Callable, restart: bool = False, order: int = 5000) -> None:
        """Register a stream feature handler.

        :param name: The name of the stream feature.
        :param handler: The function to execute if the feature is received.
        :param restart: Indicates if feature processing should halt with
                        this feature. Defaults to ``False``.
        :param order: The relative ordering in which the feature should
                      be negotiated. Lower values will be attempted
                      earlier when available.
        """
        self._stream_feature_handlers[name] = (handler, restart)
        self._stream_feature_order.append((order, name))
        self._stream_feature_order.sort()

    def unregister_feature(self, name: str, order: int) -> None:
        if name in self._stream_feature_handlers:
            del self._stream_feature_handlers[name]
        self._stream_feature_order.remove((order, name))
        self._stream_feature_order.sort()

    def update_roster(self, jid: JID, **kwargs) -> None:
        """Add or change a roster item.

        :param jid: The JID of the entry to modify.
        :param name: The user's nickname for this JID.
        :param subscription: The subscription status. May be one of
                             ``'to'``, ``'from'``, ``'both'``, or
                             ``'none'``. If set to ``'remove'``,
                             the entry will be deleted.
        :param groups: The roster groups that contain this item.
        :param timeout: The length of time (in seconds) to wait
                        for a response before continuing if blocking
                        is used. Defaults to
                        :attr:`~slixmpp.xmlstream.xmlstream.XMLStream.response_timeout`.
        :param callback: Optional reference to a stream handler function.
                         Will be executed when the roster is received.
                         Implies ``block=False``.
        """
        current = self.client_roster[jid]

        name = kwargs.get('name', current['name'])
        subscription = kwargs.get('subscription', current['subscription'])
        groups = kwargs.get('groups', current['groups'])

        timeout = kwargs.get('timeout', None)
        callback = kwargs.get('callback', None)

        return self.client_roster.update(jid, name, subscription, groups,
                                         timeout, callback)

    def del_roster_item(self, jid):
        """Remove an item from the roster.

        This is done by setting its subscription status to ``'remove'``.

        :param jid: The JID of the item to remove.
        """
        return self.client_roster.remove(jid)

    def get_roster(self, callback=None, timeout=None):
        """Request the roster from the server.

        :param callback: Reference to a stream handler function. Will
                         be executed when the roster is received.
        """
        iq = self.Iq()
        iq['type'] = 'get'
        iq.enable('roster')
        if 'rosterver' in self.features:
            iq['roster']['ver'] = self.client_roster.version

        if callback is None:
            callback = lambda resp: self.event('roster_update', resp)
        else:
            orig_cb = callback
            def wrapped(resp):
                self.event('roster_update', resp)
                orig_cb(resp)
            callback = wrapped

        return iq.send(callback, timeout)

    def _reset_connection_state(self, event: Optional[Any] = None) -> None:
        #TODO: Use stream state here
        self.authenticated = False
        self.sessionstarted = False
        self.bound = False
        self.bindfail = False
        self.features = set()

    async def _handle_stream_features(self, features: StreamFeatures) -> Optional[bool]:
        """Process the received stream features.

        :param features: The features stanza.
        """
        for order, name in self._stream_feature_order:
            if name in features['features']:
                handler, restart = self._stream_feature_handlers[name]
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(features)
                else:
                    result = handler(features)
                if result and restart:
                    # Don't continue if the feature requires
                    # restarting the XML stream.
                    return True
        log.debug('Finished processing stream features.')
        self.event('stream_negotiated')
        return None

    def _handle_roster(self, iq: Iq) -> None:
        """Update the roster after receiving a roster stanza.

        :param iq: The roster stanza.
        """
        if iq['type'] == 'set':
            if iq['from'].bare and iq['from'].bare != self.boundjid.bare:
                raise XMPPError(condition='service-unavailable')

        roster = self.client_roster
        if iq['roster']['ver']:
            roster.version = iq['roster']['ver']
        items = iq['roster']['items']

        valid_subscriptions = ('to', 'from', 'both', 'none', 'remove')
        for jid, item in items.items():
            if item['subscription'] in valid_subscriptions:
                roster[jid]['name'] = item['name']
                roster[jid]['groups'] = item['groups']
                roster[jid]['from'] = item['subscription'] in ('from', 'both')
                roster[jid]['to'] = item['subscription'] in ('to', 'both')
                roster[jid]['pending_out'] = (item['ask'] == 'subscribe')

                roster[jid].save(remove=(item['subscription'] == 'remove'))

        if iq['type'] == 'set':
            resp = self.Iq(stype='result',
                           sto=iq['from'],
                           sid=iq['id'])
            resp.enable('roster')
            resp.send()

    def _handle_session_bind(self, jid: JID) -> None:
        """Set the client roster to the JID set by the server.

        :param :class:`slixmpp.xmlstream.jid.JID` jid: The bound JID as
            dictated by the server. The same as :attr:`boundjid`.
        """
        self.client_roster = self.roster[jid]
