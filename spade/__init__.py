# -*- coding: utf-8 -*-
import asyncio
import logging
from typing import Union, List

from . import agent
from . import behaviour
from . import message
from . import template
from .agent import AgentType
from .container import run_container as run  # noqa: F401

__author__ = """Javi Palanca"""
__email__ = "jpalanca@gmail.com"
__version__ = "3.2.2"

__all__ = ["agent", "behaviour", "message", "template"]

logger = logging.getLogger("SPADE")


async def wait_until_finished(agents: Union[List[AgentType], AgentType]) -> None:
    if not isinstance(agents, list):
        agents = [agents]
    try:
        while any([agent.is_alive() for agent in agents]):
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.warning("Keyboard interrupt received. Stopping SPADE...")
    for agent in agents:
        logger.info(f"Stopping agent {agent.jid}")
        await agent.stop()
