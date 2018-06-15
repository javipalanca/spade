import time

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
