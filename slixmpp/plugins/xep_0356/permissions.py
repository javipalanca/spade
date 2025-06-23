import dataclasses
from collections import defaultdict
from enum import Enum


class RosterAccess(str, Enum):
    NONE = "none"
    GET = "get"
    SET = "set"
    BOTH = "both"


class MessagePermission(str, Enum):
    NONE = "none"
    OUTGOING = "outgoing"


class IqPermission(str, Enum):
    NONE = "none"
    GET = "get"
    SET = "set"
    BOTH = "both"


class PresencePermission(str, Enum):
    NONE = "none"
    MANAGED_ENTITY = "managed_entity"
    ROSTER = "roster"


@dataclasses.dataclass
class Permissions:
    roster = RosterAccess.NONE
    message = MessagePermission.NONE
    iq = defaultdict(lambda: IqPermission.NONE)
    presence = PresencePermission.NONE
