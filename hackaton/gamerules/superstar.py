from enum import Enum, auto
from queue import PriorityQueue
from typing import Dict, Optional, List
from .data import SuperStarField, Map, Point, Stroke, Direction, Marker


class Result(Enum):
    Ok = auto()
    NoMoreMoves = auto()
    MetOther = auto()


def manhattan_distance(u: Point, v: Point) -> float:
    return abs(u.x - v.x) + abs(u.y - u.x)


class StarHandler:
    def __init__(self, marker: Marker, board: Map, starfield: Dict[Point, SuperStarField], start: Point, stop: Point):
        self.marker = marker
        self.starfield = starfield
        self.board = board
        self.start = start
        self.stop = stop
        self.points = [self.start]
        self.queue = PriorityQueue()
        self.starfield[self.start] = SuperStarField(marker=self.marker)
        self.queue.put((0, self.start))

    def perform_tick(self) -> Result:
        if self.queue.empty():
            return Result.NoMoreMoves
        u = self.queue.get()[1]
        nhbd = self.__get_check_nhbd(u)
        for v in nhbd:
            if v in self.starfield and self.starfield[v].marker is not self.marker:
                return Result.MetOther
            if v not in self.starfield:
                self.starfield[v] = SuperStarField(marker=self.marker, parent=u)
                self.queue.put((manhattan_distance(v, self.start), v))
                self.points.append(v)
        return Result.Ok

    def __get_check_nhbd(self, u: Point) -> List[Point]:
        nhbd = self.__get_nhbd(u)
        return list(filter(lambda x: x not in self.starfield or self.starfield[x].marker != self.marker, nhbd))

    def __get_nhbd(self, u: Point) -> List[Point]:
        nhbd = []
        if u.x > 0 and Direction.Vertical not in self.board[u]:
            nhbd.append(Point(u.x - 1, u.y))
        if u.y > 0 and Direction.Horizontal not in self.board[u]:
            nhbd.append(Point(u.x, u.y - 1))
        if u.x < self.board.w - 1 and Direction.Vertical not in self.board.map[u.y][u.x + 1]:
            nhbd.append(Point(u.x + 1, u.y))
        if u.y < self.board.h - 1 and Direction.Horizontal not in self.board.map[u.y + 1][u.x]:
            nhbd.append(Point(u.x, u.y + 1))
        return nhbd


def traverse_the_stars(board: Map, last_stroke: Stroke) -> Optional[List[Point]]:
    left_point = last_stroke.start
    starfield = dict()
    if last_stroke.start.x == last_stroke.stop.x:
        right_point = Point(left_point.x - 1, left_point.y)
    else:
        right_point = Point(left_point.x, left_point.y - 1)
    left_star = StarHandler(Marker.Left, board, starfield, left_point, right_point)
    right_start = StarHandler(Marker.Right, board, starfield, right_point, left_point)
    current = left_star
    while True:
        result = current.perform_tick()
        if result is Result.MetOther:
            return None
        if result is Result.NoMoreMoves:
            return current.points
        current = right_start if current is left_star else left_star
