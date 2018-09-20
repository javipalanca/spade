# coding=utf-8
import datetime
import itertools

from aioxmpp import JID


def _agent_in_msg(agent, msg):
    return msg.to == agent or msg.sender == agent


class TraceStore(object):
    """Stores and allows queries about events."""
    def __init__(self, size):
        self.size = size
        self.store = []

    def reset(self):
        """Resets the trace store"""
        self.store = []

    def append(self, event, category=None):
        """
        Adds a new event to the trace store.
        The event may hava a category

        Args:
          event (spade.message.Message): the event to be stored
          category (str, optional): a category to classify the event (Default value = None)

        """
        date = datetime.datetime.now()
        self.store.insert(0, (date, event, category))
        if len(self.store) > self.size:
            del self.store[-1]

    def len(self):
        """
        Length of the store

        Returns:
          int: the size of the trace store

        """
        return len(self.store)

    def all(self, limit=None):
        """
        Returns all the events, until a limit if defined

        Args:
          limit (int, optional): the max length of the events to return (Default value = None)

        Returns:
          list: a list of events

        """
        return self.store[:limit][::-1]

    def received(self, limit=None):
        """
        Returns all the events that have been received (excluding sent events), until a limit if defined

        Args:
          limit (int, optional): the max length of the events to return (Default value = None)

        Returns:
          list: a list of received events

        """
        return list(itertools.islice((itertools.filterfalse(lambda x: x[1].sent, self.store)), limit))[::-1]

    def filter(self, limit=None, to=None, category=None):
        """
        Returns the events that match the filters

        Args:
          limit (int, optional): the max length of the events to return (Default value = None)
          to (str, optional): only events that have been sent or received by 'to' (Default value = None)
          category (str, optional): only events belonging to the category (Default value = None)

        Returns:
          list: a list of filtered events

        """
        if category and not to:
            msg_slice = itertools.islice((x for x in self.store if x[2] == category), limit)
        elif to and not category:
            to = JID.fromstr(to)
            msg_slice = itertools.islice((x for x in self.store if _agent_in_msg(to, x[1])), limit)
        elif to and category:
            to = JID.fromstr(to)
            msg_slice = itertools.islice((x for x in self.store if _agent_in_msg(to, x[1]) and x[2] == category), limit)
        else:
            msg_slice = self.all(limit=limit)
            return msg_slice

        return list(msg_slice)[::-1]
