from .data import Map, Point, Direction, Move, Stroke
from .superstar import traverse_the_stars
from typing import Tuple, List, Optional
from dataclasses import dataclass
from enum import Enum


class ErrorEnum(Enum):
    EDGE_ALREADY_TAKEN = 1
    EDGE_INSIDE_AREA = 2
    INTERNAL_SOLVER_ERROR = 3


@dataclass
class GameRuleException(Exception):
    cause: ErrorEnum


class GameJudge:
    def __init__(self, size: Tuple[int], closed_borders: bool = True):
        # for now let's assert that's always truth
        assert closed_borders
        board = [[[] for _y in range(size[1])] for _x in range(size[0])]
        self.owned_fields = {}
        self.map = Map(board)
        self.last_area = None

    def move(self, start: Point, end: Point) -> Optional[int]:
        move = self.__parse_move(start, end)
        self.__check_move(move)
        self.__update_board(move)
        res = traverse_the_stars(self.map, Stroke.from_move(move))
        if res is not None:
            self.last_area = res
            return len(self.last_area)
        return None

    def apply_move(self, player: int) -> List[Point]:
        if self.last_area is None:
            raise GameRuleException(ErrorEnum.INTERNAL_SOLVER_ERROR)
        for point in self.last_area:
            self.owned_fields[point] = player
        area = self.last_area
        self.last_area = None
        return area

    def __update_board(self, move: Move) -> None:
        self.map[move.pos].append(move.dir)

    def __check_move(self, move: Move) -> None:
        self.__check_edge_empty(move)
        self.__check_edge_free_field(move)

    def __check_edge_empty(self, move: Move) -> None:
        if move.dir in self.map[move.pos]:
            raise GameRuleException(ErrorEnum.EDGE_ALREADY_TAKEN)

    def __check_edge_free_field(self, move: Move) -> None:
        own_taken = move.pos in self.owned_fields
        nhbd_taken = False
        if move.dir is Direction.Horizontal and move.pos.y > 0 and \
                Point(move.pos.x, move.pos.y - 1) in self.owned_fields:
            nhbd_taken = True
        elif move.pos.x > 0 and Point(move.pos.x - 1, move.pos.y) in self.owned_fields and own_taken:
            nhbd_taken = True
        if own_taken and nhbd_taken:
            raise GameRuleException(ErrorEnum.EDGE_INSIDE_AREA)

    @staticmethod
    def __parse_move(a: Point, b: Point) -> Move:
        start = min(a, b)
        stop = max(a, b)
        if start.x == stop.x and stop.y - start.y == 1:
            return Move(start, Direction.Vertical)
        if start.y == stop.y and stop.x - start.x == 1:
            return Move(start, Direction.Horizontal)
        raise ValueError('Wrong stroke positions!')

