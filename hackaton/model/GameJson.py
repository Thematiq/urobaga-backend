import asyncio

from enum import Enum
from pydantic import BaseModel
from dataclasses import dataclass
from fastapi import WebSocket
from typing import Optional, List


from pydantic import BaseModel
from enum import Enum
from typing import Dict, List



class MessageType(Enum):
    Token = "TOKEN"
    Rules = "RULES"
    Player_list = "PLAYER_LIST"
    Start = "START"
    Error = "ERROR"
    Join = "JOIN"
    Quit = "QUIT"
    Quiz = "QUIZ"
    Move = "MOVE"


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




"""
Client
"""


class JsonPoint(BaseModel):
    x: int
    y: int


"""
Server
"""


class PlayersOrder(BaseModel):
    order: List[int]
    can_move: bool


class Question(BaseModel):
    question_content: str
    point: int


class Field(BaseModel):
    point: List[JsonPoint]


class Message(BaseModel):
    type: MessageType
    message: str

"""
Room
"""


class Token(BaseMessage, type=MessageType.Token):
    token: str


class User(BaseModel):
    id: int
    name: str
    is_host: bool


class PlayerList(BaseMessage, type=MessageType.Player_list):
    players: List[User]


@dataclass
class Player:
    id: int
    name: str
    websocket: WebSocket
    is_host: bool
    listening_task: Optional[asyncio.Task]


class GameRules(BaseMessage, type=MessageType.Rules):
    type: MessageType = MessageType.Rules
    height: int = 10
    width: int = 5
    move_timeout: float = 30.0
    question_timeout: float = 10.0


class JsonQuizQuestion(BaseModel):
    question: str
    difficulty: int
    answers: List[str]


class QuizRequest(BaseMessage, type=MessageType.Quiz):
    type: MessageType = MessageType.Quiz
    questions: List[JsonQuizQuestion]


class Move(BaseMessage, type=MessageType.Move):
    start_point: JsonPoint
    end_point: JsonPoint


class ReplyModel(BaseModel):
    move: Optional[Move]  # Move is empty if there will be timeout
    players_order: PlayersOrder
    field: Optional[Field]