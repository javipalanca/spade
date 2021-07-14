# -*- coding: utf-8 -*-

from . import agent
from . import behaviour
from . import message
from . import template
from .container import stop_container as quit_spade  # noqa: F401

__author__ = """Javi Palanca"""
__email__ = "jpalanca@gmail.com"
__version__ = "3.2.0"

__all__ = ["agent", "behaviour", "message", "template"]
