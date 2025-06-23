
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2011  Nathanael C. Fritz
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
from typing import Set, ClassVar
from slixmpp.xmlstream import StanzaBase, ElementBase
from slixmpp.xmlstream.xmlstream import InvalidCABundle

import logging
log = logging.getLogger(__name__)


class STARTTLS(StanzaBase):
    """

    .. code-block:: xml

         <starttls xmlns='urn:ietf:params:xml:ns:xmpp-tls'/>

    """
    name = 'starttls'
    namespace = 'urn:ietf:params:xml:ns:xmpp-tls'
    interfaces = {'required'}
    plugin_attrib = name

    def get_required(self):
        return True


class Proceed(StanzaBase):
    """

    .. code-block:: xml

        <proceed xmlns='urn:ietf:params:xml:ns:xmpp-tls'/>

    """
    name = 'proceed'
    namespace = 'urn:ietf:params:xml:ns:xmpp-tls'
    interfaces: ClassVar[Set[str]] = set()

    def exception(self, e: Exception) -> None:
        log.exception('Error handling {%s}%s stanza',
                      self.namespace, self.name)
        if isinstance(e, InvalidCABundle):
            raise e


class Failure(StanzaBase):
    """

    .. code-block:: xml

        <failure xmlns='urn:ietf:params:xml:ns:xmpp-tls'/>

    """
    name = 'failure'
    namespace = 'urn:ietf:params:xml:ns:xmpp-tls'
    interfaces: ClassVar[Set[str]] = set()
