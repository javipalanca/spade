"""
Unit tests for FIPA message utilities
"""

import json
import pytest
from unittest.mock import MagicMock
from spade.fipa_message import (
    FIPAMessageBuilder,
    FIPAMessageParser,
    InvalidPerformativeError,
    PerformativeNotSetError,
)


def test_fipa_message_builder_initialization():
    """Test FIPA message builder initialization"""
    builder = FIPAMessageBuilder("sender@localhost", "receiver@localhost")

    assert builder.metadata["performative"] is None
    assert "conversation-id" in builder.metadata
    assert "reply-with" in builder.metadata
    assert builder.metadata["encoding"] == "utf-8"


def test_fipa_message_builder_set_performative_valid():
    """Test setting a valid performative"""
    builder = FIPAMessageBuilder("sender@localhost", "receiver@localhost")

    result = builder.set_performative("inform")

    assert result is builder  # Should return self for chaining
    assert builder.metadata["performative"] == "inform"


def test_fipa_message_builder_set_performative_invalid():
    """Test setting an invalid performative"""
    builder = FIPAMessageBuilder("sender@localhost", "receiver@localhost")

    with pytest.raises(InvalidPerformativeError):
        builder.set_performative("invalid_performative")


def test_fipa_message_builder_set_body_json():
    """Test setting body as JSON"""
    builder = FIPAMessageBuilder("sender@localhost", "receiver@localhost")
    content = {"key": "value", "number": 42}

    result = builder.set_body(content, as_json=True)

    assert result is builder
    assert json.loads(builder.message.body) == content
    assert builder.metadata["content-type"] == "application/json"


def test_fipa_message_builder_set_body_string():
    """Test setting body as string"""
    builder = FIPAMessageBuilder("sender@localhost", "receiver@localhost")
    content = "Plain text"

    result = builder.set_body(content, as_json=False)

    assert result is builder
    assert builder.message.body == content
    assert builder.metadata["content-type"] == "text/plain"


def test_fipa_message_builder_build_without_performative():
    """Test building message without setting performative"""
    builder = FIPAMessageBuilder("sender@localhost", "receiver@localhost")

    with pytest.raises(PerformativeNotSetError):
        builder.build()


def test_fipa_message_builder_build_success():
    """Test successful message build"""
    builder = FIPAMessageBuilder("sender@localhost", "receiver@localhost")
    content = {"data": "test"}

    builder.set_performative("inform").set_body(content, as_json=True)
    message = builder.build()

    assert message is not None
    assert message.sender == "sender@localhost"
    assert message.to == "receiver@localhost"
    assert message.metadata["performative"] == "inform"
    assert json.loads(message.body) == content


def test_create_inform_message():
    """Test creation of inform message"""
    message = FIPAMessageBuilder.create_inform_message(
        sender="sender@localhost",
        receiver="receiver@localhost",
        content={"status": "ok"},
        ontology="test-ontology",
    )

    assert message.metadata["performative"] == "inform"
    assert message.metadata["ontology"] == "test-ontology"
    assert message.metadata["protocol"] == "fipa-subscribe"
    assert json.loads(message.body)["status"] == "ok"


def test_create_request_message():
    """Test creation of request message"""
    message = FIPAMessageBuilder.create_request_message(
        sender="sender@localhost",
        receiver="receiver@localhost",
        action="test-action",
        parameters={"param1": "value1"},
    )

    assert message.metadata["performative"] == "request"
    assert message.metadata["ontology"] == "action-request"
    assert message.metadata["protocol"] == "fipa-request"

    content = json.loads(message.body)
    assert content["action"] == "test-action"
    assert content["parameters"]["param1"] == "value1"


def test_create_response_message():
    """Test creation of response message"""
    # Create an original message to respond to
    original_message = MagicMock()
    original_message.sender = "original_sender@localhost"
    original_message.to = "original_receiver@localhost"
    original_message.metadata = {
        "conversation-id": "test_conv_123",
        "reply-with": "original_reply_456",
        "ontology": "test-ontology",
        "protocol": "fipa-test",
    }

    response = FIPAMessageBuilder.create_response_message(
        original_msg=original_message,
        content={"result": "success"},
        performative="inform",
    )

    assert response.metadata["performative"] == "inform"
    assert response.sender == "original_receiver@localhost"  # Swap sender/receiver
    assert response.to == "original_sender@localhost"
    assert response.metadata["conversation-id"] == "test_conv_123"
    assert response.metadata["in-reply-to"] == "original_reply_456"
    assert json.loads(response.body)["result"] == "success"


def test_fipa_message_parser_initialization():
    """Test FIPA message parser initialization"""
    mock_message = MagicMock()
    mock_message.metadata = {"performative": "inform", "conversation-id": "test_conv"}
    mock_message.body = '{"key": "value"}'

    parser = FIPAMessageParser(mock_message)

    assert parser.message is mock_message
    assert parser.metadata == mock_message.metadata


def test_fipa_message_parser_methods():
    """Test FIPA message parser methods"""
    mock_message = MagicMock()
    mock_message.metadata = {
        "performative": "request",
        "conversation-id": "test_conv_123",
        "ontology": "test-ontology",
        "language": "json",
        "protocol": "fipa-test",
        "reply-with": "test_reply_789",
    }
    mock_message.body = '{"data": "test"}'

    parser = FIPAMessageParser(mock_message)

    assert parser.get_performative() == "request"
    assert parser.get_conversation_id() == "test_conv_123"
    assert parser.get_ontology() == "test-ontology"
    assert parser.get_language() == "json"
    assert parser.get_protocol() == "fipa-test"
    assert parser.get_reply_with() == "test_reply_789"


def test_fipa_message_parser_parse_body_json():
    """Test parsing JSON body"""
    mock_message = MagicMock()
    mock_message.metadata = {"performative": "inform", "conversation-id": "test_conv"}
    mock_message.body = '{"key": "value", "number": 42}'

    parser = FIPAMessageParser(mock_message)

    parsed = parser.parse_body()
    assert isinstance(parsed, dict)
    assert parsed["key"] == "value"
    assert parsed["number"] == 42


def test_fipa_message_parser_parse_body_string():
    """Test parsing string body"""
    mock_message = MagicMock()
    mock_message.metadata = {"performative": "inform", "conversation-id": "test_conv"}
    mock_message.body = "Plain text"

    parser = FIPAMessageParser(mock_message)
    # Temporarily change language
    parser.metadata["language"] = "string"

    parsed = parser.parse_body()
    assert parsed == "Plain text"


def test_fipa_message_parser_is_valid_fipa_message():
    """Test basic FIPA message validation"""
    # Valid message
    valid_message = MagicMock()
    valid_message.metadata = {"performative": "inform", "conversation-id": "test_conv"}
    valid_message.body = '{"key": "value"}'

    valid_parser = FIPAMessageParser(valid_message)
    assert valid_parser.is_valid_fipa_message() is True

    # Message without performative
    invalid_message = MagicMock()
    invalid_message.metadata = {"conversation-id": "test_conv"}
    invalid_message.body = '{"key": "value"}'

    invalid_parser = FIPAMessageParser(invalid_message)
    assert invalid_parser.is_valid_fipa_message() is False

    # Message without conversation-id
    invalid_message2 = MagicMock()
    invalid_message2.metadata = {"performative": "inform"}
    invalid_message2.body = '{"key": "value"}'

    invalid_parser2 = FIPAMessageParser(invalid_message2)
    assert invalid_parser2.is_valid_fipa_message() is False


def test_fipa_message_parser_get_custom_metadata():
    """Test getting custom metadata"""
    mock_message = MagicMock()
    mock_message.metadata = {
        "performative": "inform",
        "conversation-id": "test_conv",
        "custom-field": "custom-value",
        "another-field": 123,
    }
    mock_message.body = '{"key": "value"}'

    parser = FIPAMessageParser(mock_message)

    assert parser.get_custom_metadata("custom-field") == "custom-value"
    assert parser.get_custom_metadata("another-field") == 123
    assert parser.get_custom_metadata("non-existent") is None
    assert parser.get_custom_metadata("non-existent", "default") == "default"
