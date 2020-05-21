import logging

import aioxmpp
import aioxmpp.forms.xso as forms_xso

SPADE_X_METADATA = "spade:x:metadata"

logger = logging.getLogger("spade.Message")


class MessageBase(object):
    """ """

    def __init__(self, to=None, sender=None, body=None, thread=None, metadata=None):
        self.sent = False
        self._to, self._sender, self._body, self._thread = None, None, None, None
        self.to = to
        self.sender = sender
        self.body = body
        self.thread = thread

        if metadata is None:
            self.metadata = {}
        else:
            for key, value in metadata.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    raise TypeError("Key and Value of metadata MUST be strings")
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

        for data in node.xep0004_data:
            if data.title == SPADE_X_METADATA:
                for field in data.fields:
                    if field.var != "_thread_node":
                        msg.set_metadata(field.var, field.values[0])
                    else:
                        msg.thread = field.values[0]

        return msg

    @property
    def to(self) -> aioxmpp.JID:
        """
        Gets the jid of the receiver.

        Returns:
          aioxmpp.JID: jid of the receiver

        """
        return self._to

    @to.setter
    def to(self, jid: str):
        """
        Set jid of the receiver.

        Args:
          jid (str): the jid of the receiver.

        """
        if jid is not None and not isinstance(jid, str):
            raise TypeError("'to' MUST be a string")
        self._to = aioxmpp.JID.fromstr(jid) if jid is not None else None

    @property
    def sender(self) -> aioxmpp.JID:
        """
        Get jid of the sender

        Returns:
          aioxmpp.JID: jid of the sender

        """
        return self._sender

    @sender.setter
    def sender(self, jid: str):
        """
        Set jid of the sender

        Args:
          jid (str): jid of the sender

        """
        if jid is not None and not isinstance(jid, str):
            raise TypeError("'sender' MUST be a string")
        self._sender = aioxmpp.JID.fromstr(jid) if jid is not None else None

    @property
    def body(self) -> str:
        """
        Get body of the message
        Returns:
            str: the body of the message
        """
        return self._body

    @body.setter
    def body(self, body: str):
        """
        Set body of the message
        Args:
            body (str): The body of the message
        """
        if body is not None and not isinstance(body, str):
            raise TypeError("'body' MUST be a string")
        self._body = body

    @property
    def thread(self) -> str:
        """
        Get Thread of the message

        Returns:
            str: thread id
        """
        return self._thread

    @thread.setter
    def thread(self, value: str):
        """
        Set thread id of the message

        Args:
            value (str): the thread id

        """
        if value is not None and not isinstance(value, str):
            raise TypeError("'thread' MUST be a string")
        self._thread = value

    def set_metadata(self, key: str, value: str):
        """
        Add a new metadata to the message

        Args:
          key (str): name of the metadata
          value (str): value of the metadata

        """
        if not isinstance(key, str) or not isinstance(value, str):
            raise TypeError("'key' and 'value' of metadata MUST be strings")
        self.metadata[key] = value

    def get_metadata(self, key) -> str:
        """
        Get the value of a metadata. Returns None if metadata does not exist.

        Args:
          key (str): name of the metadata

        Returns:
          str: the value of the metadata (or None)

        """
        return self.metadata[key] if key in self.metadata else None

    def match(self, message) -> bool:
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
            metadata=self.metadata,
        )

    def prepare(self):
        """
        Returns an aioxmpp.stanza.Message built from the Message and prepared to be sent.

        Returns:
          aioxmpp.stanza.Message: the message prepared to be sent

        """

        msg = aioxmpp.stanza.Message(
            to=self.to, from_=self.sender, type_=aioxmpp.MessageType.CHAT,
        )

        msg.body[None] = self.body

        # Send metadata using xep-0004: Data Forms (https://xmpp.org/extensions/xep-0004.html)
        if len(self.metadata):
            data = forms_xso.Data(type_=forms_xso.DataType.FORM)

            for name, value in self.metadata.items():
                data.fields.append(
                    forms_xso.Field(
                        var=name, type_=forms_xso.FieldType.TEXT_SINGLE, values=[value],
                    )
                )

            if self.thread:
                data.fields.append(
                    forms_xso.Field(
                        var="_thread_node",
                        type_=forms_xso.FieldType.TEXT_SINGLE,
                        values=[self.thread],
                    )
                )

            data.title = SPADE_X_METADATA
            msg.xep0004_data = [data]

        return msg

    def __str__(self):
        s = f'<message to="{self.to}" from="{self.sender}" thread="{self.thread}" metadata={self.metadata}>'
        if self.body:
            s += "\n" + self.body + "\n"
        s += "</message>"
        return s
