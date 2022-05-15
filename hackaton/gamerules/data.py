from dataclasses import dataclass
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum, auto


class Marker(Enum):
    Left = auto()
    Right = auto()


class Direction(Enum):
    Horizontal = auto()
    Vertical = auto()


@dataclass
class Point:
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


class Map:
    def __init__(self, board):
        self.map = board
        self.h = len(board)
        self.w = len(board[0])

    def __getitem__(self, item: Point) -> List[Direction]:
        if not isinstance(item, Point):
            raise TypeError
        return self.map[item.y][item.x]


class Stroke:
    def __init__(self, start: Point, stop: Point):
        self.start = min(start, stop)
        self.stop = max(start, stop)
        if self.stop.x != self.start.x:
            self.type = Direction.Horizontal
        else:
            self.type = Direction.Vertical


@dataclass
class SuperStarField:
    parent: Optional[Point] = None
    marker: Optional[Marker] = None


class Field(BaseModel):
    owner: Optional[int]


