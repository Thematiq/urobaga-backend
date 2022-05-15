import pytest

from hackaton.gamerules.data import Map, Stroke, Direction, Point
from hackaton.gamerules.superstar import traverse_the_stars


open_map = Map([
    [[], [], [], [], []],
    [[], [], [], [Direction.Vertical], []],
    [[Direction.Horizontal], [Direction.Horizontal], [Direction.Horizontal], [], []],
    [[], [], [], [], []]])
open_stroke = Stroke(Point(3, 1), Point(3, 2))
open_result = None

closed_map = Map([
    [[], [], [], []],
    [[], [Direction.Horizontal, Direction.Vertical], [Direction.Vertical], []],
    [[], [Direction.Vertical], [Direction.Horizontal], [Direction.Vertical]],
    [[], [Direction.Horizontal], [Direction.Horizontal], []]])
closed_stroke = Stroke(Point(3, 2), Point(3, 3))
closed_result = [Point(1, 1), Point(1, 2), Point(2, 2)]

corner_map = Map([
    [[], [], []],
    [[], [], []],
    [[], [], []],
    [[Direction.Horizontal], [Direction.Horizontal], [Direction.Horizontal]]])
corner_stroke = Stroke(Point(0, 3), Point(1, 3))
corner_result = [Point(0, 4), Point(1, 4), Point(2, 4)]


def test_open_stars():
    assert traverse_the_stars(open_map, open_stroke) is None


def test_closed_stars():
    assert traverse_the_stars(closed_map, closed_stroke).sort() == closed_result.sort()


def test_corner_stars():
    assert traverse_the_stars(corner_map, corner_stroke).sort() == corner_result.sort()
