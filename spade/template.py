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

    def __init__(self, to=None, from_=None, body=None, thread=None, metadata=None):
        if metadata is None:
            metadata = {}
        self.to = aioxmpp.JID.fromstr(to) if to is not None else to
        self.from_ = aioxmpp.JID.fromstr(from_) if from_ is not None else from_
        self.body = body
        self.thread = thread
        self.metadata = metadata

    def match(self, message):
        if self.to and message.to != self.to:
            return False

        if self.from_ and message.from_ != self.from_:
            return False

        if self.body and message.body != self.body:
            return False

        if self.thread and message.thread != self.thread:
            return False

        for key, value in self.metadata:
            if message.get_metadata(key) != value:
                return False

        logger.debug(f"message matched {self} == {message}")
        return True

    def __str__(self):
        s = f'<template to="{self.to}" from="{self.from_}" thread="{self.thread}" metadata={self.metadata}>'
        if self.body:
            s += self.body
        s += "</template>"
        return s
