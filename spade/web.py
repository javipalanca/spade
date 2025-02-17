import datetime
import logging
import socket
from typing import Optional, Coroutine, Type

import aiohttp_jinja2
import jinja2
import timeago
from aiohttp import web as aioweb
from aiohttp.web_runner import AppRunner
from slixmpp import JID

from .behaviour import CyclicBehaviour
from .message import Message
from .presence import PresenceShow, ContactNotFound, PresenceNotFound

logger = logging.getLogger("spade.Web")


def unused_port(hostname: str) -> None:
    """Return a port that is unused on the current host."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((hostname, 0))
        return s.getsockname()[1]


async def start_server_in_loop(runner: AppRunner, hostname: str, port: int, agent):
    """
    Listens to http requests and sends them to the webapp.

    Args:
        runner (AppRunner): AppRunner to process the http requests
        hostname (str): host name to listen from.
        port (int): port to listen from.
        agent (spade.agent.Agent): agent that owns the web app.
    """
    await runner.setup()
    agent.web.server = aioweb.TCPSite(runner, hostname, port)
    await agent.web.server.start()
    logger.info(f"Serving on http://{hostname}:{port}/")


class WebApp(object):
    """Module to handle agent's web interface"""

    def __init__(self, agent):
        self.agent = agent
        self.server = None
        self.hostname = None
        self.port = None
        self.runner = None
        self.app = aioweb.Application()
        internal_loader = jinja2.PackageLoader(
            "spade", package_path="templates", encoding="utf-8"
        )
        cwd_loader = jinja2.FileSystemLoader(".")
        self.loaders = [internal_loader, cwd_loader]
        self._set_loaders()
        self.menu_entries = {}

    def start(
        self,
        hostname: Optional[str] = None,
        port: Optional[int] = None,
        templates_path: Optional[str] = None,
    ):
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
        self.runner = aioweb.AppRunner(self.app)
        return self.agent.submit(
            start_server_in_loop(self.runner, self.hostname, self.port, self.agent)
        )

    def add_template_path(self, templates_path):
        self.loaders.insert(0, jinja2.FileSystemLoader(templates_path))
        self._set_loaders()

    def is_started(self) -> bool:
        return self.runner is not None

    def _set_loaders(self) -> None:
        loader = jinja2.ChoiceLoader(self.loaders)
        aiohttp_jinja2.setup(
            self.app,
            loader=loader,
            extensions=["jinja2_time.TimeExtension"],
            context_processors=[self.agent_processor, aiohttp_jinja2.request_processor],
        )

    def setup_routes(self) -> None:
        self.app.router.add_get("/spade", self.index)
        self.app.router.add_get("/spade/", self.index)
        self.app.router.add_get("/spade/stop", self.stop_agent)
        self.app.router.add_get("/spade/stop/now/", self.stop_now)
        self.app.router.add_get("/spade/messages/", self.get_messages)
        self.app.router.add_get(
            "/spade/behaviour/{behaviour_type}/{behaviour_class}/", self.get_behaviour
        )
        self.app.router.add_get(
            "/spade/behaviour/{behaviour_type}/{behaviour_class}/kill/",
            self.kill_behaviour,
        )

        self.app.router.add_get(
            "/spade/agent/{agentjid:[^/]+(?:/[^/]+)?}/", self.get_agent
        )
        self.app.router.add_get(
            "/spade/agent/unsubscribe/{agentjid:[^/]+(?:/[^/]+)?}/",
            self.unsubscribe_agent,
        )
        self.app.router.add_post(
            "/spade/agent/{agentjid:[^/]+(?:/[^/]+)?}/send/", self.send_agent
        )

    def add_menu_entry(self, name: str, url: str, icon="fa fa-circle") -> None:
        """
        Adds a new entry to the menu.

        Args:
          name (str): name of the entry
          url (str): url to be redirected to
          icon (str): icon to be displayed (Default value = "fa fa-circle")

        """
        self.menu_entries[name] = (url, icon)

    def add_get(
        self,
        path: str,
        controller: Coroutine,
        template: str,
        raw: Optional[bool] = False,
    ) -> None:
        """
        Setup a route of type GET

        Args:
          path (str): URL to listen to
          controller (coroutine): the coroutine to handle the request
          template (str): the template to render the response or None if it is a JSON response
          raw (bool): indicates if post-processing (jinja, json, etc) is needed or not

        """
        if raw:
            fn = controller
        else:
            fn = self._prepare_controller(controller, template)
        self.app.router.add_get(path, fn)

    def add_post(
        self,
        path: str,
        controller: Coroutine,
        template: str,
        raw: Optional[bool] = False,
    ) -> None:
        """
        Setup a route of type POST

        Args:
          path (str): URL to listen to
          controller (coroutine): the coroutine to handle the request
          template (str): the template to render the response or None if it is a JSON response
          raw (bool): indicates if post-processing (jinja, json, etc) is needed or not

        """
        if raw:
            fn = controller
        else:
            fn = self._prepare_controller(controller, template)
        self.app.router.add_post(path, fn)

    def _prepare_controller(self, controller: Coroutine, template: str) -> None:
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
            return aioweb.json_response(data=result, content_type="application/json")

        return wrapper

    @staticmethod
    def timeago(date):
        return timeago.format(date, datetime.datetime.now())

    async def agent_processor(self, request):
        messages = [
            (self.timeago(m[0]), m[1]) for m in self.agent.traces.received(limit=5)
        ]
        return {
            "agent": self.agent,
            "messages": messages,
            "menu": self.menu_entries,
            "active": request.path,
        }

    # Default controllers for agent

    @aiohttp_jinja2.template("internal_tpl_index.html")
    async def index(self, request):
        contacts = [
            {
                "jid": jid,
                "avatar": self.agent.build_avatar_url(jid),
                "available": c.is_available(),
                "show": c.get_presence().show,
                "resources": c.resources,
                "resource0": (
                    list(c.resources.values())[0].show,
                    list(c.resources.values())[0].status,
                    list(c.resources.values())[0].priority,
                ),
            }
            for jid, c in self.agent.presence.get_contacts().items()
        ]
        return {"contacts": contacts}

    @aiohttp_jinja2.template("internal_tpl_index.html")
    async def stop_agent(self, request):
        return {"stopping": True}

    async def stop_now(self, request):
        logger.warning("Stopping agent from web interface.")
        await self.agent.stop()
        return aioweb.json_response({})  # pragma: no cover

    @aiohttp_jinja2.template("internal_tpl_messages.html")
    async def get_messages(self, request):
        messages = [(self.timeago(m[0]), m[1]) for m in self.agent.traces.received()]
        return {"messages": messages}

    @aiohttp_jinja2.template("internal_tpl_behaviour.html")
    async def get_behaviour(self, request):
        behaviour_str = f"{request.match_info['behaviour_type']}/{request.match_info['behaviour_class']}"
        behaviour = self.find_behaviour(behaviour_str)
        messages = [
            (self.timeago(m[0]), m[1])
            for m in self.agent.traces.filter(category=behaviour_str)
        ]
        return {"behaviour": behaviour, "bmessages": messages}

    async def kill_behaviour(self, request):
        behaviour_str = f"{request.match_info['behaviour_type']}/{request.match_info['behaviour_class']}"
        behaviour = self.find_behaviour(behaviour_str)
        behaviour.kill()
        raise aioweb.HTTPFound("/spade")

    @aiohttp_jinja2.template("internal_tpl_agent.html")
    async def get_agent(self, request):
        agent_jid = request.match_info["agentjid"]
        agent_messages = [
            (self.timeago(m[0]), m[1]) for m in self.agent.traces.filter(to=agent_jid)
        ]
        try:
            c = self.agent.presence.get_contact(JID(agent_jid))
            if c.get_presence().show is not None:
                contact = {"show": c.get_presence().show.value}
            else:
                contact = {"show": PresenceShow.NONE.value}
        except ContactNotFound:
            # raise 404
            raise aioweb.HTTPNotFound()
        except PresenceNotFound:
            contact = {"show": PresenceShow.NONE.value}

        except Exception as e:
            logger.error(e)
            raise e

        return {"amessages": agent_messages, "ajid": agent_jid, "contact": contact}

    async def unsubscribe_agent(self, request):
        try:
            agent_jid = request.match_info["agentjid"]
            self.agent.presence.unsubscribe(str(JID(agent_jid).bare))
        except Exception as e:
            logger.error(e)
        raise aioweb.HTTPFound("/spade")

    async def send_agent(self, request):
        agent_jid = request.match_info["agentjid"]
        form = await request.post()
        body = form["message"]
        logger.info("Sending message to {}: {}".format(agent_jid, body))
        msg = Message(to=agent_jid, sender=str(self.agent.jid), body=body)
        slixmpp_msg = msg.prepare(self.agent.client)
        self.agent.client.send(slixmpp_msg)
        msg.sent = True
        self.agent.traces.append(msg)
        raise aioweb.HTTPFound("/spade/agent/{agentjid}/".format(agentjid=agent_jid))

    def find_behaviour(self, behaviour_str: str) -> Optional[Type[CyclicBehaviour]]:
        behav = None
        for behaviour in self.agent.behaviours:
            if str(behaviour) == behaviour_str:
                behav = behaviour
                break
        return behav
