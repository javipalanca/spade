import logging
from abc import ABCMeta

from spade.message import MessageBase

logger = logging.getLogger('spade.Template')


# TODO: Include regex in templates

class BaseTemplate(metaclass=ABCMeta):
    """Template operators"""
    def __and__(self, other):
        """Implementation of & operator"""
        if not issubclass(other.__class__, BaseTemplate):
            raise TypeError("Expressions must be of class Template")
        return ANDTemplate(self, other)

    def __iand__(self, other):
        """Implementation of &= operator"""
        return self & other

    def __or__(self, other):
        """Implementation of | operator"""
        if not issubclass(other.__class__, BaseTemplate):
            raise TypeError("Expressions must be of class Template")
        return ORTemplate(self, other)

    def __ior__(self, other):
        """Implementation of |= operator"""
        return self | other

    def __xor__(self, other):
        """Implementation of ^ operator"""
        if not issubclass(other.__class__, BaseTemplate):
            raise TypeError("Expressions must be of class Template")
        return XORTemplate(self, other)

    def __ixor__(self, other):
        """Implementation of ^= operator"""
        return self ^ other

    def __invert__(self):
        """Implementation of ~ operator"""
        return NOTTemplate(self)


class NOTTemplate(BaseTemplate):
    """ """
    def __init__(self, expr):
        self.expr = expr

    def match(self, message):
        """ """
        return not (self.expr.match(message))


class ORTemplate(BaseTemplate):
    """ """
    def __init__(self, expr1, expr2):
        self.expr1 = expr1
        self.expr2 = expr2

    def match(self, message):
        """ """
        return self.expr1.match(message) | self.expr2.match(message)


class ANDTemplate(BaseTemplate):
    """ """
    def __init__(self, expr1, expr2):
        self.expr1 = expr1
        self.expr2 = expr2

    def match(self, message):
        """ """
        return self.expr1.match(message) & self.expr2.match(message)


class XORTemplate(BaseTemplate):
    """ """
    def __init__(self, expr1, expr2):
        self.expr1 = expr1
        self.expr2 = expr2

    def match(self, message):
        """ """
        return self.expr1.match(message) ^ self.expr2.match(message)


class Template(BaseTemplate, MessageBase):
    """Template for message matching"""
    def __str__(self):
        s = f'<template to="{self.to}" from="{self.sender}" thread="{self.thread}" metadata={self.metadata}>'
        if self.body:
            s += "\n" + self.body + "\n"
        s += "</template>"
        return s
