#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `message` package."""
import copy

import aioxmpp
import pytest

from spade.message import Message, SPADE_X_METADATA


@pytest.fixture
def message():
    return Message(
        to="to@localhost",
        sender="sender@localhost",
        body="message body",
        thread="thread-id",
        metadata={
            "metadata1": "value1",
            "metadata2": "value2"
        }
    )


@pytest.fixture
def message2():
    return Message(
        to="to2@localhost",
        sender="sender2@localhost",
        body="message body",
        thread="thread-id",
    )


def test_prepare(message):
    aiomsg = message.prepare()
    assert aiomsg.to == aioxmpp.JID.fromstr("to@localhost")
    assert aiomsg.from_ == aioxmpp.JID.fromstr("sender@localhost")
    assert aiomsg.body[None] == "message body"
    assert aiomsg.thread == "thread-id"

    for data in aiomsg.xep0004_data:
        if data.title == SPADE_X_METADATA:
            for field in data.fields:
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


def test_equal(message):
    assert message == copy.copy(message)


def test_not_equal(message, message2):
    assert message != message2
