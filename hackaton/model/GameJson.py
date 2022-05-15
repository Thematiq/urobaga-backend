import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import List
from typing import Optional

from fastapi import WebSocket
from pydantic import BaseModel


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

    class Config:
        use_enum_values = True


"""
Client
"""


class Point(BaseModel):
    x: int
    y: int

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        if not isinstance(other, Point):
            return False
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        if not isinstance(other, Point):
            raise TypeError
        return self.x < other.x or (self.x == other.x and self.y < other.y)


class Quit(BaseMessage, type=MessageType.Quit):
    type: MessageType = MessageType.Quit


class Start(BaseMessage, type=MessageType.Start):
    type: MessageType = MessageType.Start


"""
Server
"""


class PlayersOrder(BaseModel):
    order: List[int]
    current_player: int


class Question(BaseModel):
    question_content: str
    point: int


class Field(BaseModel):
    point: List[Point]


class Message(BaseModel):
    type: MessageType
    message: str


"""
Room
"""


class Token(BaseMessage, type=MessageType.Token):
    type: MessageType = MessageType.Token
    token: str


class User(BaseModel):
    id: int
    name: str
    is_host: bool


class PlayerList(BaseMessage, type=MessageType.Player_list):
    type: MessageType = MessageType.Player_list
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


class JsonMove(BaseMessage, type=MessageType.Move):
    start_point: Point
    end_point: Point
    user: Optional[int]


class ReplyModel(BaseModel):
    move: Optional[JsonMove]  # Move is empty if there will be timeout
    players_order: PlayersOrder
    field: Optional[Field]
