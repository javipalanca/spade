import logging
from typing import Optional, Dict, Type

import slixmpp.stanza
from slixmpp.plugins.xep_0004 import Form

import spade.message

SPADE_X_METADATA = "spade:x:metadata"

logger = logging.getLogger("spade.Message")


class MessageBase(object):
    """ """

    def __init__(
        self,
        to: Optional[str] = None,
        sender: Optional[str] = None,
        body: Optional[str] = None,
        thread: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ):
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
    def from_node(cls, node: slixmpp.Message) -> Type["MessageBase"]:
        """
        Creates a new spade.message.Message from a slixmpp.stanza.Message

        Args:
          node (slixmpp.stanza.Message): a slixmpp Message

        Returns:
          spade.message.Message: a new spade Message

        """
        if not isinstance(node, slixmpp.stanza.Message):
            raise AttributeError("node must be a slixmpp.stanza.Message instance")
        msg = cls()
        msg._to = node["to"]
        msg._sender = node["from"]

        if isinstance(node["body"], dict):
            for body in node["body"].values():
                msg.body = body
                break
        else:
            msg.body = node["body"]

        for data in [pl for pl in node.get_payload() if pl.tag == "{jabber:x:data}x"]:
            if data.find("{jabber:x:data}title").text == SPADE_X_METADATA:
                for field in data.findall("{jabber:x:data}field"):
                    if field.attrib["var"] != "_thread_node":
                        msg.set_metadata(
                            field.attrib["var"], field.find("{jabber:x:data}value").text
                        )
                    else:
                        msg.thread = field.find("{jabber:x:data}value").text

        return msg

    @property
    def to(self) -> slixmpp.JID:
        """
        Gets the jid of the receiver.

        Returns:
          slixmpp.JID: jid of the receiver

        """
        return self._to

    @to.setter
    def to(self, jid: str) -> None:
        """
        Set jid of the receiver.

        Args:
          jid (str): the jid of the receiver.

        """
        if jid is not None and not isinstance(jid, str):
            raise TypeError("'to' MUST be a string")
        self._to = slixmpp.JID(jid) if jid is not None else None

    @property
    def sender(self) -> slixmpp.JID:
        """
        Get jid of the sender

        Returns:
          slixmpp.JID: jid of the sender

        """
        return self._sender

    @sender.setter
    def sender(self, jid: str) -> None:
        """
        Set jid of the sender

        Args:
          jid (str): jid of the sender

        """
        if jid is not None and not isinstance(jid, str):
            raise TypeError("'sender' MUST be a string")
        self._sender = slixmpp.JID(jid) if jid is not None else None

    @property
    def body(self) -> str:
        """
        Get body of the message
        Returns:
            str: the body of the message
        """
        return self._body

    @body.setter
    def body(self, body: str) -> None:
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
    def thread(self, value: str) -> None:
        """
        Set thread id of the message

        Args:
            value (str): the thread id

        """
        if value is not None and not isinstance(value, str):
            raise TypeError("'thread' MUST be a string")
        self._thread = value

    def set_metadata(self, key: str, value: str) -> None:
        """
        Add a new metadata to the message

        Args:
          key (str): name of the metadata
          value (str): value of the metadata

        """
        if not isinstance(key, str) or not isinstance(value, str):
            raise TypeError("'key' and 'value' of metadata MUST be strings")
        self.metadata[key] = value

    def get_metadata(self, key: str) -> str:
        """
        Get the value of a metadata. Returns None if metadata does not exist.

        Args:
          key (str): name of the metadata

        Returns:
          str: the value of the metadata (or None)

        """
        return self.metadata[key] if key in self.metadata else None

    def match(self, message: Type["MessageBase"]) -> bool:
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
    def id(self) -> int:
        """ """
        return id(self)

    def __eq__(self, other: Type["MessageBase"]):
        if type(other) is not spade.message.Message:
            return False
        return self.match(other)


class Message(MessageBase):
    """ """

    def make_reply(self) -> "Message":
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

    def prepare(self) -> slixmpp.stanza.Message:
        """
        Returns a slixmpp.stanza.Message built from the Message and prepared to be sent.

        Returns:
          slixmpp.stanza.Message: the message prepared to be sent

        """
        msg = slixmpp.stanza.Message()
        msg["to"] = self.to
        msg["from"] = self.sender
        msg["body"] = self.body
        msg.chat()

        # Send metadata using xep-0004: Data Forms (https://xmpp.org/extensions/xep-0004.html)
        if len(self.metadata):
            form = Form()
            form["type"] = "form"
            for name, value in self.metadata.items():
                form.add_field(var=name, ftype="text-single", value=value)

            if self.thread:
                form.add_field(
                    var="_thread_node", ftype="text-single", value=self.thread
                )

            form["title"] = SPADE_X_METADATA
            msg.append(form)

        return msg

    def __str__(self) -> str:
        s = f'<message to="{self.to}" from="{self.sender}" thread="{self.thread}" metadata={self.metadata}>'
        if self.body:
            s += "\n" + self.body + "\n"
        s += "</message>"
        return s
