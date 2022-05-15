from pydantic import BaseModel
from typing import Optional, List

"""
Client
"""


class Point(BaseModel):
    x: int
    y: int


class Move(BaseModel):
    start_point: Point
    end_point: Point
    user: int


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
    move: Optional[Move]    # Move is empty if there will be timeout
    players_order: PlayersOrder
    field: Optional[Field]
    questions: Optional[List[Question]]
    no_move: bool


class ErrorMsg(BaseModel):
    message: str
# print(PlayersOrder.schema_json(indent=2))
