from typing import Optional

from slixmpp.plugins import BasePlugin
from slixmpp.types import JidStr
from slixmpp.xmlstream import StanzaBase
from slixmpp.xmlstream.handler import Callback
from slixmpp.xmlstream.matcher import StanzaPath

from . import stanza


class XEP_0461(BasePlugin):
    """XEP-0461: Message Replies"""

    name = "xep_0461"
    description = "XEP-0461: Message Replies"

    dependencies = {"xep_0030", "xep_0428"}
    stanza = stanza
    namespace = stanza.NS

    def plugin_init(self) -> None:
        stanza.register_plugins()
        self.xmpp.register_handler(
            Callback(
                "Message replied to",
                StanzaPath("message/reply"),
                self._handle_reply_to_message,
            )
        )

    def plugin_end(self):
        self.xmpp.plugin["xep_0030"].del_feature(feature=stanza.NS)

    def session_bind(self, jid):
        self.xmpp.plugin["xep_0030"].add_feature(feature=stanza.NS)

    def _handle_reply_to_message(self, msg: StanzaBase):
        self.xmpp.event("message_reply", msg)

    def make_reply(self, reply_to: JidStr, reply_id: str,
                   fallback: Optional[str] = None,
                   quoted_nick: Optional[str] = None, **msg_kwargs):
        """Create a replies message stanza

        :param reply_to: Full JID of the quoted author
        :param reply_id: ID of the message to reply to
        :param fallback: Body of the quoted message
        :param quoted_nick: nickname of the quoted participant
        :param msg_kwargs: Parameters are consistent with the make_message method,
            required parameters are ``mto`` and ``mbody``
        """

        msg = self.xmpp.make_message(**msg_kwargs)
        msg["reply"]["to"] = reply_to
        msg["reply"]["id"] = reply_id
        if fallback:
            msg["reply"].add_quoted_fallback(fallback, quoted_nick)
        return msg

    def send_reply(self, reply_to: JidStr, reply_id: str,
                   fallback: Optional[str] = None,
                   quoted_nick: Optional[str] = None, **msg_kwargs):
        """

        :param reply_to: Full JID of the quoted author
        :param reply_id: ID of the message to reply to
        :param fallback: Body of the quoted message
        :param quoted_nick: nickname of the quoted participant
        """
        msg = self.make_reply(reply_to, reply_id, fallback, quoted_nick, **msg_kwargs)
        msg.send()
