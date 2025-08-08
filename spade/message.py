import logging
from typing import Optional, Dict, Union, Type

from slixmpp import ClientXMPP
from slixmpp.plugins.xep_0004.stanza.form import Form
from slixmpp import JID
from slixmpp.stanza import Message as SlixmppMessage

SPADE_X_METADATA = "spade:x:metadata"

logger = logging.getLogger("spade.Message")


class MessageBase(object):
    """Base class for message handling in SPADE."""

    def __init__(
        self,
        to: Union[str, JID, None] = None,
        sender: Union[str, JID, None] = None,
        body: Optional[str] = None,
        thread: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ):
        self.sent = False
        self.to = to  # type: ignore
        self.sender = sender  # type: ignore
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
    def from_node(cls, node: SlixmppMessage) -> Type["MessageBase"]:
        """
        Creates a new spade.message.Message from a slixmpp.stanza.Message

        Args:
          node (slixmpp.stanza.Message): a slixmpp Message

        Returns:
          spade.message.Message: a new spade Message

        """
        if not isinstance(node, SlixmppMessage):
            raise AttributeError("node must be a slixmpp.stanza.Message instance")
        msg = cls()
        msg.to = node["to"]
        msg.sender = node["from"]

        if isinstance(node["body"], dict):
            for body in node["body"].values():
                msg.body = body
                break
        else:
            msg.body = node["body"]

        for data in [pl for pl in node.get_payload() if pl.tag == "{jabber:x:data}x"]:
            title_elem = data.find("{jabber:x:data}title")
            if title_elem is not None and title_elem.text == SPADE_X_METADATA:
                for field in data.findall("{jabber:x:data}field"):
                    value_elem = field.find("{jabber:x:data}value")
                    value_text = value_elem.text if value_elem is not None else None
                    if field.attrib["var"] != "_thread_node":
                        if value_text is not None:
                            msg.set_metadata(field.attrib["var"], value_text)
                    else:
                        if value_text is not None:
                            msg.thread = value_text

        return msg

    @property
    def to(self) -> JID:
        """
        Gets the jid of the receiver.

        Returns:
          slixmpp.JID: jid of the receiver

        """
        return self._to

    @to.setter
    def to(self, jid: Union[str, JID, None]) -> None:
        """
        Set jid of the receiver.

        Args:
          jid (str): the jid of the receiver.

        """
        if jid is None:
            self._to = JID()
        elif isinstance(jid, str):
            self._to = JID(jid)
        elif isinstance(jid, JID):
            self._to = jid
        else:
            raise TypeError("'to' MUST be a valid JID, str or None")

    @property
    def sender(self) -> JID:
        """
        Get jid of the sender

        Returns:
          slixmpp.JID: jid of the sender

        """
        return self._sender

    @sender.setter
    def sender(self, jid: Union[str, JID, None]) -> None:
        """
        Set jid of the sender

        Args:
          jid (str): jid of the sender

        """
        if jid is None:
            self._sender = JID()
        elif isinstance(jid, str):
            self._sender = JID(jid)
        elif isinstance(jid, JID):
            self._sender = jid
        else:
            raise TypeError("'sender' MUST be a valid JID, str or None")

    @property
    def body(self) -> Union[str, None]:
        """
        Get body of the message
        Returns:
            str: the body of the message
        """
        return self._body

    @body.setter
    def body(self, body: Union[str, None]) -> None:
        """
        Set body of the message
        Args:
            body (str): The body of the message
        """
        if body is None:
            self._body = ""
        elif not isinstance(body, str):
            raise TypeError("'body' MUST be a string")
        self._body = body  # type: ignore

    @property
    def thread(self) -> Union[str, None]:
        """
        Get Thread of the message

        Returns:
            str: thread id
        """
        return self._thread

    @thread.setter
    def thread(self, value: Union[str, None]) -> None:
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

    def get_metadata(self, key: str) -> Union[str, None]:
        """
        Get the value of a metadata. Returns None if metadata does not exist.

        Args:
          key (str): name of the metadata

        Returns:
          str: the value of the metadata (or None)

        """
        return self.metadata[key] if key in self.metadata else None

    @staticmethod
    def empty_jid(jid: JID):
        return not jid.bare and not jid.domain and not jid.resource

    def empty_to(self):
        return self.empty_jid(self.to)

    def empty_sender(self):
        return self.empty_jid(self.sender)

    def match(self, message: "MessageBase") -> bool:
        """
        Returns wether a message matches with this message or not.
        The message can be a Message object or a Template object.

        Args:
          message (spade.message.Message): the message to match to

        Returns:
          bool: wether the message matches or not

        """
        if not self.empty_to() and not message.to.__eq__(self.to):
            return False

        if not self.empty_sender() and not message.sender.__eq__(self.sender):
            return False

        if self.body and message.body != self.body:
            return False

        if self.thread and (message.thread is None or message.thread != self.thread):
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

    def __eq__(self, other: object):
        if not isinstance(other, Message):
            return False
        return self.match(other) and other.match(self)


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

    def prepare(self, client: ClientXMPP) -> SlixmppMessage:
        """
        Returns a slixmpp.stanza.Message built from the Message and prepared to be sent.

        Args:
            client (ClientXMPP): An XMPP client, whose stream will be used to send the message

        Returns:
            slixmpp.stanza.Message: the message prepared to be sent

        """
        msg = client.Message()
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
