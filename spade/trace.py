# coding=utf-8
import datetime
import itertools

from aioxmpp import JID


def _agent_in_msg(agent, msg):
    return msg.to == agent or msg.sender == agent


class TraceStore(object):
    """
    Stores and allows queries about events.
    """
    def __init__(self, size):
        self.size = size
        self.store = []

    def reset(self):
        """
        Resets the trace store
        """
        self.store = []

    def append(self, event, category=None):
        """
        Adds a new event to the trace store.
        The event may hava a category
        :param event: the event to be stored
        :type event: spade.message.Message
        :param category: a category to classify the event
        :type category: str
        """
        date = datetime.datetime.now()
        self.store.insert(0, (date, event, category))
        if len(self.store) > self.size:
            del self.store[-1]

    def len(self):
        """
        :return: the size of the trace store
        :rtype: int
        """
        return len(self.store)

    def all(self, limit=None):
        """
        Returns all the events, until a limit if defined
        :param limit: the max length of the events to return
        :type limit: int
        :return: a list of events
        :rtype: list
        """
        return self.store[:limit][::-1]

    def received(self, limit=None):
        """
        Returns all the events that have been received (excluding sent events), until a limit if defined
        :param limit: the max length of the events to return
        :type limit: int
        :return: a list of received events
        :rtype: list
        """
        return list(itertools.islice((itertools.filterfalse(lambda x: x[1].sent, self.store)), limit))[::-1]

    def filter(self, limit=None, to=None, category=None):
        """
        Returns the events that match the filters
        :param limit: the max length of the events to return
        :type limit: int
        :param to: only events that have been sent or received by 'to'
        :type to: str
        :param category: only events belonging to the category
        :type category: str
        :return: a list of filtered events
        :rtype: list
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
