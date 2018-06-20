#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `template` package."""
import pytest

from spade.message import Message
from spade.template import Template


def test_match():
    template = Template()
    template.sender = "sender1@host"
    template.to = "recv1@host"
    template.body = "Hello World"
    template.thread = "thread-id"
    template.metadata = {"performative": "query"}

    message = Message()
    message.sender = "sender1@host"
    message.to = "recv1@host"
    message.body = "Hello World"
    message.thread = "thread-id"
    message.set_metadata("performative", "query")

    assert template.match(message)


def test_match_false_sender():
    template = Template()
    template.sender = "sender2@host"

    message = Message()

    assert not template.match(message)

    message.sender = "sender1@host"

    assert not template.match(message)


def test_match_false_to():
    template = Template()
    template.to = "recv1@host"

    message = Message()

    assert not template.match(message)

    message.to = "recv2@host"

    assert not template.match(message)


def test_match_false_body():
    template = Template()
    template.body = "Hello World"

    message = Message()

    assert not template.match(message)

    message.body = "Bye Bye Love"

    assert not template.match(message)


def test_match_false_thread():
    template = Template()
    template.thread = "thread-id"

    message = Message()

    assert not template.match(message)

    message.thread = "thread-id-false"

    assert not template.match(message)


def test_match_false_metadata():
    template = Template()
    template.metadata = {"performative": "query"}

    message = Message()

    assert not template.match(message)

    message.set_metadata("performative", "inform")

    assert not template.match(message)


def test_match_false_metadata_with_different_key():
    template = Template()
    template.metadata = {"performative": "query"}

    message = Message()
    message.set_metadata("language", "query")

    assert not template.match(message)


def test_match_and():
    t1 = Template()
    t1.sender = "sender1@host"
    t2 = Template()
    t2.to = "recv1@host"
    t2.metadata = {"performative": "query"}

    m1 = Message()
    m1.sender = "sender1@host"

    assert not (t1 & t2).match(m1)

    m2 = Message()
    m2.to = "recv1@host"
    m2.metadata = {"performative": "query"}

    assert not (t1 & t2).match(m2)

    m3 = Message()
    m3.sender = "sender1@host"
    m3.to = "recv1@host"
    m3.metadata = {"performative": "query"}

    assert (t1 & t2).match(m3)


def test_match_iand():
    t1 = Template()
    t1.sender = "sender1@host"
    t2 = Template()
    t2.to = "recv1@host"
    t2.metadata = {"performative": "query"}

    m1 = Message()
    m1.sender = "sender1@host"

    t1 &= t2
    assert not t1.match(m1)

    m2 = Message()
    m2.to = "recv1@host"
    m2.metadata = {"performative": "query"}

    assert not t1.match(m2)

    m3 = Message()
    m3.sender = "sender1@host"
    m3.to = "recv1@host"
    m3.metadata = {"performative": "query"}

    assert t1.match(m3)


def test_match_or():
    t1 = Template()
    t1.sender = "sender1@host"
    t2 = Template()
    t2.to = "recv1@host"
    t2.metadata = {"performative": "query"}

    m1 = Message()
    m1.sender = "sender1@host"

    assert (t1 | t2).match(m1)

    m2 = Message()
    m2.to = "recv1@host"
    m2.metadata = {"performative": "query"}

    assert (t1 | t2).match(m2)

    m3 = Message()
    m3.sender = "sender2@host"
    m3.to = "recv1@host"
    m3.metadata = {"performative": "inform"}

    assert not (t1 | t2).match(m3)


def test_match_ior():
    t1 = Template()
    t1.sender = "sender1@host"
    t2 = Template()
    t2.to = "recv1@host"
    t2.metadata = {"performative": "query"}

    m1 = Message()
    m1.sender = "sender1@host"

    t1 |= t2

    assert t1.match(m1)

    m2 = Message()
    m2.to = "recv1@host"
    m2.metadata = {"performative": "query"}

    assert t1.match(m2)

    m3 = Message()
    m3.sender = "sender2@host"
    m3.to = "recv1@host"
    m3.metadata = {"performative": "inform"}

    assert not t1.match(m3)


def test_match_xor():
    t1 = Template()
    t1.sender = "sender1@host"
    t2 = Template()
    t2.to = "recv1@host"
    t2.metadata = {"performative": "query"}

    m1 = Message()
    m1.sender = "sender1@host"

    assert (t1 ^ t2).match(m1)

    m2 = Message()
    m2.to = "recv1@host"
    m2.metadata = {"performative": "query"}

    assert (t1 ^ t2).match(m2)

    m3 = Message()
    m3.sender = "sender2@host"
    m3.to = "recv1@host"
    m3.metadata = {"performative": "inform"}

    assert not (t1 ^ t2).match(m3)

    t1 = Template()
    t1.sender = "sender1@host"
    t2 = Template()
    t2.sender = "sender1@host"
    m4 = Message()
    m4.sender = "sender1@host"

    assert not (t1 ^ t2).match(m4)


def test_match_ixor():
    t1 = Template()
    t1.sender = "sender1@host"
    t2 = Template()
    t2.to = "recv1@host"
    t2.metadata = {"performative": "query"}

    m1 = Message()
    m1.sender = "sender1@host"

    t1 ^= t2

    assert t1.match(m1)

    m2 = Message()
    m2.to = "recv1@host"
    m2.metadata = {"performative": "query"}

    assert t1.match(m2)

    m3 = Message()
    m3.sender = "sender2@host"
    m3.to = "recv1@host"
    m3.metadata = {"performative": "inform"}

    assert not t1.match(m3)

    t1 = Template()
    t1.sender = "sender1@host"
    t2 = Template()
    t2.sender = "sender1@host"
    m4 = Message()
    m4.sender = "sender1@host"

    t1 ^= t2

    assert not t1.match(m4)


def test_match_not():
    t1 = Template()
    t1.sender = "sender1@host"
    t1.to = "recv1@host"
    t1.metadata = {"performative": "query"}

    m1 = Message()
    m1.sender = "sender1@host"

    assert (~t1).match(m1)

    m2 = Message()
    m2.sender = "sender1@host"
    m2.to = "recv1@host"

    assert (~t1).match(m2)

    m3 = Message()
    m3.sender = "sender1@host"
    m3.to = "recv1@host"
    m3.metadata = {"performative": "query"}

    assert not (~t1).match(m3)


def test_and_value_error():
    with pytest.raises(TypeError):
        assert Template() & None

    with pytest.raises(TypeError):
        assert Template() & 3

    with pytest.raises(TypeError):
        assert Template() & "string"

    with pytest.raises(TypeError):
        assert Template() & object()


def test_or_value_error():
    with pytest.raises(TypeError):
        assert Template() | None

    with pytest.raises(TypeError):
        assert Template() | 3

    with pytest.raises(TypeError):
        assert Template() | "string"

    with pytest.raises(TypeError):
        assert Template() | object()


def test_xor_value_error():
    with pytest.raises(TypeError):
        assert Template() ^ None

    with pytest.raises(TypeError):
        assert Template() ^ 3

    with pytest.raises(TypeError):
        assert Template() ^ "string"

    with pytest.raises(TypeError):
        assert Template() ^ object()
