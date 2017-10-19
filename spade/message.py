import logging

import aioxmpp
import aioxmpp.forms.xso as forms_xso

SPADE_X_METADATA = "spade:x:metadata"

logger = logging.getLogger('spade.Message')


class Message(object):
    def __init__(self, to=None, sender=None):
        self._to, self._sender = None, None
        self.to = to
        self.sender = sender
        self.body = None
        self.thread = None

        self.metadata = {}

    @classmethod
    def from_node(cls, node):
        if not isinstance(node, aioxmpp.stanza.Message):
            raise AttributeError("node must be a aioxmpp.stanza.Message instance")
        msg = cls()
        msg._to = node.to
        msg._sender = node.from_
        msg.body = node.body[None]
        msg.thread = node.thread

        for data in node.xep0004_data:
            if data.title == SPADE_X_METADATA:
                for field in data.fields:
                    msg.set_metadata(field.var, field.values[0])

        return msg

    @property
    def to(self):
        return self._to

    @to.setter
    def to(self, jid):
        self._to = aioxmpp.JID.fromstr(jid)

    @property
    def sender(self):
        return self._sender

    @sender.setter
    def sender(self, jid):
        self._sender = aioxmpp.JID.fromstr(jid)

    def set_metadata(self, key, value):
        self.metadata[key] = value

    def get_metadata(self, key):
        return self.metadata[key] if key in self.metadata else None

    def prepare(self):

        msg = aioxmpp.stanza.Message(
            to=self.to,
            from_=self.sender,
            type_=aioxmpp.MessageType.CHAT,
        )

        msg.body[None] = self.body

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
