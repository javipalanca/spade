# Slixmpp: The Slick XMPP Library
# Copyright © 2021 Mathieu Pasquet <mathieui@mathieui.net>
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.

"""
This file contains boilerplate to define types relevant to slixmpp.
"""

from typing import (
    Any,
    Dict,
    Optional,
    Union,
    Iterable,
    List,
)

try:
    from typing import (
        Literal,
        TypedDict,
        Protocol,
    )
except ImportError:
    from typing_extensions import (
        Literal,
        TypedDict,
        Protocol,
    )

from slixmpp.jid import JID

PresenceTypes = Literal[
    'error', 'probe', 'subscribe', 'subscribed',
    'unavailable', 'unsubscribe', 'unsubscribed',
]

PresenceShows = Literal[
    'away', 'chat', 'dnd', 'xa',
]

# add the empty string, but not for sending
ExtPresenceShows = Literal[
    'away', 'chat', 'dnd', 'xa', ''
]

MessageTypes = Literal[
    'chat', 'error', 'groupchat',
    'headline', 'normal',
]

IqTypes = Literal[
    "error", "get", "set", "result",
]

MucRole = Literal[
    'moderator', 'participant', 'visitor', 'none'
]

MucAffiliation = Literal[
    'outcast', 'member', 'admin', 'owner', 'none'
]

OptJid = Optional[JID]
JidStr = Union[str, JID]
OptJidStr = Optional[Union[str, JID]]

class PresenceArgs(TypedDict, total=False):
    pfrom: JidStr
    pto: JidStr
    pshow: PresenceShows
    ptype: PresenceTypes
    pstatus: str


class MucRoomItem(TypedDict, total=False):
    jid: str
    role: MucRole
    affiliation: MucAffiliation
    show: Optional[PresenceShows]
    status: str
    alt_nick: str


class ResourceDict(TypedDict, total=False):
    show: ExtPresenceShows
    priority: int
    status: str


RosterState = TypedDict(
    'RosterState',
    {
        'from': bool,
        'to': bool,
        'pending_in': bool,
        'pending_out': bool,
        'whitelisted': bool,
        'subscription': str,
        'name': str,
        'groups': List[str],
        'removed': bool,
    }
)


class RosterDBProtocol(Protocol):
    def load(self, owner:JidStr, jid:JidStr, db_state: Dict[str, Any]) -> Optional[RosterState]:
        ...

    def save(self, owner:JidStr, jid:JidStr, state: RosterState, db_state: Dict[str, Any]):
        ...

    def entries(self, owner: OptJidStr, db_state: Optional[dict[str, Any]] = None) -> Iterable[str]:
        ...


MucRoomItemKeys = Literal[
    'jid', 'role', 'affiliation', 'show', 'status',  'alt_nick',
]

MAMDefault = Literal['always', 'never', 'roster']

FilterString = Literal['in', 'out', 'out_sync']

ErrorTypes = Literal["modify", "cancel", "auth", "wait", "cancel"]

ErrorConditions = Literal[
    "bad-request",
    "conflict",
    "feature-not-implemented",
    "forbidden",
    "gone",
    "internal-server-error",
    "item-not-found",
    "jid-malformed",
    "not-acceptable",
    "not-allowed",
    "not-authorized",
    "payment-required",
    "policy-violation",
    "recipient-unavailable",
    "redirect",
    "registration-required",
    "remote-server-not-found",
    "remote-server-timeout",
    "resource-constraint",
    "service-unavailable",
    "subscription-required",
    "undefined-condition",
    "unexpected-request",
]

# https://xmpp.org/registrar/disco-categories.html#client
ClientTypes = Literal[
    "bot",
    "console",
    "game",
    "handheld",
    "pc",
    "phone",
    "sms",
    "tablet",
    "web",
]

__all__ = [
    'Protocol', 'TypedDict', 'Literal', 'OptJid', 'OptJidStr', 'JidStr', 'MAMDefault',
    'PresenceTypes', 'PresenceShows', 'MessageTypes', 'IqTypes', 'MucRole',
    'MucAffiliation', 'FilterString', 'ErrorConditions', 'ErrorTypes', 'ClientTypes'
]
