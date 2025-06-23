from typing import Any, Optional, Callable
from asyncio import iscoroutinefunction, Future
from slixmpp.xmlstream import JID

APIHandler = Callable[
    [Optional[JID], Optional[str], Optional[JID], Any],
    Any
]

class APIWrapper(object):
    """Slixmpp API wrapper.

    This class provide a shortened binding to access ``self.api`` from
    plugins without having to specify the plugin name or the global
    :class:`~.APIRegistry`.
    """

    def __init__(self, api, name):
        self.api = api
        self.name = name
        if name not in self.api.settings:
            self.api.settings[name] = {}

    def __getattr__(self, attr: str):
        """Curry API management commands with the API name."""
        if attr == 'name':
            return self.name
        elif attr == 'settings':
            return self.api.settings[self.name]
        elif attr == 'register':
            def partial(handler, op, jid=None, node=None, default=False):
                register = getattr(self.api, attr)
                return register(handler, self.name, op, jid, node, default)
            return partial
        elif attr == 'register_default':
            def partial1(handler, op, jid=None, node=None):
                return getattr(self.api, attr)(handler, self.name, op)
            return partial1
        elif attr in ('run', 'restore_default', 'unregister'):
            def partial2(*args, **kwargs):
                return getattr(self.api, attr)(self.name, *args, **kwargs)
            return partial2
        return None

    def __getitem__(self, attr):
        def partial(jid=None, node=None, ifrom=None, args=None):
            return self.api.run(self.name, attr, jid, node, ifrom, args)
        return partial


class APIRegistry(object):
    """API Registry.

    This class is the global Slixmpp API registry, on which any handler will
    be registed.
    """

    def __init__(self, xmpp):
        self._handlers = {}
        self._handler_defaults = {}
        self.xmpp = xmpp
        self.settings = {}

    def _setup(self, ctype: str, op: str):
        """Initialize the API callback dictionaries.

        :param ctype: The name of the API to initialize.
        :param op: The API operation to initialize.
        """
        if ctype not in self.settings:
            self.settings[ctype] = {}
        if ctype not in self._handler_defaults:
            self._handler_defaults[ctype] = {}
        if ctype not in self._handlers:
            self._handlers[ctype] = {}
        if op not in self._handlers[ctype]:
            self._handlers[ctype][op] = {'global': None,
                                         'jid': {},
                                         'node': {}}

    def wrap(self, ctype: str) -> APIWrapper:
        """Return a wrapper object that targets a specific API."""
        return APIWrapper(self, ctype)

    def purge(self, ctype: str) -> None:
        """Remove all information for a given API."""
        del self.settings[ctype]
        del self._handler_defaults[ctype]
        del self._handlers[ctype]

    def run(self, ctype: str, op: str, jid: Optional[JID] = None,
            node: Optional[str] = None, ifrom: Optional[JID] = None,
            args: Any = None) -> Future:
        """Execute an API callback, based on specificity.

        The API callback that is executed is chosen based on the combination
        of the provided JID and node:

        ====== ======= ===================
        JID     node    Handler
        ====== ======= ===================
        Given   Given   Node + JID handler
        Given   None    JID handler
        None    Given   Node handler
        None    None    Global handler
        ====== ======= ===================

        A node handler is responsible for servicing a single node at a single
        JID, while a JID handler may respond for any node at a given JID, and
        the global handler will answer to any JID+node combination.

        Handlers should check that the JID ``ifrom`` is authorized to perform
        the desired action.

        .. versionchanged:: 1.8.0
            ``run()`` always returns a future, if the handler is a coroutine
            the future should be awaited on.

        :param ctype: The name of the API to use.
        :param op: The API operation to perform.
        :param jid: Optionally provide specific JID.
        :param node: Optionally provide specific node.
        :param ifrom: Optionally provide the requesting JID.
        :param args: Optional arguments to the handler.
        """
        self._setup(ctype, op)

        if not jid:
            jid = self.xmpp.boundjid
        elif jid and not isinstance(jid, JID):
            jid = JID(jid)
        elif jid == JID(''):
            jid = self.xmpp.boundjid
        assert jid is not None

        if node is None:
            node = ''

        if self.xmpp.is_component:
            if self.settings[ctype].get('component_bare', False):
                jid_str = jid.bare
            else:
                jid_str = jid.full
        else:
            if self.settings[ctype].get('client_bare', False):
                jid_str = jid.bare
            else:
                jid_str = jid.full

        jid = JID(jid_str)

        handler = self._handlers[ctype][op]['node'].get((jid, node), None)
        if handler is None:
            handler = self._handlers[ctype][op]['jid'].get(jid, None)
        if handler is None:
            handler = self._handlers[ctype][op].get('global', None)

        if handler:
            try:
                if iscoroutinefunction(handler):
                    return self.xmpp.wrap(handler(jid, node, ifrom, args))
                else:
                    future: Future = Future()
                    result = handler(jid, node, ifrom, args)
                    future.set_result(result)
                    return future
            except TypeError:
                # To preserve backward compatibility, drop the ifrom
                # parameter for existing handlers that don't understand it.
                return handler(jid, node, args)
        future = Future()
        future.set_result(None)
        return future

    def register(self, handler: Optional[APIHandler], ctype: str, op: str,
                 jid: Optional[JID] = None, node: Optional[str] = None,
                 default: bool = False):
        """Register an API callback, with JID+node specificity.

        The API callback can later be executed based on the
        specificity of the provided JID+node combination.

        See :meth:`~.APIRegistry.run` for more details.

        :param ctype: The name of the API to use.
        :param op: The API operation to perform.
        :param jid: Optionally provide specific JID.
        :param node: Optionally provide specific node.
        """
        self._setup(ctype, op)
        if jid is None and node is None:
            if handler is None:
                handler = self._handler_defaults[op]
            self._handlers[ctype][op]['global'] = handler
        elif jid is not None and node is None:
            self._handlers[ctype][op]['jid'][jid] = handler
        else:
            self._handlers[ctype][op]['node'][(jid, node)] = handler

        if default:
            self.register_default(handler, ctype, op)

    def register_default(self, handler, ctype: str, op: str):
        """Register a default, global handler for an operation.

        :param handler: The default, global handler for the operation.
        :param ctype: The name of the API to modify.
        :param op: The API operation to use.
        """
        self._setup(ctype, op)
        self._handler_defaults[ctype][op] = handler

    def unregister(self, ctype: str, op: str, jid: Optional[JID] = None,
                   node: Optional[str] = None):
        """Remove an API callback.

        The API callback chosen for removal is based on the
        specificity of the provided JID+node combination.

        See :meth:`~ApiRegistry.run` for more details.

        :param ctype: The name of the API to use.
        :param op: The API operation to perform.
        :param jid: Optionally provide specific JID.
        :param node: Optionally provide specific node.
        """
        self._setup(ctype, op)
        self.register(None, ctype, op, jid, node)

    def restore_default(self, ctype: str, op: str, jid: Optional[JID] = None,
                        node: Optional[str] = None):
        """Reset an API callback to use a default handler.

        :param ctype: The name of the API to use.
        :param op: The API operation to perform.
        :param jid: Optionally provide specific JID.
        :param node: Optionally provide specific node.
        """
        self.unregister(ctype, op, jid, node)
        self.register(self._handler_defaults[ctype][op], ctype, op, jid, node)
