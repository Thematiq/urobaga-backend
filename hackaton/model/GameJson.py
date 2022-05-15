import asyncio

from enum import Enum
from pydantic import BaseModel
from dataclasses import dataclass
from fastapi import WebSocket
from typing import Optional, List


class MessageType(Enum):
    Start = "START"
    Error = "ERROR"
    Join = "JOIN"
    Quit = "QUIT"


"""
Client
"""


class Point(BaseModel):
    x: int
    y: int


class Move(BaseModel):
    start_point: Point
    end_point: Point
    # user: int


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
    point: List[Point]


class ReplyModel:
    move: Optional[Move]  # Move is empty if there will be timeout
    players_order: PlayersOrder
    field: Optional[Field]
    questions: Optional[List[Question]]
    no_move: bool


class Message(BaseModel):
    type: MessageType
    message: str


print(Move.schema_json(indent=2))


"""
Room
"""


class Token(BaseModel):
    token: str


class User(BaseModel):
    id: int
    name: str
    is_host: bool


@dataclass
class Player:
    id: int
    name: str
    websocket: WebSocket
    is_host: bool
    listening_task: Optional[asyncio.Task]


class GameRules(BaseModel):
    height: int = 10
    width: int = 5
    move_timeout: float = 30.0

