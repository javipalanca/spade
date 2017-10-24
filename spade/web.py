import logging
import socket

from aiohttp import web
import aiohttp_jinja2
import jinja2

logger = logging.getLogger("spade.Web")


def unused_port(hostname):
    """Return a port that is unused on the current host."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((hostname, 0))
        return s.getsockname()[1]


class WebApp(object):
    def __init__(self, agent):
        self.agent = agent
        self.loop = self.agent.aiothread.loop
        self.app = None
        self.server = None
        self.hostname = None
        self.port = None

    def start(self, hostname=None, port=None, templates_path=None):
        self.hostname = hostname if hostname else "localhost"
        self.port = port if port else unused_port(self.hostname)
        self.app = web.Application()
        internal_loader = jinja2.PackageLoader("spade", package_path='templates', encoding='utf-8')
        if templates_path:
            loader = jinja2.ChoiceLoader([
                jinja2.FileSystemLoader(templates_path),
                internal_loader
            ])
        else:
            loader = internal_loader
        aiohttp_jinja2.setup(self.app, loader=loader)
        self.app.router.add_route("GET", "/", self.agent_index)
        fut = self.loop.create_server(self.app.make_handler(), self.hostname, self.port)
        # self.server = self.loop.run_until_complete(future=fut)
        self.agent.submit(fut)
        logger.info(f"Serving on http://{self.hostname}:{self.port}/")

    @aiohttp_jinja2.template('agent.html')
    async def agent_index(self, request):
        return {
            "jid": self.agent.jid,
            "avatar": self.agent.avatar
        }
