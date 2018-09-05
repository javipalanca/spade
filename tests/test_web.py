import random
import time
import requests
from parsel import Selector

from aiohttp_jinja2 import get_env
from jinja2 import ChoiceLoader, FileSystemLoader, PackageLoader

from tests.utils import make_connected_agent


def test_web():
    agent = make_connected_agent()
    agent.start()
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
    agent = make_connected_agent()

    agent.web.start()

    env = get_env(agent.web.app)
    loader = env.loader

    package_loader = loader.loaders[0]
    filesystem_loader = loader.loaders[1]

    assert type(loader) == ChoiceLoader
    assert len(loader.loaders) == 2
    assert type(package_loader) == PackageLoader
    assert type(filesystem_loader) == FileSystemLoader

    assert "agent.html" in package_loader.list_templates()
    assert "agent.html" not in filesystem_loader.list_templates()
    assert filesystem_loader.searchpath == ["."]


def test_add_template_path():
    agent = make_connected_agent()

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


def test_request_home():
    agent = make_connected_agent()
    agent.start()
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
