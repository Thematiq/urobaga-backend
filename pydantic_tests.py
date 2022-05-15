from pydantic import BaseModel
from enum import Enum
from typing import Dict, List


class MessageType(Enum):
    UPDATE_GAME = "updateGame"
    UPDATE_RULES = "updateRules"
    RANDOM_MESSAGE = "randomMessage"


class BaseMessage(BaseModel):
    type: MessageType

    _subtypes_ = dict()

    def __init_subclass__(cls, type=None):
        cls._subtypes_[type or cls.__name__.lower()] = cls

    @classmethod
    def parse_obj(cls, obj):
        return cls._convert_to_real_type_(obj)

    @classmethod
    def __get_validators__(cls):
        yield cls._convert_to_real_type_

    @classmethod
    def _convert_to_real_type_(cls, data):
        data_type = MessageType(data.get("type"))
        if data_type is None:
            raise ValueError('Missing `type` field!!')

        sub = cls._subtypes_.get(data_type)

        if sub is None:
            return cls(**data)
        return sub(**data)


class UpdateRuleMessage(BaseMessage, type=MessageType.UPDATE_RULES):
    newRules: Dict[str, str]


class UpdateGame(BaseMessage, type=MessageType.UPDATE_GAME):
    newPlayers: List[str]


example_message_rules = '''{
    "type": "updateRules",
    "newRules": {
        "bruh": "test"
    }
}'''

model = BaseMessage.parse_raw(example_message_rules)

example_message_game = {
    'type': 'updateGame',
    'newPlayers': ['bob']
}

model = BaseMessage.parse_obj(example_message_game)

example_custom_message = {
    'type': 'randomMessage'
}

