# fipa_message.py
"""
Module for creating and handling FIPA-ACL messages compatible with SPADE.

Based on the FIPA ACL Message Structure Specification:
http://www.fipa.org/specs/fipa00061/SC00061G.html

This module provides tools for building, validating, and parsing
FIPA-ACL messages that comply with the Foundation for Intelligent Physical Agents (FIPA) standards.
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Any, ClassVar, Union, Optional
import logging

from spade.message import Message

logger = logging.getLogger(__name__)


class InvalidPerformativeError(ValueError):
    """Exception raised when an invalid performative is provided.

    This exception is raised when attempting to use a performative
    that is not defined in the FIPA-ACL specification.
    """

    def __init__(self, performative, valid_performatives):
        """Initialize the exception with the invalid performative and valid ones.

        Args:
            performative (str): The performative that caused the error.
            valid_performatives: The valid performatives (e.g., a list or formatted string).
        """
        self.performative = performative
        self.valid_performatives = valid_performatives
        super().__init__(
            f"Invalid performative '{performative}'. " f"Valid: {valid_performatives}"
        )


class PerformativeNotSetError(ValueError):
    """Exception raised when performative is not set before building the message.

    This exception is raised when attempting to build a FIPA-ACL message
    without having previously set the corresponding performative.
    """

    def __init__(self):
        """Initialize the exception with a descriptive message."""
        super().__init__("Performative not set. Use set_performative() before build().")


class FIPAMessageBuilder:
    """
    Builder for FIPA-ACL messages for agent communication.

    This class provides a fluent interface for creating messages
    that follow the FIPA Agent Communication Language standard.

    Attributes:
        message (Message): The SPADE Message object being built
        metadata (Dict): Dictionary with FIPA-ACL metadata
    """

    # Standard FIPA-ACL performatives (FIPA SC00037J)
    PERFORMATIVES: ClassVar[dict] = {
        "accept-proposal": "Accept a proposal",
        "agree": "Agree to perform an action",
        "cancel": "Cancel a previously agreed action",
        "cfp": "Call for proposal (request proposals)",
        "confirm": "Confirm that something is true",
        "disconfirm": "Inform that something is false",
        "failure": "Report failure to execute action",
        "inform": "Inform that something is true",
        "inform-if": "Inform whether a proposition is true",
        "inform-ref": "Inform the value of a reference",
        "not-understood": "Indicate that the message was not understood",
        "propagate": "Ask an agent to send a message to others",
        "propose": "Make a proposal",
        "proxy": "Ask an agent to act as proxy",
        "query-if": "Ask whether a proposition is true",
        "query-ref": "Ask the value of a reference",
        "refuse": "Refuse to perform an action",
        "reject-proposal": "Reject a proposal",
        "request": "Request that an action be performed",
        "request-when": "Request that an action be performed when a condition holds",
        "request-whenever": "Request that an action be performed whenever a condition holds",
        "subscribe": "Subscribe to information",
    }

    # Supported content languages
    LANGUAGES: ClassVar[dict] = {
        "fipa-sl": "FIPA Semantic Language (standard)",
        "fipa-sl0": "FIPA SL level 0",
        "fipa-sl1": "FIPA SL level 1",
        "fipa-sl2": "FIPA SL level 2",
        "json": "JavaScript Object Notation",
        "xml": "Extensible Markup Language",
        "string": "Plain text string",
    }

    # FIPA interaction protocols
    PROTOCOLS: ClassVar[dict] = {
        "fipa-request": "Request protocol",
        "fipa-query": "Query protocol",
        "fipa-subscribe": "Subscribe protocol",
        "fipa-propose": "Propose protocol",
        "fipa-contract-net": "Contract net protocol",
        "fipa-brokering": "Brokering protocol",
        "fipa-recruiting": "Recruiting protocol",
    }

    def __init__(self, sender: str, receiver: str):
        """
        Initialize a new FIPA-ACL message builder.

        Args:
            sender (str): JID of the sending agent (e.g., "agent1@localhost")
            receiver (str): JID of the receiving agent (e.g., "agent2@localhost")

        Example:
            >>> builder = FIPAMessageBuilder(
            ...     sender="monitor@localhost",
            ...     receiver="validator@localhost"
            ... )
        """
        self.message = Message(sender=sender, to=receiver)
        self.metadata = {}

        # Default FIPA-ACL values
        self._set_default_metadata()

    def _set_default_metadata(self) -> None:
        """Configure default values for FIPA-ACL metadata.

        This method sets the default values for FIPA-ACL metadata
        that should be present in all messages.
        """
        # Generate unique conversation ID by default
        self.metadata["conversation-id"] = f"conv-{uuid.uuid4().hex[:8]}"

        # Generate unique message ID
        self.metadata["reply-with"] = f"msg-{uuid.uuid4().hex[:8]}"

        # Standard default values
        self.metadata["encoding"] = "utf-8"  # Default encoding
        self.metadata["language"] = (
            "json"  # Default language (not FIPA standard but useful)
        )
        self.metadata["ontology"] = "fipa-agent-communication"
        self.metadata["performative"] = (
            None  # Initialize performative as None for testing
        )

        # Creation timestamp
        self.metadata["creation-timestamp"] = datetime.now().isoformat()

    def set_performative(self, performative: str) -> "FIPAMessageBuilder":
        """
        Set the speech act (performative) of the message.

        Args:
            performative (str): Type of speech act. Must be one of the
                               valid FIPA-ACL performatives.

        Returns:
            FIPAMessageBuilder: Self for method chaining.

        Raises:
            ValueError: If the performative is not valid.

        Example:
            >>> builder.set_performative("inform")
        """
        if performative not in self.PERFORMATIVES:
            valid_performatives = ", ".join(sorted(self.PERFORMATIVES.keys()))
            raise InvalidPerformativeError(performative, valid_performatives)

        self.metadata["performative"] = performative
        return self

    def set_body(
        self, content: Union[dict, str, Any], as_json: bool = True
    ) -> "FIPAMessageBuilder":
        """
        Set the message body content.

        Args:
            content: Message content. Can be dict, str, or other type.
            as_json (bool): If True, serializes non-string content to JSON or
                            treats string content as already-serialized JSON.
                            If False, uses content as string.

        Returns:
            FIPAMessageBuilder: Self for method chaining.

        Example:
            >>> builder.set_body({"data": "value"}, as_json=True)
            >>> builder.set_body('{"data": "value"}', as_json=True)
            >>> builder.set_body("plain text", as_json=False)
        """
        if as_json:
            if isinstance(content, str):
                 # Treat string content as already-serialized JSON
                 self.message.body = content
            else:
                self.message.body = json.dumps(content, ensure_ascii=False)
            self.metadata["content-type"] = "application/json"
            self.metadata["language"] = "json"
        else:
            self.message.body = str(content)
            self.metadata["content-type"] = "text/plain"
            self.metadata["language"] = "string"

        return self

    def set_language(self, language: str) -> "FIPAMessageBuilder":
        """
        Set the content language.

        Args:
            language (str): Content language. Recommended to use
                           "json", "xml", or "fipa-sl".

        Returns:
            FIPAMessageBuilder: Self for method chaining.

        Example:
            >>> builder.set_language("json")
        """
        if language not in self.LANGUAGES:
            logger.warning(
                "Language '%s' is not in the list of known languages",
                language
            )

        self.metadata["language"] = language
        return self

    def set_protocol(self, protocol: str) -> "FIPAMessageBuilder":
        """
        Set the interaction protocol.

        Args:
            protocol (str): FIPA protocol. E.g., "fipa-request", "fipa-subscribe".

        Returns:
            FIPAMessageBuilder: Self for method chaining.

        Example:
            >>> builder.set_protocol("fipa-request")
        """
        if protocol not in self.PROTOCOLS:
            logger.warning(
            "Protocol '%s' is not in the list of known protocols",
            protocol
            )

        self.metadata["protocol"] = protocol
        return self

    def set_ontology(self, ontology: str) -> "FIPAMessageBuilder":
        """
        Set the message ontology.

        Args:
            ontology (str): Ontology that defines the terms/concepts used.

        Returns:
            FIPAMessageBuilder: Self for method chaining.

        Example:
            >>> builder.set_ontology("database-update")
        """
        self.metadata["ontology"] = ontology
        return self

    def set_conversation_id(self, conversation_id: str) -> "FIPAMessageBuilder":
        """
        Set a specific conversation ID.

        Args:
            conversation_id (str): Unique ID for the conversation.

        Returns:
            FIPAMessageBuilder: Self for method chaining.

        Note:
            If not set, one is automatically generated with UUID.

        Example:
            >>> builder.set_conversation_id("db-update-123")
        """
        self.metadata["conversation-id"] = conversation_id
        return self

    def set_in_reply_to(self, reply_to: str) -> "FIPAMessageBuilder":
        """
        Set which message is being replied to.

        Args:
            reply_to (str): Value of the 'reply-with' field from the original message.

        Returns:
            FIPAMessageBuilder: Self for method chaining.

        Example:
            >>> builder.set_in_reply_to("msg-abc123")
        """
        self.metadata["in-reply-to"] = reply_to
        return self

    def set_reply_by(self, minutes: int = 5) -> "FIPAMessageBuilder":
        """
        Set deadline for response.

        Args:
            minutes (int): Minutes until response wait expires.

        Returns:
            FIPAMessageBuilder: Self for method chaining.

        Example:
            >>> builder.set_reply_by(10)  # 10 minutes to respond
        """
        expiry_time = datetime.now() + timedelta(minutes=minutes)
        self.metadata["reply-by"] = expiry_time.isoformat()
        return self

    def set_custom_metadata(self, key: str, value: Any) -> "FIPAMessageBuilder":
        """
        Add custom metadata to the message.

        Args:
            key (str): Metadata key.
            value: Metadata value. It will be converted to a string for storage.

        Returns:
            FIPAMessageBuilder: Self for method chaining.

        Example:
            >>> builder.set_custom_metadata("priority", "high")
        """
        self.metadata[str(key)] = str(value)
        return self

    def build(self) -> Message:
        """
        Build and return the SPADE Message object.

        Returns:
            Message: Message object ready to send.

        Raises:
            ValueError: If performative has not been set.

        Example:
            >>> msg = builder.build()
            >>> await agent.send(msg)
        """
        # Verify that performative has been set
        if "performative" not in self.metadata or self.metadata["performative"] is None:
            raise PerformativeNotSetError()

        # Apply metadata to message
        self.message.metadata = self.metadata

        return self.message

    @classmethod
    def create_inform_message(
        cls, sender: str, receiver: str, content: dict, ontology: str = "general"
    ) -> Message:
        """
        Convenience method to create 'inform' messages.

        Args:
            sender (str): Sender JID.
            receiver (str): Receiver JID.
            content (Dict): Message content.
            ontology (str): Message ontology.

        Returns:
            Message: FIPA-ACL 'inform' message.

        Example:
            >>> msg = FIPAMessageBuilder.create_inform_message(
            ...     sender="agent1@localhost",
            ...     receiver="agent2@localhost",
            ...     content={"data": "value"},
            ...     ontology="database"
            ... )
        """
        return (
            cls(sender, receiver)
            .set_performative("inform")
            .set_body(content)
            .set_ontology(ontology)
            .set_protocol("fipa-subscribe")
            .build()
        )

    @classmethod
    def create_request_message(
        cls, sender: str, receiver: str, action: str, parameters: Optional[dict] = None
    ) -> Message:
        """
        Convenience method to create 'request' messages.

        Args:
            sender (str): Sender JID.
            receiver (str): Receiver JID.
            action (str): Action to request.
            parameters (Dict): Action parameters.

        Returns:
            Message: FIPA-ACL 'request' message.

        Example:
            >>> msg = FIPAMessageBuilder.create_request_message(
            ...     sender="agent1@localhost",
            ...     receiver="agent2@localhost",
            ...     action="update-database",
            ...     parameters={"table": "users"}
            ... )
        """
        if parameters is None:
            parameters = {}

        content = {
            "action": action,
            "parameters": parameters,
            "timestamp": datetime.now().isoformat(),
        }

        return (
            cls(sender, receiver)
            .set_performative("request")
            .set_body(content)
            .set_ontology("action-request")
            .set_protocol("fipa-request")
            .set_reply_by(10)
            .build()
        )

    @classmethod
    def create_response_message(
        cls, original_msg: Message, content: dict, performative: str = "confirm"
    ) -> Message:
        """
        Create a response message to another message.

        Args:
            original_msg (Message): Original message being responded to.
            content (Dict): Response content.
            performative (str): Response performative ("confirm", "failure", etc.).

        Returns:
            Message: FIPA-ACL response message.

        Example:
            >>> response = FIPAMessageBuilder.create_response_message(
            ...     original_msg=received_msg,
            ...     content={"status": "success"},
            ...     performative="confirm"
            ... )
        """
        # Extract metadata from original message
        original_metadata = original_msg.metadata

        return (
            cls(
                sender=str(original_msg.to),  # Swap sender/receiver
                receiver=str(original_msg.sender),
            )
            .set_performative(performative)
            .set_body(content)
            .set_ontology(original_metadata.get("ontology", "response"))
            .set_conversation_id(original_metadata.get("conversation-id", "unknown"))
            .set_in_reply_to(original_metadata.get("reply-with", ""))
            .set_protocol(original_metadata.get("protocol", "fipa-request"))
            .build()
        )


class FIPAMessageParser:
    """
    Parser for received FIPA-ACL messages.

    Provides methods for extracting and validating FIPA metadata
    from incoming messages.
    """

    def __init__(self, message: Message):
        """
        Initialize the parser with a received message.

        Args:
            message (Message): Received SPADE message.
        """
        self.message = message
        self.metadata = message.metadata

    def get_performative(self) -> str:
        """
        Get the message performative.

        Returns:
            str: Message performative, or "unknown" if not present.
        """
        return self.metadata.get("performative", "unknown")

    def get_conversation_id(self) -> str:
        """
        Get the conversation ID.

        Returns:
            str: Conversation ID, or "unknown" if not present.
        """
        return self.metadata.get("conversation-id", "unknown")

    def get_ontology(self) -> str:
        """
        Get the message ontology.

        Returns:
            str: Message ontology, or "unknown" if not present.
        """
        return self.metadata.get("ontology", "unknown")

    def get_language(self) -> str:
        """
        Get the content language.

        Returns:
            str: Content language, or "unknown" if not present.
        """
        return self.metadata.get("language", "unknown")

    def get_protocol(self) -> str:
        """
        Get the interaction protocol.

        Returns:
            str: FIPA protocol, or "unknown" if not present.
        """
        return self.metadata.get("protocol", "unknown")

    def get_reply_with(self) -> str:
        """
        Get the message ID for responses.

        Returns:
            str: Value of 'reply-with', or empty string if not present.
        """
        return self.metadata.get("reply-with", "")

    def get_custom_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get custom metadata.

        Args:
            key (str): Metadata key.
            default: Default value if key does not exist.

        Returns:
            Any: Metadata value or default value.
        """
        return self.metadata.get(key, default)

    def parse_body(self) -> Any:
        """
        Parse the message body according to its language.

        Returns:
            Any: Parsed content. If the language is "json" (or the body looks 
            like JSON), returns the decoded JSON (typically a dict or list). 
            If JSON parsing fails or the body is not JSON, returns the 
            original body string unchanged.

        Note:
            This method does NOT raise ``json.JSONDecodeError``. Instead, it 
            gracefully returns the raw body string when JSON decoding fails, 
            allowing callers to handle malformed content as needed.

        Example:
            >>> parser = FIPAMessageParser(message)
            >>> content = parser.parse_body()  # Returns dict if JSON, str otherwise
        """
        language = self.get_language()

        if language == "json":
            try:
                return json.loads(self.message.body)
            except json.JSONDecodeError:
                # If JSON parsing fails, return body as string
                return self.message.body
        else:
            # If language is not explicitly 'json', try to detect if it's JSON
            try:
                # Check if body looks like JSON (starts with { or [)
                body_str = self.message.body
                if body_str and body_str.strip().startswith(("{", "[")):
                    return json.loads(body_str)
            except (json.JSONDecodeError, AttributeError):
                # If not valid JSON or not a string, return as is
                pass

            return self.message.body

    def is_valid_fipa_message(self) -> bool:
        """
        Check if the message has the basic FIPA-ACL structure.

        Returns:
            bool: True if message passes FIPA-ACL validation.
        """
        is_valid, _ = self.validate_fipa_message()
        return is_valid

    def validate_fipa_message(self) -> tuple[bool, str]:
        """
        Fully validate a FIPA-ACL message and return error details.

        Returns:
            tuple[bool, str]: (is_valid, error_message_or_empty)
        """
        # Check performative
        if "performative" not in self.metadata:
            return False, "Missing 'performative' field"

        performative = self.metadata["performative"]
        if performative not in FIPAMessageBuilder.PERFORMATIVES:
            return False, f"Performative '{performative}' is not valid"

        # Check conversation-id
        if "conversation-id" not in self.metadata:
            return False, "Missing 'conversation-id' field"

        # Check that body is valid JSON if language is JSON
        if self.get_language() == "json":
            try:
                json.loads(self.message.body)
            except json.JSONDecodeError:
                return False, "Message body is not valid JSON"

        return True, ""

    def print_debug_info(self) -> str:
        """
        Build and log debug information about the FIPA message.

        Returns:
            str: The formatted debug string (also logged via logger.info).
        """
        lines = [
            "=" * 60,
            "FIPA-ACL MESSAGE RECEIVED",
            "=" * 60,
            f"From: {self.message.sender}",
            f"To: {self.message.to}",
            f"Performative: {self.get_performative()}",
            f"Conversation-ID: {self.get_conversation_id()}",
            f"Ontology: {self.get_ontology()}",
            f"Language: {self.get_language()}",
            f"Protocol: {self.get_protocol()}",
            f"Reply-With: {self.get_reply_with()}",
            f"Body length: {len(self.message.body)} chars",
            "=" * 60,
        ]

        # Show body if it's short
        if len(self.message.body) < 500:
            try:
                parsed = self.parse_body()
                lines.append("Content:")
                lines.append(json.dumps(parsed, indent=2, ensure_ascii=False))
            except (json.JSONDecodeError, TypeError):
                lines.append("Content (raw):")
                preview = self.message.body[:200]
                if len(self.message.body) > 200:
                    preview += "..."
                lines.append(preview)

        lines.append("=" * 60)

        # Build final string and log it
        debug_str = "\n".join(lines)
        logger.info(debug_str)

        return debug_str