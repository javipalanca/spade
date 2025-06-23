
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2011 Nathanael C. Fritz, Lance J.T. Stout
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import asyncio
import functools
import logging
import time

from slixmpp import Iq
from slixmpp.exceptions import XMPPError
from slixmpp.xmlstream.handler import Callback
from slixmpp.xmlstream.matcher import StanzaPath
from slixmpp.xmlstream import register_stanza_plugin, JID
from slixmpp.plugins import BasePlugin
from slixmpp.plugins.xep_0050 import stanza
from slixmpp.plugins.xep_0050 import Command
from slixmpp.plugins.xep_0004 import Form


log = logging.getLogger(__name__)


class XEP_0050(BasePlugin):

    """
    XEP-0050: Ad-Hoc Commands

    XMPP's Adhoc Commands provides a generic workflow mechanism for
    interacting with applications. The result is similar to menu selections
    and multi-step dialogs in normal desktop applications. Clients do not
    need to know in advance what commands are provided by any particular
    application or agent. While adhoc commands provide similar functionality
    to Jabber-RPC, adhoc commands are used primarily for human interaction.

    Also see <http://xmpp.org/extensions/xep-0050.html>

    Events:
        command_execute  -- Received a command with action="execute"
        command_next     -- Received a command with action="next"
        command_complete -- Received a command with action="complete"
        command_cancel   -- Received a command with action="cancel"

    Attributes:
        commands -- A dictionary mapping JID/node pairs to command
                    names and handlers.
        sessions -- A dictionary or equivalent backend mapping
                    session IDs to dictionaries containing data
                    relevant to a command's session.

    """

    name = 'xep_0050'
    description = 'XEP-0050: Ad-Hoc Commands'
    dependencies = {'xep_0030', 'xep_0004'}
    stanza = stanza
    default_config = {
        'session_db': None
    }

    def plugin_init(self):
        """Start the XEP-0050 plugin."""
        self.sessions = self.session_db
        if self.sessions is None:
            self.sessions = {}

        self.commands = {}

        self.xmpp.register_handler(
            Callback("Ad-Hoc Execute",
                     StanzaPath('iq@type=set/command'),
                     self._handle_command))

        register_stanza_plugin(Iq, Command)
        register_stanza_plugin(Command, Form, iterable=True)

        self.xmpp.add_event_handler('command', self._handle_command_all)

    def plugin_end(self):
        self.xmpp.del_event_handler('command', self._handle_command_all)
        self.xmpp.remove_handler('Ad-Hoc Execute')
        self.xmpp['xep_0030'].del_feature(feature=Command.namespace)
        self.xmpp['xep_0030'].set_items(node=Command.namespace, items=tuple())

    def session_bind(self, jid):
        self.xmpp['xep_0030'].add_feature(Command.namespace)
        self.xmpp['xep_0030'].set_items(node=Command.namespace, items=tuple())

    def set_backend(self, db):
        """
        Replace the default session storage dictionary with
        a generic, external data storage mechanism.

        The replacement backend must be able to interact through
        the same syntax and interfaces as a normal dictionary.

        :param db: The new session storage mechanism.
        """
        self.sessions = db

    def prep_handlers(self, handlers, **kwargs):
        """
        Prepare a list of functions for use by the backend service.

        Intended to be replaced by the backend service as needed.

        :param handlers: A list of function pointers
        :param kwargs: Any additional parameters required by the backend.
        """
        pass

    # =================================================================
    # Server side (command provider) API

    def add_command(self, jid=None, node=None, name='', handler=None):
        """
        Make a new command available to external entities.

        Access control may be implemented in the provided handler.

        Command workflow is done across a sequence of command handlers. The
        first handler is given the initial Iq stanza of the request in order
        to support access control. Subsequent handlers are given only the
        payload items of the command. All handlers will receive the command's
        session data.

        :param jid: The JID that will expose the command.
        :param node: The node associated with the command.
        :param name: A human readable name for the command.
        :param handler: A function that will generate the response to the
                        initial command request, as well as enforcing any
                        access control policies.
        """
        if jid is None:
            jid = self.xmpp.boundjid
        elif not isinstance(jid, JID):
            jid = JID(jid)
        item_jid = jid.full

        self.xmpp['xep_0030'].add_identity(category='automation',
                                           itype='command-list',
                                           name='Ad-Hoc commands',
                                           node=Command.namespace,
                                           jid=jid)
        self.xmpp['xep_0030'].add_item(jid=item_jid,
                                       name=name,
                                       node=Command.namespace,
                                       subnode=node,
                                       ijid=jid)
        self.xmpp['xep_0030'].add_identity(category='automation',
                                           itype='command-node',
                                           name=name,
                                           node=node,
                                           jid=jid)
        self.xmpp['xep_0030'].add_feature(Command.namespace, None, jid)

        self.commands[(item_jid, node)] = (name, handler)

    def new_session(self):
        """Return a new session ID."""
        return str(time.time()) + '-' + self.xmpp.new_id()

    def _handle_command(self, iq):
        """Raise command events based on the command action."""
        self.xmpp.event('command', iq)
        self.xmpp.event('command_%s' % iq['command']['action'], iq)

    async def _handle_command_all(self, iq: Iq) -> None:
        action = iq['command']['action']
        sessionid = iq['command']['sessionid']
        session = self.sessions.get(sessionid)

        if session is None:
            return await self._handle_command_start(iq)

        if action in ('next', 'execute'):
            return await self._handle_command_next(iq)
        if action == 'prev':
            return await self._handle_command_prev(iq)
        if action == 'complete':
            return await self._handle_command_complete(iq)
        if action == 'cancel':
            return await self._handle_command_cancel(iq)
        return None

    async def _handle_command_start(self, iq):
        """
        Process an initial request to execute a command.

        :param iq: The command execution request.
        """
        sessionid = self.new_session()
        node = iq['command']['node']
        key = (iq['to'].full, node)
        name, handler = self.commands.get(key, ('Not found', None))
        if not handler:
            log.debug('Command not found: %s, %s', key, self.commands)
            raise XMPPError('item-not-found')

        payload = []
        for stanza in iq['command']['substanzas']:
            payload.append(stanza)

        if len(payload) == 1:
            payload = payload[0]

        interfaces = {item.plugin_attrib for item in payload}
        payload_classes = {item.__class__ for item in payload}

        initial_session = {'id': sessionid,
                           'from': iq['from'],
                           'to': iq['to'],
                           'node': node,
                           'payload': payload,
                           'interfaces': interfaces,
                           'payload_classes': payload_classes,
                           'notes': None,
                           'has_next': False,
                           'allow_complete': False,
                           'allow_prev': False,
                           'past': [],
                           'next': None,
                           'prev': None,
                           'cancel': None}

        session = await _await_if_needed(handler, iq, initial_session)

        self._process_command_response(iq, session)

    async def _handle_command_next(self, iq):
        """
        Process a request for the next step in the workflow
        for a command with multiple steps.

        :param iq: The command continuation request.
        """
        sessionid = iq['command']['sessionid']
        session = self.sessions.get(sessionid)

        if session:
            handler = session['next']
            interfaces = session['interfaces']
            results = []
            for stanza in iq['command']['substanzas']:
                if stanza.plugin_attrib in interfaces:
                    results.append(stanza)
            if len(results) == 1:
                results = results[0]

            session = await _await_if_needed(handler, results, session)

            self._process_command_response(iq, session)
        else:
            raise XMPPError('item-not-found')

    async def _handle_command_prev(self, iq):
        """
        Process a request for the prev step in the workflow
        for a command with multiple steps.

        :param iq: The command continuation request.
        """
        sessionid = iq['command']['sessionid']
        session = self.sessions.get(sessionid)

        if session:
            handler = session['prev']
            interfaces = session['interfaces']
            results = []
            for stanza in iq['command']['substanzas']:
                if stanza.plugin_attrib in interfaces:
                    results.append(stanza)
            if len(results) == 1:
                results = results[0]

            session = await _await_if_needed(handler, results, session)

            self._process_command_response(iq, session)
        else:
            raise XMPPError('item-not-found')

    def _process_command_response(self, iq, session):
        """
        Generate a command reply stanza based on the
        provided session data.

        :param iq: The command request stanza.
        :param session: A dictionary of relevant session data.
        """
        sessionid = session['id']

        payload = session['payload']
        if payload is None:
            payload = []
        if not isinstance(payload, list):
            payload = [payload]

        interfaces = session.get('interfaces', set())
        payload_classes = session.get('payload_classes', set())

        interfaces.update({item.plugin_attrib for item in payload})
        payload_classes.update({item.__class__ for item in payload})

        session['interfaces'] = interfaces
        session['payload_classes'] = payload_classes

        self.sessions[sessionid] = session

        for item in payload:
            register_stanza_plugin(Command, item.__class__, iterable=True)

        iq = iq.reply()
        iq['command']['node'] = session['node']
        iq['command']['sessionid'] = session['id']

        if session['next'] is None:
            iq['command']['actions'] = []
            iq['command']['status'] = 'completed'
        elif session['has_next']:
            actions = ['next']
            if session['allow_complete']:
                actions.append('complete')
            if session['allow_prev']:
                actions.append('prev')
            iq['command']['actions'] = actions
            iq['command']['status'] = 'executing'
        else:
            actions = ['complete']
            if session['allow_prev']:
                actions.append('prev')
            iq['command']['actions'] = actions
            iq['command']['status'] = 'executing'

        iq['command']['notes'] = session['notes']

        for item in payload:
            iq['command'].append(item)

        iq.send()

    async def _handle_command_cancel(self, iq):
        """
        Process a request to cancel a command's execution.

        :param iq: The command cancellation request.
        """
        node = iq['command']['node']
        sessionid = iq['command']['sessionid']

        session = self.sessions.get(sessionid)

        if session:
            handler = session['cancel']
            if handler:
                await _await_if_needed(handler, iq, session)
            del self.sessions[sessionid]
            iq = iq.reply()
            iq['command']['node'] = node
            iq['command']['sessionid'] = sessionid
            iq['command']['status'] = 'canceled'
            iq['command']['notes'] = session['notes']
            iq.send()
        else:
            raise XMPPError('item-not-found')


    async def _handle_command_complete(self, iq):
        """
        Process a request to finish the execution of command
        and terminate the workflow.

        All data related to the command session will be removed.

        Arguments:
        :param iq: The command completion request.
        """
        node = iq['command']['node']
        sessionid = iq['command']['sessionid']
        session = self.sessions.get(sessionid)

        if session:
            handler = session['next']
            interfaces = session['interfaces']
            results = []
            for stanza in iq['command']['substanzas']:
                if stanza.plugin_attrib in interfaces:
                    results.append(stanza)
            if len(results) == 1:
                results = results[0]

            if handler:
                await _await_if_needed(handler, results, session)

            del self.sessions[sessionid]

            payload = session['payload']
            if payload is None:
                payload = []
            if not isinstance(payload, list):
                payload = [payload]

            for item in payload:
                register_stanza_plugin(Command, item.__class__, iterable=True)

            iq = iq.reply()

            iq['command']['node'] = node
            iq['command']['sessionid'] = sessionid
            iq['command']['actions'] = []
            iq['command']['status'] = 'completed'
            iq['command']['notes'] = session['notes']

            for item in payload:
                iq['command'].append(item)

            iq.send()
        else:
            raise XMPPError('item-not-found')

    # =================================================================
    # Client side (command user) API

    def get_commands(self, jid, **kwargs):
        """
        Return a list of commands provided by a given JID.

        :param jid: The JID to query for commands.
        :param local: If true, then the query is for a JID/node
                      combination handled by this Slixmpp instance and
                      no stanzas need to be sent.
                      Otherwise, a disco stanza must be sent to the
                      remove JID to retrieve the items.
        :param iterator: If True, return a result set iterator using
                         the XEP-0059 plugin, if the plugin is loaded.
                         Otherwise the parameter is ignored.
        """
        return self.xmpp['xep_0030'].get_items(jid=jid,
                                               node=Command.namespace,
                                               **kwargs)

    def send_command(self, jid, node, ifrom=None, action='execute',
                     payload=None, sessionid=None, flow=False, **kwargs):
        """
        Create and send a command stanza, without using the provided
        workflow management APIs.

        :param jid: The JID to send the command request or result.
        :param node: The node for the command.
        :param ifrom: Specify the sender's JID.
        :param action: May be one of: execute, cancel, complete,
                         or cancel.
        :param payload: Either a list of payload items, or a single
                        payload item such as a data form.
        :param sessionid: The current session's ID value.
        :param flow: If True, process the Iq result using the
                     command workflow methods contained in the
                     session instead of returning the response
                     stanza itself. Defaults to False.
        """
        iq = self.xmpp.Iq()
        iq['type'] = 'set'
        iq['to'] = jid
        iq['from'] = ifrom
        iq['command']['node'] = node
        iq['command']['action'] = action
        if sessionid is not None:
            iq['command']['sessionid'] = sessionid
        if payload is not None:
            if not isinstance(payload, list):
                payload = [payload]
            for item in payload:
                iq['command'].append(item)
        if not flow:
            return iq.send(**kwargs)
        else:
            iq.send(callback=self._handle_command_result)

    def start_command(self, jid, node, session, ifrom=None):
        """
        Initiate executing a command provided by a remote agent.

        The provided session dictionary should contain:

        :param next: A handler for processing the command result.
        :param error: A handler for processing any error stanzas
                      generated by the request.

        :param jid: The JID to send the command request.
        :param node: The node for the desired command.
        :param session: A dictionary of relevant session data.
        """
        session['jid'] = jid
        session['node'] = node
        session['timestamp'] = time.time()
        if 'payload' not in session:
            session['payload'] = None

        iq = self.xmpp.Iq()
        iq['type'] = 'set'
        iq['to'] = jid
        iq['from'] = ifrom
        session['from'] = ifrom
        iq['command']['node'] = node
        iq['command']['action'] = 'execute'
        if session['payload'] is not None:
            payload = session['payload']
            if not isinstance(payload, list):
                payload = list(payload)
            for stanza in payload:
                iq['command'].append(stanza)
        sessionid = 'client:pending_' + iq['id']
        session['id'] = sessionid
        self.sessions[sessionid] = session
        iq.send(callback=self._handle_command_result)

    def continue_command(self, session, direction='next'):
        """
        Execute the next action of the command.

        :param session: All stored data relevant to the current
                        command session.
        """
        sessionid = 'client:' + session['id']
        self.sessions[sessionid] = session

        self.send_command(session['jid'],
                          session['node'],
                          ifrom=session.get('from', None),
                          action=direction,
                          payload=session.get('payload', None),
                          sessionid=session['id'],
                          flow=True)

    def cancel_command(self, session):
        """
        Cancel the execution of a command.

        :param session: All stored data relevant to the current
                        command session.
        """
        sessionid = 'client:' + session['id']
        self.sessions[sessionid] = session

        self.send_command(session['jid'],
                          session['node'],
                          ifrom=session.get('from', None),
                          action='cancel',
                          payload=session.get('payload', None),
                          sessionid=session['id'],
                          flow=True)

    def complete_command(self, session):
        """
        Finish the execution of a command workflow.

        :param session: All stored data relevant to the current
                        command session.
        """
        sessionid = 'client:' + session['id']
        self.sessions[sessionid] = session

        self.send_command(session['jid'],
                          session['node'],
                          ifrom=session.get('from', None),
                          action='complete',
                          payload=session.get('payload', None),
                          sessionid=session['id'],
                          flow=True)

    def terminate_command(self, session):
        """
        Delete a command's session after a command has completed
        or an error has occurred.

        :param session: All stored data relevant to the current
                        command session.
        """
        sessionid = 'client:' + session['id']
        try:
            del self.sessions[sessionid]
        except Exception as e:
            log.error("Error deleting adhoc command session: %s" % e)

    def _handle_command_result(self, iq):
        """
        Process the results of a command request.

        Will execute the 'next' handler stored in the session
        data, or the 'error' handler depending on the Iq's type.

        :param iq: The command response.
        """
        sessionid = 'client:' + iq['command']['sessionid']
        pending = False

        if sessionid not in self.sessions:
            pending = True
            pendingid = 'client:pending_' + iq['id']
            if pendingid not in self.sessions:
                return
            sessionid = pendingid

        session = self.sessions[sessionid]
        sessionid = 'client:' + iq['command']['sessionid']
        session['id'] = iq['command']['sessionid']

        self.sessions[sessionid] = session

        if pending:
            del self.sessions[pendingid]

        handler_type = 'next'
        if iq['type'] == 'error':
            handler_type = 'error'
        handler = session.get(handler_type, None)
        if handler:
            handler(iq, session)
        elif iq['type'] == 'error':
            self.terminate_command(session)

        if iq['command']['status'] == 'completed':
            self.terminate_command(session)


def _iscoroutine_or_partial_coroutine(handler):
    return asyncio.iscoroutinefunction(handler) \
        or isinstance(handler, functools.partial) \
        and asyncio.iscoroutinefunction(handler.func)


async def _await_if_needed(handler, *args):
    if handler is None:
        raise XMPPError("bad-request", text="The command is completed")
    if _iscoroutine_or_partial_coroutine(handler):
        log.debug(f"%s is async", handler)
        return await handler(*args)
    else:
        log.debug(f"%s is sync", handler)
        return handler(*args)
