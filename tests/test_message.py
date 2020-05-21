#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `message` package."""
import copy

import aioxmpp
import aioxmpp.forms.xso as forms_xso
import pytest

from spade.message import Message, SPADE_X_METADATA


def test_prepare(message):
    aiomsg = message.prepare()
    assert aiomsg.to == aioxmpp.JID.fromstr("to@localhost")
    assert aiomsg.from_ == aioxmpp.JID.fromstr("sender@localhost")
    assert aiomsg.body[None] == "message body"

    for data in aiomsg.xep0004_data:
        if data.title == SPADE_X_METADATA:
            for field in data.fields:
                if field.var == "_thread_node":
                    assert field.values[0] == "thread-id"
                else:
                    assert message.get_metadata(field.var) == field.values[0]


def test_make_reply(message):
    reply = message.make_reply()
    assert reply.to == aioxmpp.JID.fromstr("sender@localhost")
    assert reply.sender == aioxmpp.JID.fromstr("to@localhost")
    assert reply.body == "message body"
    assert reply.thread == "thread-id"
    assert reply.get_metadata("metadata1") == "value1"
    assert reply.get_metadata("metadata2") == "value2"


def test_message_from_node_attribute_error():
    with pytest.raises(AttributeError) as e:
        Message.from_node(Message())


def test_body_with_languages():
    msg = aioxmpp.Message(type_=aioxmpp.MessageType.CHAT)
    msg.body["en"] = "Hello World"
    msg.body["es"] = "Hola Mundo"

    new_msg = Message.from_node(msg)
    assert new_msg.body == "Hello World"


def test_message_from_node():
    aiomsg = aioxmpp.Message(type_=aioxmpp.MessageType.CHAT)
    data = forms_xso.Data(type_=forms_xso.DataType.FORM)

    data.fields.append(
        forms_xso.Field(
            var="performative",
            type_=forms_xso.FieldType.TEXT_SINGLE,
            values=["request"],
        )
    )

    data.fields.append(
        forms_xso.Field(
            var="_thread_node",
            type_=forms_xso.FieldType.TEXT_SINGLE,
            values=["thread-id"],
        )
    )
    data.title = SPADE_X_METADATA
    aiomsg.xep0004_data = [data]

    msg = Message.from_node(aiomsg)

    assert msg.thread == "thread-id"
    assert msg.get_metadata("performative") == "request"
    assert msg.metadata == {"performative": "request"}


def test_thread_empty():
    msg = Message(thread=None)

    assert msg.thread is None
    assert msg.metadata == {}

    aiomsg = msg.prepare()
    for data in aiomsg.xep0004_data:
        if data.title == SPADE_X_METADATA:
            for field in data.fields:
                assert field.var != "_thread_node"


def test_equal(message):
    assert message == copy.copy(message)


def test_not_equal(message, message2):
    assert message != message2


def test_id(message):
    assert type(message.id) == int


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
        Message(to=aioxmpp.JID.fromstr("agent@fakeserver"))


def test_to_set_string():
    msg = Message()
    msg.to = "agent@fakeserver"


def test_to_set_not_string():
    msg = Message()
    with pytest.raises(TypeError):
        msg.to = 1000


def test_to_set_none():
    msg = Message()
    msg.to = None


def test_sender_is_string():
    Message(sender="agent@fakeserver")


def test_sender_is_not_string():
    with pytest.raises(TypeError):
        Message(sender=aioxmpp.JID.fromstr("agent@fakeserver"))


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
