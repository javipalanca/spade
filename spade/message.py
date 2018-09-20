import logging

import aioxmpp
import aioxmpp.forms.xso as forms_xso

SPADE_X_METADATA = "spade:x:metadata"

logger = logging.getLogger('spade.Message')


class MessageBase(object):
    """ """
    def __init__(self, to=None, sender=None, body=None, thread=None, metadata=None):
        self._to, self._sender = None, None
        self.to = to
        self.sender = sender
        self.body = body
        self.thread = thread
        self.sent = False

        if metadata is None:
            self.metadata = {}
        else:
            self.metadata = metadata

    @classmethod
    def from_node(cls, node):
        """
        Creates a new spade.message.Message from an aixoxmpp.stanza.Message

        Args:
          node (aioxmpp.stanza.Message): an aioxmpp Message

        Returns:
          spade.message.Message: a new spade Message

        """
        if not isinstance(node, aioxmpp.stanza.Message):
            raise AttributeError("node must be a aioxmpp.stanza.Message instance")
        msg = cls()
        msg._to = node.to
        msg._sender = node.from_
        if None in node.body:
            msg.body = node.body[None]
        else:
            for key in node.body.keys():
                msg.body = node.body[key]
                break
        msg.thread = node.thread

        for data in node.xep0004_data:
            if data.title == SPADE_X_METADATA:
                for field in data.fields:
                    msg.set_metadata(field.var, field.values[0])

        return msg

    @property
    def to(self):
        """
        Gets the jid of the receiver.

        Returns:
          aioxmpp.JID: jid of the receiver

        """
        return self._to

    @to.setter
    def to(self, jid):
        """
        Set jid of the receiver.

        Args:
          jid (str): the jid of the receiver.

        """
        self._to = aioxmpp.JID.fromstr(jid) if jid is not None else None

    @property
    def sender(self):
        """
        Get jid of the sender

        Returns:
          aioxmpp.JID: jid of the sender

        """
        return self._sender

    @sender.setter
    def sender(self, jid):
        """
        Set jid of the sender

        Args:
          jid (str): jid of the sender

        """
        self._sender = aioxmpp.JID.fromstr(jid) if jid is not None else None

    def set_metadata(self, key, value):
        """
        Add a new metadata to the message

        Args:
          key (str): name of the metadata
          value (str): value of the metadata

        """
        self.metadata[key] = value

    def get_metadata(self, key):
        """
        Get the value of a metadata. Returns None if metadata does not exist.

        Args:
          key (str): name of the metadata

        Returns:
          str: the value of the metadata (or None)

        """
        return self.metadata[key] if key in self.metadata else None

    def match(self, message):
        """
        Returns wether a message matches with this message or not.
        The message can be a Message object or a Template object.

        Args:
          message (spade.message.Message): the message to match to

        Returns:
          bool: wether the message matches or not

        """
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

    @property
    def id(self):
        """ """
        return id(self)

    def __eq__(self, other):
        return self.match(other)


class Message(MessageBase):
    """ """
    def make_reply(self):
        """
        Creates a copy of the message, exchanging sender and receiver

        Returns:
          spade.message.Message: a new message with exchanged sender and receiver

        """
        return Message(
            to=str(self.sender),
            sender=str(self.to),
            body=self.body,
            thread=self.thread,
            metadata=self.metadata
        )

    def prepare(self):
        """
        Returns an aioxmpp.stanza.Message built from the Message and prepared to be sent.

        Returns:
          aioxmpp.stanza.Message: the message prepared to be sent

        """

        msg = aioxmpp.stanza.Message(
            to=self.to,
            from_=self.sender,
            type_=aioxmpp.MessageType.CHAT,
        )

        msg.body[None] = self.body
        msg.thread = self.thread

        # Send metadata using xep-0004: Data Forms (https://xmpp.org/extensions/xep-0004.html)
        if len(self.metadata):
            data = forms_xso.Data(type_=forms_xso.DataType.FORM)

            for name, value in self.metadata.items():
                data.fields.append(
                    forms_xso.Field(
                        var=name,
                        type_=forms_xso.FieldType.TEXT_SINGLE,
                        values=[value],
                    )
                )

            data.title = SPADE_X_METADATA
            msg.xep0004_data = [data]

        return msg

    def __str__(self):
        return self.prepare().__str__()
