# coding=utf-8
import datetime
from functools import lru_cache
import itertools

from aioxmpp import JID


def _agent_in_msg(agent, msg):
    return msg.to == agent or msg.sender == agent


class TraceStore(object):
    def __init__(self, size):
        self.size = size
        self.store = []

    def reset(self):
        self.store = []
        self.filter.cache_clear()

    def append(self, trace, category=None):
        date = datetime.datetime.now()
        self.store.insert(0, (date, trace, category))
        if len(self.store) > self.size:
            del self.store[-1]

    def len(self):
        return len(self.store)

    def all(self, limit=None):
        return self.store[:limit:-1]

    def received(self, limit=None):
        return list(itertools.islice((itertools.filterfalse(lambda x: x[1].sent, self.store)), limit))[::-1]

    @lru_cache(maxsize=32)
    def filter(self, limit=None, to=None, category=None):
        if category and not to:
            slice = itertools.islice((x for x in self.store if x[2] == category), limit)
        elif to and not category:
            to = JID.fromstr(to)
            slice = itertools.islice((x for x in self.store if _agent_in_msg(to, x[1])), limit)
        elif to and category:
            to = JID.fromstr(to)
            slice = itertools.islice((x for x in self.store if _agent_in_msg(to, x[1]) and x[2] == category), limit)
        else:
            slice = self.all(limit=limit)

        return list(slice)[::-1]

