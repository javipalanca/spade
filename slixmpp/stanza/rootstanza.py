
# Slixmpp: The Slick XMPP Library
# Copyright (C) 2010  Nathanael C. Fritz
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import logging

from slixmpp.exceptions import XMPPError, IqError, IqTimeout
from slixmpp.stanza import Error
from slixmpp.xmlstream import ET, StanzaBase, register_stanza_plugin


log = logging.getLogger(__name__)


class RootStanza(StanzaBase):

    """
    A top-level XMPP stanza in an XMLStream.

    The RootStanza class provides a more XMPP specific exception
    handler than provided by the generic StanzaBase class.

    Methods:
        exception -- Overrides StanzaBase.exception
    """

    def exception(self, e):
        """
        Create and send an error reply.

        Typically called when an event handler raises an exception.
        The error's type and text content are based on the exception
        object's type and content.

        Overrides StanzaBase.exception.

        Arguments:
            e -- Exception object
        """
        if isinstance(e, IqError):
            # We received an Iq error reply, but it wasn't caught
            # locally. Using the condition/text from that error
            # response could leak too much information, so we'll
            # only use a generic error here.
            reply = self.reply()
            reply['error']['condition'] = 'undefined-condition'
            reply['error']['text'] = 'External error'
            reply['error']['type'] = 'cancel'
            log.warning('You should catch IqError exceptions', exc_info=True)
            reply.send()
        elif isinstance(e, IqTimeout):
            reply = self.reply()
            reply['error']['condition'] = 'remote-server-timeout'
            reply['error']['type'] = 'wait'
            log.warning('You should catch IqTimeout exceptions', exc_info=True)
            reply.send()
        elif isinstance(e, XMPPError):
            # We raised this deliberately
            keep_id = self['id']
            reply = self.reply(clear=e.clear)
            reply['id'] = keep_id
            reply['error']['condition'] = e.condition
            reply['error']['text'] = e.text
            reply['error']['type'] = e.etype
            if e.by:
                reply["error"]["by"] = e.by
            if e.extension is not None:
                # Extended error tag
                extxml = ET.Element("{%s}%s" % (e.extension_ns, e.extension),
                                    e.extension_args)
                reply['error'].append(extxml)
            reply.send()
        else:
            # We probably didn't raise this on purpose, so send an error stanza
            keep_id = self['id']
            reply = self.reply()
            reply['id'] = keep_id
            reply['error']['condition'] = 'undefined-condition'
            reply['error']['text'] = "Slixmpp got into trouble."
            reply['error']['type'] = 'cancel'
            reply.send()
            # log the error
            log.exception('Error handling {%s}%s stanza',
                          self.namespace, self.name)
            # Finally raise the exception to a global exception handler
            self.stream.exception(e)

register_stanza_plugin(RootStanza, Error)
