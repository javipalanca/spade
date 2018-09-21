import asyncio
import random
import time

from asynctest import Mock, CoroutineMock
import requests
from aioxmpp import JID, PresenceType
from aioxmpp.roster import Item
from parsel import Selector

from aiohttp_jinja2 import get_env
from jinja2 import ChoiceLoader, FileSystemLoader, PackageLoader
from testfixtures import LogCapture

from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
from tests.utils import make_connected_agent


def test_web():
    agent = make_connected_agent()
    agent.start(auto_register=False)
    agent.web.start()

    assert agent.web.app is not None

    counter = 0
    while counter < 4:
        if agent.web.server is not None:
            break
        counter += 1
        time.sleep(0.1)
    assert agent.web.server is not None
    agent.stop()


def test_default_template_path():
    agent = Agent("jid@server", "password")

    env = get_env(agent.web.app)
    loader = env.loader

    package_loader = loader.loaders[0]
    filesystem_loader = loader.loaders[1]

    assert type(loader) == ChoiceLoader
    assert len(loader.loaders) == 2
    assert type(package_loader) == PackageLoader
    assert type(filesystem_loader) == FileSystemLoader

    assert "internal_tpl_agent.html" in package_loader.list_templates()
    assert "internal_tpl_agent.html" not in filesystem_loader.list_templates()
    assert filesystem_loader.searchpath == ["."]

    agent.stop()


def test_add_template_path():
    agent = Agent("jid@server", "password")

    agent.web.start(templates_path="/tmp/spade")

    env = get_env(agent.web.app)
    loader = env.loader

    assert type(loader) == ChoiceLoader
    assert len(loader.loaders) == 3
    assert type(loader.loaders[0]) == FileSystemLoader
    assert type(loader.loaders[1]) == PackageLoader
    assert type(loader.loaders[2]) == FileSystemLoader

    filesystem_loader = loader.loaders[0]

    assert filesystem_loader.list_templates() == []
    assert filesystem_loader.searchpath == ["/tmp/spade"]

    agent.stop()


def test_check_server():
    agent = make_connected_agent()
    agent.start(auto_register=False)
    port = random.randint(5000, 9999)
    agent.web.start(hostname="0.0.0.0", port=port)

    # wait for web server to be up
    counter = 0
    while counter < 4:
        if agent.web.server is not None:
            break
        counter += 1
        time.sleep(0.1)
    assert agent.web.server is not None

    response = requests.get(f"http://localhost:{port}/")

    sel = Selector(text=response.text)

    assert sel.css("title::text").get() == "fake agent"
    assert sel.css("img::attr(src)").get() == agent.avatar

    assert sel.css("ul.products-list > li").getall() == []

    agent.stop()


async def test_request_home(test_client, loop):
    agent = Agent("jid@server", "password")
    agent.web.setup_routes()
    client = await test_client(agent.web.app)

    response = await client.get("/")
    response = await response.text()

    sel = Selector(text=response)

    assert sel.css("title::text").get() == "jid agent"
    assert sel.css("img::attr(src)").get() == agent.avatar

    assert sel.css("ul.products-list > li").getall() == []

    agent.stop()


async def test_get_messages(test_client, loop):
    agent = Agent("jid@server", "password")
    agent.web.setup_routes()
    client = await test_client(agent.web.app)

    # add messages to trace
    for i in range(5):
        msg = Message(body=str(i), sender="{}@server".format(i), to="receiver@server")
        agent.traces.append(msg)

    response = await client.get("/messages/")
    response = await response.text()

    sel = Selector(text=response)

    assert len(sel.css("ul.timeline > li").getall()) == 6  # num messages + end clock

    agent.stop()


async def test_get_behaviour(test_client, loop):
    class EmptyOneShotBehaviour(OneShotBehaviour):
        async def run(self):
            self.kill()

    agent = Agent("jid@server", "password")
    behaviour = EmptyOneShotBehaviour()
    agent.add_behaviour(behaviour)
    agent.web.setup_routes()

    client = await test_client(agent.web.app)

    response = await client.get("/behaviour/OneShotBehaviour/EmptyOneShotBehaviour/")
    response = await response.text()

    sel = Selector(text=response)

    assert sel.css("section.content-header > h1::text").get().strip() == "OneShotBehaviour/EmptyOneShotBehaviour"
    agent.stop()


async def test_kill_behaviour(test_client, loop):
    class EmptyCyclicBehaviour(CyclicBehaviour):
        async def run(self):
            await asyncio.sleep(0.1)

    agent = Agent("jid@server", "password")
    behaviour = EmptyCyclicBehaviour()
    agent.add_behaviour(behaviour)

    agent.web.setup_routes()
    client = await test_client(agent.web.app)

    await client.get("/behaviour/CyclicBehaviour/EmptyCyclicBehaviour/kill/")

    assert behaviour.is_killed()

    agent.stop()


async def test_get_agent(test_client, loop):
    agent = Agent("jid@server", "password")
    agent.web.setup_routes()
    client = await test_client(agent.web.app)

    jid = "friend@server"
    item = Item(jid=JID.fromstr(jid))

    agent.presence.roster._update_entry(item)

    response = await client.get(f"/agent/{jid}/")
    response = await response.text()

    sel = Selector(text=response)

    assert sel.css("section.content-header > h1::text").get().strip() == jid

    agent.stop()


async def test_unsubscribe_agent(test_client, loop):
    agent = make_connected_agent()
    agent.aiothread.client.enqueue = Mock()
    agent.start(auto_register=False)
    agent.web.setup_routes()
    client = await test_client(agent.web.app)

    jid = "friend@server"
    jid_ = JID.fromstr(jid)
    item = Item(jid=jid_)

    agent.presence.roster._update_entry(item)

    response = await client.get(f"/agent/{jid}/unsubscribe/")

    assert str(response.url.relative()) == f"/agent/{jid}/"

    assert agent.aiothread.client.enqueue.mock_calls
    arg = agent.aiothread.client.enqueue.call_args[0][0]

    assert arg.to == jid_.bare()
    assert arg.type_ == PresenceType.UNSUBSCRIBE

    agent.stop()


async def test_send_agent(test_client, loop):
    agent = make_connected_agent()
    agent.stream.send = CoroutineMock()
    agent.start(auto_register=False)
    agent.web.setup_routes()
    client = await test_client(agent.web.app)

    jid = "friend@server"
    item = Item(jid=JID.fromstr(jid))
    agent.presence.roster._update_entry(item)

    msg = "Hello World"

    response = await client.post(f"/agent/{jid}/send/", data={"message": msg})

    assert str(response.url.relative()) == f"/agent/{jid}/"

    sent = agent.traces.all()[0]

    assert sent[1].sent
    assert sent[1].body == "Hello World"

    agent.stop()


def test_find_behaviour():
    class EmptyOneShotBehaviour(OneShotBehaviour):
        async def run(self):
            pass

    agent = Agent("jid@server", "password")
    behaviour = EmptyOneShotBehaviour()
    agent.add_behaviour(behaviour)

    found_behaviour = agent.web.find_behaviour("OneShotBehaviour/EmptyOneShotBehaviour")

    assert found_behaviour == behaviour

    agent.stop()


def test_find_behaviour_fail():
    agent = Agent("jid@server", "password")
    found_behaviour = agent.web.find_behaviour("OneShotBehaviour/EmptyOneShotBehaviour")

    assert found_behaviour is None

    agent.stop()


async def test_add_get(test_client, loop):
    agent = Agent("jid@server", "password")
    agent.web.add_get("/test", lambda request: {"number": 42}, "examples/hello.html")

    agent.web.setup_routes()
    client = await test_client(agent.web.app)

    response = await client.get("/test")
    response = await response.text()

    sel = Selector(text=response)
    assert sel.css("h1::text").get().strip() == "42"

    agent.stop()


async def test_add_post(test_client, loop):
    agent = Agent("jid@server", "password")

    async def handle_post(request):
        form = await request.post()
        number = form["number"]
        return {"number": number}

    agent.web.add_post("/test", handle_post, "examples/hello.html")
    agent.web.setup_routes()
    client = await test_client(agent.web.app)

    response = await client.post("/test", data={"number": 1024})
    response = await response.text()

    sel = Selector(text=response)
    assert sel.css("h1::text").get() == "1024"

    agent.stop()


async def test_stop(test_client, loop):
    agent = Agent("jid@server", "password")
    agent.web.setup_routes()
    client = await test_client(agent.web.app)

    response = await client.get("/stop")
    response = await response.text()

    sel = Selector(text=response)
    assert sel.css("div.alert-warning > span::text").get().strip() == "Agent is stopping now."

    with LogCapture() as log:
        try:
            await client.get("/stop/now/", timeout=0.0005)
        except requests.exceptions.ReadTimeout:
            pass

        log.check_present(('spade.Web', 'WARNING', "Stopping agent from web interface."))

    counter = 5
    while agent.is_alive() and counter > 0:
        counter -= 0.5
        time.sleep(0.5)

    assert not agent.is_alive()


async def test_add_get_json(test_client, loop):

    async def controller(request):
        return {"number": 42}

    agent = Agent("jid@server", "password")
    agent.web.add_get("/test", controller, None)

    agent.web.setup_routes()
    client = await test_client(agent.web.app)

    response = await client.get("/test")
    assert response.status == 200

    data = await response.json()
    assert data["number"] == 42

    agent.stop()


async def test_add_post_json(test_client, loop):

    async def handle_post(request):
        form = await request.post()
        number = form["number"]
        return {"number": int(number)}

    agent = Agent("jid@server", "password")
    agent.web.add_post("/test", handle_post, None)

    agent.web.setup_routes()
    client = await test_client(agent.web.app)

    response = await client.post("/test", data={"number": 1024})
    assert response.status == 200

    data = await response.json()
    assert data["number"] == 1024

    agent.stop()
