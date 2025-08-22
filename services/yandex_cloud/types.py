from collections.abc import Callable
from typing import TypeAlias
from dataclasses import dataclass, field


__all__ = [
    'MessageGroupId',
    'Message',
    'MessageGroup',
    'MessagesGroupsHandler'
]


MessageGroupId: TypeAlias = str

@dataclass
class Message:
    text: str
    receipt_handle: str


@dataclass
class MessageGroup:
    group_id: MessageGroupId
    messages: list[Message] = field(default_factory=list)


MessagesGroupsHandler = Callable[[MessageGroup], bool]
