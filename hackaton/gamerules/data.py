from dataclasses import dataclass
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum, auto

from ..model.GameJson import Point


class Marker(Enum):
    Left = auto()
    Right = auto()


class Direction(Enum):
    Horizontal = auto()
    Vertical = auto()


class Map:
    def __init__(self, board):
        self.map = board
        self.h = len(board)
        self.w = len(board[0])

    def __getitem__(self, item: Point) -> List[Direction]:
        if not isinstance(item, Point):
            raise TypeError
        return self.map[item.y][item.x]


@dataclass
class Move:
    pos: Point
    dir: Direction


class Stroke:
    def __init__(self, start: Point, stop: Point):
        self.start = min(start, stop)
        self.stop = max(start, stop)
        if self.stop.x != self.start.x:
            self.type = Direction.Horizontal
        else:
            self.type = Direction.Vertical

    @classmethod
    def from_move(cls, move: Move):
        if move.dir is Direction.Horizontal:
            return cls(move.pos, Point(x=move.pos.x + 1, y=move.pos.y))
        else:
            return cls(move.pos, Point(x=move.pos.x, y=move.pos.y))


@dataclass
class SuperStarField:
    parent: Optional[Point] = None
    marker: Optional[Marker] = None


class Field(BaseModel):
    owner: Optional[int]


