import logging

import aioxmpp

logger = logging.getLogger('spade.Template')


# TODO: Include regex in templates

class BaseTemplate:
    """
    Template operators
    """

    def match(self, message):
        return False

    def __and__(self, other):
        """Implementation of & operator"""
        return ANDTemplate(self, other)

    def __rand__(self, other):
        """Implementation of &= operator"""
        return self & other

    def __or__(self, other):
        """Implementation of | operator"""
        return ORTemplate(self, other)

    def __ror__(self, other):
        """Implementation of |= operator"""
        return self | other

    def __xor__(self, other):
        """Implementation of ^ operator"""
        return XORTemplate(self, other)

    def __rxor__(self, other):
        """Implementation of ^= operator"""
        return self ^ other

    def __invert__(self):
        """Implementation of ~ operator"""
        return NOTTemplate(self)


class NOTTemplate(BaseTemplate):
    def __init__(self, expr):
        self.expr = expr

    def match(self, message):
        return not (self.expr.match(message))


class ORTemplate(BaseTemplate):
    def __init__(self, expr1, expr2):
        self.expr1 = expr1
        self.expr2 = expr2

    def match(self, message):
        return self.expr1.match(message) | self.expr2.match(message)


class ANDTemplate(BaseTemplate):
    def __init__(self, expr1, expr2):
        self.expr1 = expr1
        self.expr2 = expr2

    def match(self, message):
        return self.expr1.match(message) & self.expr2.match(message)


class XORTemplate(BaseTemplate):
    def __init__(self, expr1, expr2):
        self.expr1 = expr1
        self.expr2 = expr2

    def match(self, message):
        return self.expr1.match(message) ^ self.expr2.match(message)


class Template(BaseTemplate):
    """
    Template for message matching
    """

    def __init__(self, to=None, sender=None, body=None, thread=None, metadata=None):
        if metadata is None:
            metadata = {}
        self._to = aioxmpp.JID.fromstr(to) if to is not None else to
        self._sender = aioxmpp.JID.fromstr(sender) if sender is not None else sender
        self.body = body
        self.thread = thread
        self.metadata = metadata

    @property
    def to(self):
        return self._to

    @to.setter
    def to(self, jid):
        self._to = aioxmpp.JID.fromstr(jid) if jid is not None else None

    @property
    def sender(self):
        return self._sender

    @sender.setter
    def sender(self, jid):
        self._sender = aioxmpp.JID.fromstr(jid) if jid is not None else None

    def match(self, message):
        if self.to and message.to != self.to:
            return False

        if self.sender and message.sender != self.sender:
            return False

        if self.body and message.body != self.body:
            return False

        if self.thread and message.thread != self.thread:
            return False

        for key, value in self.metadata.items():
            if message.get_metadata(key) != value:
                return False

        logger.debug(f"message matched {self} == {message}")
        return True

    def __str__(self):
        s = f'<template to="{self.to}" from="{self.sender}" thread="{self.thread}" metadata={self.metadata}>'
        if self.body:
            s += self.body
        s += "</template>"
        return s
