import asyncio
from unittest.mock import Mock

import requests
from aiohttp import web
from aiohttp_jinja2 import get_env
from jinja2 import ChoiceLoader, FileSystemLoader, PackageLoader
from parsel import Selector
from slixmpp import JID, Presence
from testfixtures import LogCapture

from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
from spade.presence import PresenceType, PresenceShow
from .factories import MockedAgentFactory, MockedPresenceAgentFactory


async def test_web():
    agent = MockedAgentFactory()
    await agent.start(auto_register=False)

    agent.web.start(port=10000)

    assert agent.web.app is not None

    counter = 0
    while counter < 4:
        if agent.web.server is not None:
            break
        counter += 1
        await asyncio.sleep(0.1)
    assert agent.web.server is not None
    await agent.stop()


async def test_default_template_path():
    agent = Agent("jid@server", "password")

    env = get_env(agent.web.app)
    loader = env.loader

    package_loader = loader.loaders[0]
    filesystem_loader = loader.loaders[1]

    assert isinstance(loader, ChoiceLoader)
    assert len(loader.loaders) == 2
    assert isinstance(package_loader, PackageLoader)
    assert isinstance(filesystem_loader, FileSystemLoader)

    assert "internal_tpl_agent.html" in package_loader.list_templates()
    assert "internal_tpl_agent.html" not in filesystem_loader.list_templates()
    assert filesystem_loader.searchpath == ["."]

    await agent.stop()


async def test_add_template_path_init():
    agent = Agent("jid@server", "password")

    agent.web.start(templates_path="/tmp/spade")

    env = get_env(agent.web.app)
    loader = env.loader

    assert isinstance(loader, ChoiceLoader)
    assert len(loader.loaders) == 3
    assert isinstance(loader.loaders[0], FileSystemLoader)
    assert isinstance(loader.loaders[1], PackageLoader)
    assert isinstance(loader.loaders[2], FileSystemLoader)

    filesystem_loader = loader.loaders[0]

    assert filesystem_loader.list_templates() == []
    assert filesystem_loader.searchpath == ["/tmp/spade"]

    await agent.stop()


async def test_add_template_path():
    agent = Agent("jid@server", "password")

    agent.web.start()
    agent.web.add_template_path(templates_path="/tmp/spade")

    env = get_env(agent.web.app)
    loader = env.loader

    assert isinstance(loader, ChoiceLoader)
    assert len(loader.loaders) == 3
    assert isinstance(loader.loaders[0], FileSystemLoader)
    assert isinstance(loader.loaders[1], PackageLoader)
    assert isinstance(loader.loaders[2], FileSystemLoader)

    filesystem_loader = loader.loaders[0]

    assert filesystem_loader.list_templates() == []
    assert filesystem_loader.searchpath == ["/tmp/spade"]

    await agent.stop()


async def test_check_server(aiohttp_client):
    agent = MockedPresenceAgentFactory()
    await agent.start(auto_register=False)

    agent.web.setup_routes()

    client = await aiohttp_client(agent.web.app)
    response = await client.get("/spade")

    assert response.status == 200

    text = await response.text()

    sel = Selector(text=text)

    assert sel.css("title::text").get() == "fake agent"
    assert sel.css("img::attr(src)").get() == agent.avatar

    assert sel.css("ul.products-list > li").getall() == []

    await agent.stop()


async def test_request_home(aiohttp_client):
    agent = MockedAgentFactory(jid="jid@server", password="password")
    await agent.start(auto_register=False)

    agent.web.setup_routes()
    client = await aiohttp_client(agent.web.app)

    response = await client.get("/spade")
    response = await response.text()

    sel = Selector(text=response)

    assert sel.css("title::text").get() == "jid agent"
    assert sel.css("img::attr(src)").get() == agent.avatar

    assert sel.css("ul.products-list > li").getall() == []

    await agent.stop()


async def test_get_messages(aiohttp_client):
    agent = Agent("jid@server", "password")
    agent.web.setup_routes()
    client = await aiohttp_client(agent.web.app)

    # add messages to trace
    for i in range(5):
        msg = Message(body=str(i), sender="{}@server".format(i), to="receiver@server")
        agent.traces.append(msg)

    response = await client.get("/spade/messages/")
    response = await response.text()

    sel = Selector(text=response)

    assert len(sel.css("ul.timeline > li").getall()) == 6  # num messages + end clock

    await agent.stop()


async def test_get_behaviour(aiohttp_client):
    class EmptyOneShotBehaviour(OneShotBehaviour):
        async def run(self):
            self.kill()

    agent = Agent("jid@server", "password")
    behaviour = EmptyOneShotBehaviour()
    agent.add_behaviour(behaviour)
    agent.web.setup_routes()

    client = await aiohttp_client(agent.web.app)

    response = await client.get(
        "/spade/behaviour/OneShotBehaviour/EmptyOneShotBehaviour/"
    )
    response = await response.text()

    sel = Selector(text=response)

    assert (
        sel.css("section.content-header > h1::text").get().strip()
        == "OneShotBehaviour/EmptyOneShotBehaviour"
    )
    await agent.stop()


async def test_kill_behaviour(aiohttp_client):
    class EmptyCyclicBehaviour(CyclicBehaviour):
        async def run(self):
            await asyncio.sleep(0.1)

    agent = Agent("jid@server", "password")
    behaviour = EmptyCyclicBehaviour()
    agent.add_behaviour(behaviour)

    agent.web.setup_routes()
    client = await aiohttp_client(agent.web.app)

    await client.get("/spade/behaviour/CyclicBehaviour/EmptyCyclicBehaviour/kill/")

    assert behaviour.is_killed()

    await agent.stop()


async def test_get_agent(aiohttp_client):
    agent = MockedPresenceAgentFactory(jid="jid@server.com/work", password="password")
    await agent.start(auto_register=False)

    agent.web.setup_routes()
    client = await aiohttp_client(agent.web.app)

    jid = JID("friend@server.com/work")
    # Create a presence stanza with the desired change
    stanza = Presence()
    stanza["from"] = jid
    stanza["show"] = PresenceShow.CHAT.value
    # Trigger the 'changed_status' event with the presence stanza
    agent.client.event("changed_status", stanza)

    response = await client.get(f"/spade/agent/{jid.bare}/")
    response = await response.text()

    sel = Selector(text=response)

    assert sel.css("section.content-header > h1::text").get().strip() == jid.bare

    await agent.stop()


async def test_unsubscribe_agent(aiohttp_client, jid):
    agent = MockedPresenceAgentFactory()
    await agent.start(auto_register=False)

    agent.client.send_presence = Mock()

    agent.web.setup_routes()
    client = await aiohttp_client(agent.web.app)

    agent.client.update_roster(jid=jid, name="friend", subscription="both")

    response = await client.get(f"/spade/agent/unsubscribe/{jid}/")

    assert str(response.url.relative()) == "/spade"

    assert agent.client.send_presence.mock_calls
    arg = agent.client.send_presence.call_args[1]

    assert arg["pto"] == jid.bare
    assert arg["ptype"] == PresenceType.UNSUBSCRIBE.value

    await agent.stop()


async def test_send_agent(aiohttp_client, jid, iq):
    agent = MockedPresenceAgentFactory()
    await agent.start(auto_register=False)

    agent.client.send = Mock()
    agent.web.setup_routes()
    client = await aiohttp_client(agent.web.app)

    agent.presence.handle_roster_update(iq)

    msg = "Hello World"

    response = await client.post(f"/spade/agent/{jid}/send/", data={"message": msg})

    assert response.status == 200
    assert str(response.url.relative()) == f"/spade/agent/{jid}/"

    sent = agent.traces.all()[0]

    assert sent[1].sent
    assert sent[1].body == "Hello World"

    await agent.stop()


async def test_find_behaviour():
    class EmptyOneShotBehaviour(OneShotBehaviour):
        async def run(self):
            pass

    agent = MockedAgentFactory()
    behaviour = EmptyOneShotBehaviour()
    agent.add_behaviour(behaviour)
    found_behaviour = agent.web.find_behaviour("OneShotBehaviour/EmptyOneShotBehaviour")

    assert found_behaviour == behaviour

    await agent.stop()


async def test_find_behaviour_fail():
    agent = Agent("jid@server", "password")
    found_behaviour = agent.web.find_behaviour("OneShotBehaviour/EmptyOneShotBehaviour")

    assert found_behaviour is None

    await agent.stop()


async def test_add_get(aiohttp_client):
    agent = MockedAgentFactory()

    async def controller(request):
        return {"number": 42}

    agent.web.add_get("/test", controller, "tests/hello.html")

    await agent.start(auto_register=False)

    agent.web.setup_routes()
    client = await aiohttp_client(agent.web.app)

    response = await client.get("/test")

    assert response.status == 200

    response = await response.text()

    sel = Selector(text=response)
    assert sel.css("h1::text").get().strip() == "42"

    await agent.stop()


async def test_add_get_raw(aiohttp_client):
    agent = Agent("jid@server", "password")
    agent.web.add_get(
        "/test",
        lambda request: web.Response(text="Hello Raw Get"),
        template=None,
        raw=True,
    )

    agent.web.setup_routes()
    client = await aiohttp_client(agent.web.app)

    response = await client.get("/test")
    response = await response.text()

    assert response == "Hello Raw Get"

    await agent.stop()


async def test_add_post(aiohttp_client):
    agent = Agent("jid@server", "password")

    async def handle_post(request):
        form = await request.post()
        number = form["number"]
        return {"number": number}

    agent.web.add_post("/test", handle_post, "tests/hello.html")
    agent.web.setup_routes()
    client = await aiohttp_client(agent.web.app)

    response = await client.post("/test", data={"number": 1024})
    response = await response.text()

    sel = Selector(text=response)
    assert sel.css("h1::text").get() == "1024"

    await agent.stop()


async def test_add_post_raw(aiohttp_client):
    agent = Agent("jid@server", "password")

    async def handle_post(request):
        form = await request.post()
        number = form["number"]
        return web.Response(text="Hello Raw Post Number={}".format(number))

    agent.web.add_post("/test", handle_post, template=None, raw=True)
    agent.web.setup_routes()
    client = await aiohttp_client(agent.web.app)

    response = await client.post("/test", data={"number": 1024})
    response = await response.text()

    assert response == "Hello Raw Post Number=1024"

    await agent.stop()


async def test_stop(aiohttp_client):
    agent = Agent("jid@server", "password")
    agent.web.setup_routes()
    client = await aiohttp_client(agent.web.app)

    response = await client.get("/spade/stop")
    assert response.status == 200

    response = await response.text()

    sel = Selector(text=response)
    assert (
        sel.css("div.alert-warning > span::text").get().strip()
        == "Agent is stopping now."
    )

    with LogCapture() as log:
        try:
            await client.get("/spade/stop/now/", timeout=0.05)
        except requests.exceptions.ReadTimeout:
            pass
        except asyncio.exceptions.TimeoutError:
            pass

        log.check_present(
            ("spade.Web", "WARNING", "Stopping agent from web interface.")
        )

    counter = 5
    while agent.is_alive() and counter > 0:
        counter -= 0.5
        await asyncio.sleep(0.5)

    assert not agent.is_alive()


async def test_add_get_json(aiohttp_client):
    async def controller(request):
        return {"number": 42}

    agent = Agent("jid@server", "password")
    agent.web.add_get("/test", controller, None)

    agent.web.setup_routes()
    client = await aiohttp_client(agent.web.app)

    response = await client.get("/test")
    assert response.status == 200

    data = await response.json()
    assert data["number"] == 42

    await agent.stop()


async def test_add_post_json(aiohttp_client):
    async def handle_post(request):
        form = await request.post()
        number = form["number"]
        return {"number": int(number)}

    agent = Agent("jid@server", "password")
    agent.web.add_post("/test", handle_post, None)

    agent.web.setup_routes()
    client = await aiohttp_client(agent.web.app)

    response = await client.post("/test", data={"number": 1024})
    assert response.status == 200

    data = await response.json()
    assert data["number"] == 1024

    await agent.stop()


async def test_add_menu_entry(aiohttp_client):
    agent = MockedPresenceAgentFactory()
    await agent.start(auto_register=False)
    agent.web.setup_routes()

    agent.web.add_menu_entry("Test", "/test", "fa fa-test")

    client = await aiohttp_client(agent.web.app)
    response = await client.get("/spade")

    assert response.status == 200

    # get html from response
    response = await response.text()
    # look for menu entry
    sel = Selector(text=response)

    assert len(sel.css("ul.sidebar-menu > li").getall()) == 2

    # get second li element from sidebar-menu
    menu_entry = sel.css("ul.sidebar-menu > li").getall()[1]
    menu_entry = Selector(text=menu_entry)
    assert menu_entry.css("li > a > span::text").get().strip() == "Test"
    assert menu_entry.css("a > i::attr(class)").get().strip() == "fa fa-test"
    assert menu_entry.css("a::attr(href)").get().strip() == "/test"
