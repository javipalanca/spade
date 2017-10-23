#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `message` package."""
import aioxmpp
from spade.message import Message, SPADE_X_METADATA


def test_prepare():
    msg = Message(
        to="to@localhost",
        sender="sender@localhost",
        body="message body",
        thread="thread-id",
        metadata={
            "metadata1": "value1",
            "metadata2": "value2"
        }
    )

    aiomsg = msg.prepare()
    assert aiomsg.to == aioxmpp.JID.fromstr("to@localhost")
    assert aiomsg.from_ == aioxmpp.JID.fromstr("sender@localhost")
    assert aiomsg.body[None] == "message body"
    assert aiomsg.thread == "thread-id"

    for data in aiomsg.xep0004_data:
        if data.title == SPADE_X_METADATA:
            for field in data.fields:
                assert msg.get_metadata(field.var) == field.values[0]


def test_make_reply():
    msg = Message(
        to="to@localhost",
        sender="sender@localhost",
        body="message body",
        thread="thread-id",
        metadata={
            "metadata1": "value1",
            "metadata2": "value2"
        }
    )

    reply = msg.make_reply()
    assert reply.to == aioxmpp.JID.fromstr("sender@localhost")
    assert reply.sender == aioxmpp.JID.fromstr("to@localhost")
    assert reply.body == "message body"
    assert reply.thread == "thread-id"
    assert reply.get_metadata("metadata1") == "value1"
    assert reply.get_metadata("metadata2") == "value2"
