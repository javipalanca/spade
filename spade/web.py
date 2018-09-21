import datetime
import logging
import socket

import timeago
from aiohttp import web as aioweb
import aiohttp_jinja2
import jinja2
from aioxmpp import PresenceType, JID
from spade.message import Message

logger = logging.getLogger("spade.Web")


def unused_port(hostname):
    """Return a port that is unused on the current host."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((hostname, 0))
        return s.getsockname()[1]


async def start_server_in_aiothread(handler, hostname, port, agent):
    """
    Listens to http requests and sends them to the webapp.

    Args:
        handler: handler to process the http requests
        hostname: host name to listen from.
        port: port to listen from.
        agent: agent that owns the web app.
    """
    loop = agent.aiothread.loop
    agent.web.server = await loop.create_server(handler, hostname, port)
    logger.info(f"Serving on http://{hostname}:{port}/")


class WebApp(object):
    """Module to handle agent's web interface"""

    def __init__(self, agent):
        self.agent = agent
        self.app = None
        self.handler = None
        self.server = None
        self.hostname = None
        self.port = None
        self.app = aioweb.Application()
        internal_loader = jinja2.PackageLoader("spade", package_path='templates', encoding='utf-8')
        cwd_loader = jinja2.FileSystemLoader(".")
        self.loaders = [internal_loader, cwd_loader]
        self._set_loaders()

    def start(self, hostname=None, port=None, templates_path=None):
        """
        Starts the web interface.

        Args:
          hostname (str, optional): host name to listen from. (Default value = None)
          port (int, optional): port to listen from. (Default value = None)
          templates_path (str, optional): path to look for templates. (Default value = None)

        """
        self.hostname = hostname if hostname else "localhost"
        if port:
            self.port = port
        elif not self.port:
            self.port = unused_port(self.hostname)
        if templates_path:
            self.loaders.insert(0, jinja2.FileSystemLoader(templates_path))
            self._set_loaders()
        self.setup_routes()
        self.handler = self.app.make_handler()
        self.agent.submit(start_server_in_aiothread(self.handler, self.hostname, self.port, self.agent))

    def _set_loaders(self):
        loader = jinja2.ChoiceLoader(self.loaders)
        aiohttp_jinja2.setup(self.app, loader=loader,
                             extensions=['jinja2_time.TimeExtension'],
                             context_processors=[self.agent_processor,
                                                 aiohttp_jinja2.request_processor]
                             )

    def setup_routes(self):
        self.app.router.add_get("/", self.index)
        self.app.router.add_get("/stop", self.stop_agent)
        self.app.router.add_get("/stop/now/", self.stop_now)
        self.app.router.add_get("/messages/", self.get_messages)
        self.app.router.add_get("/behaviour/{behaviour_type}/{behaviour_class}/", self.get_behaviour)
        self.app.router.add_get("/behaviour/{behaviour_type}/{behaviour_class}/kill/", self.kill_behaviour)
        self.app.router.add_get("/agent/{agentjid}/", self.get_agent)
        self.app.router.add_get("/agent/{agentjid}/unsubscribe/", self.unsubscribe_agent)
        self.app.router.add_post("/agent/{agentjid}/send/", self.send_agent)

    def add_get(self, path, controller, template):
        """
        Setup a route of type GET

        Args:
          path (str): URL to listen to
          controller (coroutine): the coroutine to handle the request
          template (str): the template to render the response or None if it is a JSON response

        """
        fn = self._prepare_controller(controller, template)
        self.app.router.add_get(path, fn)

    def add_post(self, path, controller, template):
        """
        Setup a route of type POST

        Args:
          path (str): URL to listen to
          controller (coroutine): the coroutine to handle the request
          template (str): the template to render the response or None if it is a JSON response

        """
        fn = self._prepare_controller(controller, template)
        self.app.router.add_post(path, fn)

    def _prepare_controller(self, controller, template):
        """
        Wraps the controller wether to render a jinja template or to return a json response (if template is None)
        Args:
            controller (coroutine): the coroutine to be wrapped
            template (str): the name of the template or None

        Returns:
            coroutine: a wrapped coroutine of the controller
        """
        if template:
            fn = aiohttp_jinja2.template(template_name=template)(controller)
        else:
            fn = self._parse_json_response(controller)
        return fn

    @staticmethod
    def _parse_json_response(func):
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            return aioweb.json_response(data=result, content_type='application/json')
        return wrapper

    @staticmethod
    def timeago(date):
        return timeago.format(date, datetime.datetime.now())

    async def agent_processor(self, request):
        messages = [(self.timeago(m[0]), m[1]) for m in self.agent.traces.received(limit=5)]
        return {"agent": self.agent, "messages": messages}

    # Default controllers for agent

    @aiohttp_jinja2.template('internal_tpl_index.html')
    async def index(self, request):
        contacts = [{"jid": jid,
                     "avatar": self.agent.build_avatar_url(jid.bare()),
                     "available": c["presence"].type_ == PresenceType.AVAILABLE if "presence" in c.keys() else False,
                     "show": str(c["presence"].show).split(".")[1] if "presence" in c.keys() else None,
                     } for jid, c in self.agent.presence.get_contacts().items()]
        return {"contacts": contacts}

    @aiohttp_jinja2.template("internal_tpl_index.html")
    async def stop_agent(self, request):
        return {"stopping": True}

    async def stop_now(self, request):
        logger.warning("Stopping agent from web interface.")
        self.agent.stop()
        return aioweb.json_response({})

    @aiohttp_jinja2.template("internal_tpl_messages.html")
    async def get_messages(self, request):
        messages = [(self.timeago(m[0]), m[1]) for m in self.agent.traces.received()]
        return {"messages": messages}

    @aiohttp_jinja2.template('internal_tpl_behaviour.html')
    async def get_behaviour(self, request):
        behaviour_str = request.match_info['behaviour_type'] + "/" + request.match_info['behaviour_class']
        behaviour = self.find_behaviour(behaviour_str)
        messages = [(self.timeago(m[0]), m[1]) for m in self.agent.traces.filter(category=behaviour_str)]
        return {"behaviour": behaviour, "bmessages": messages}

    async def kill_behaviour(self, request):
        behaviour_str = request.match_info['behaviour_type'] + "/" + request.match_info['behaviour_class']
        behaviour = self.find_behaviour(behaviour_str)
        behaviour.kill()
        raise aioweb.HTTPFound('/')

    @aiohttp_jinja2.template("internal_tpl_agent.html")
    async def get_agent(self, request):
        agent_jid = request.match_info['agentjid']
        agent_messages = [(self.timeago(m[0]), m[1]) for m in self.agent.traces.filter(to=agent_jid)]
        c = self.agent.presence.get_contact(JID.fromstr(agent_jid))
        contact = {
            "show": str(c["presence"].show).split(".")[1] if "presence" in c.keys() else None
        }
        return {"amessages": agent_messages, "ajid": agent_jid, "contact": contact}

    async def unsubscribe_agent(self, request):
        agent_jid = request.match_info['agentjid']
        self.agent.presence.unsubscribe(agent_jid)
        raise aioweb.HTTPFound("/agent/{agentjid}/".format(agentjid=agent_jid))

    async def send_agent(self, request):
        agent_jid = request.match_info['agentjid']
        form = await request.post()
        body = form["message"]
        logger.info("Sending message to {}: {}".format(agent_jid, body))
        msg = Message(to=agent_jid, sender=str(self.agent.jid), body=body)
        aioxmpp_msg = msg.prepare()
        await self.agent.stream.send(aioxmpp_msg)
        msg.sent = True
        self.agent.traces.append(msg)
        raise aioweb.HTTPFound("/agent/{agentjid}/".format(agentjid=agent_jid))

    def find_behaviour(self, behaviour_str):
        behav = None
        for behaviour in self.agent.behaviours:
            if str(behaviour) == behaviour_str:
                behav = behaviour
                break
        return behav
