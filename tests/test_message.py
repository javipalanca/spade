#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `message` package."""

import copy
from unittest.mock import MagicMock

import slixmpp.stanza
from slixmpp.plugins.xep_0004 import Form
from slixmpp import JID
from slixmpp import Message as slixmppMessage
import pytest

from spade.message import Message, SPADE_X_METADATA


def test_prepare(message):
    mock_client = MagicMock()
    mock_client.Message.return_value = slixmpp.stanza.Message()
    aiomsg = message.prepare(mock_client)
    assert aiomsg["to"] == JID("to@localhost")
    assert aiomsg["from"] == JID("sender@localhost")
    assert aiomsg["body"] == "message body"

    for form in [pl for pl in aiomsg.xml.findall("{jabber:x:data}x")]:
        if form.find("{jabber:x:data}title").text == SPADE_X_METADATA:
            for field in form.findall("{jabber:x:data}field"):
                if field.attrib["var"] == "_thread_node":
                    assert field.find("{jabber:x:data}value").text == "thread-id"
                else:
                    assert (
                        message.get_metadata(field.attrib["var"])
                        == field.find("{jabber:x:data}value").text
                    )


def test_message_to_string(message):
    assert message.__str__() == (
        '<message to="to@localhost" from="sender@localhost" thread="thread-id" metadata={'
        "'metadata1': 'value1', 'metadata2': 'value2'}>\nmessage body\n</message>"
    )


def test_make_reply(message):
    reply = message.make_reply()
    assert reply.to == JID("sender@localhost")
    assert reply.sender == JID("to@localhost")
    assert reply.body == "message body"
    assert reply.thread == "thread-id"
    assert reply.get_metadata("metadata1") == "value1"
    assert reply.get_metadata("metadata2") == "value2"


def test_message_from_node_attribute_error():
    with pytest.raises(AttributeError):
        Message.from_node(Message())


def test_body_with_languages():
    msg = slixmppMessage()
    msg.chat()
    msg["body"] = {"en": "Hello World", "es": "Hola Mundo"}

    new_msg = Message.from_node(msg)
    assert new_msg.body == "Hello World"

    msg = slixmppMessage()
    msg.chat()


def test_message_from_node():
    slimsg = slixmppMessage()
    slimsg.chat()

    data = Form()
    data["type"] = "form"

    data.add_field(var="performative", ftype="text-single", value="request")

    data.add_field(var="_thread_node", ftype="text-single", value="thread-id")

    data["title"] = SPADE_X_METADATA
    slimsg.append(data)

    msg = Message.from_node(slimsg)

    assert msg.thread == "thread-id"
    assert msg.get_metadata("performative") == "request"
    assert msg.metadata == {"performative": "request"}


def test_thread_empty():
    msg = Message(thread=None)

    assert msg.thread is None
    assert msg.metadata == {}

    mock_client = MagicMock()
    mock_client.Message.return_value = slixmpp.stanza.Message()
    slimsg = msg.prepare(mock_client)
    for data in [pl for pl in slimsg.get_payload() if pl.tag == "{jabber:x:data}x"]:
        if data.findall("{jabber:x:data}title").text == SPADE_X_METADATA:
            for field in data.findall("{jabber:x:data}field"):
                assert field.attrib["var"] != "_thread_node"


def test_equal(message):
    assert message == copy.copy(message)


def test_not_equal(message, message2):
    assert message != message2


def test_id(message):
    assert isinstance(message.id, int)


def test_metadata_is_string():
    Message(metadata={"key": "value"})


def test_metadata_is_not_string():
    with pytest.raises(TypeError):
        Message(metadata={"key": 1000})


def test_metadata_set_string():
    msg = Message()
    msg.set_metadata("key", "value")


def test_metadata_set_not_string():
    msg = Message()
    with pytest.raises(TypeError):
        msg.set_metadata(1000, "value")


def test_body_is_string():
    Message(body="body")


def test_body_is_none():
    Message(body=None)


def test_body_is_not_string():
    with pytest.raises(TypeError):
        Message(body={})


def test_body_set_string():
    msg = Message()
    msg.body = "body"


def test_body_set_not_string():
    msg = Message()
    with pytest.raises(TypeError):
        msg.body = 1000


def test_body_set_none():
    msg = Message()
    msg.body = None


def test_to_is_string():
    Message(to="agent@fakeserver")


def test_to_is_not_string():
    with pytest.raises(TypeError):
        Message(to={})


def test_to_set_string():
    msg = Message()
    msg.to = "agent@fakeserver"


def test_to_set_jid():
    msg = Message()
    msg.to = JID("agent@fakeserver")


def test_to_set_not_string():
    msg = Message()
    with pytest.raises(TypeError):
        msg.to = 1000


def test_to_set_none():
    msg = Message()
    msg.to = None


def test_sender_is_string():
    Message(sender="agent@fakeserver")


def test_sender_is_jid():
    Message(sender=JID("agent@fakeserver"))


def test_sender_is_not_string():
    with pytest.raises(TypeError):
        Message(sender={})


def test_sender_set_string():
    msg = Message()
    msg.sender = "agent@fakeserver"


def test_sender_set_not_string():
    msg = Message()
    with pytest.raises(TypeError):
        msg.sender = 1000


def test_sender_set_none():
    msg = Message()
    msg.sender = None


def test_thread_is_string():
    Message(thread="thread_id_001")


def test_thread_is_not_string():
    with pytest.raises(TypeError):
        Message(thread=1000)


def test_thread_set_string():
    msg = Message()
    msg.thread = "thread_id_001"


def test_thread_set_not_string():
    msg = Message()
    with pytest.raises(TypeError):
        msg.thread = 1000


def test_thread_set_none():
    msg = Message()
    msg.thread = None


def test_sender_empty_true():
    msg = Message()
    assert msg.empty_sender()
