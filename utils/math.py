from dataclasses import dataclass
import numpy as np
from pygame import Vector2
from typing import Union, List, Tuple


@dataclass
class Point:
    x: float
    y: float

    def to_vect2(self):
        return Vector2(self.x, self.y)

    @staticmethod
    def from_list(pts: List[Union[List, Tuple]]):
        return [Point(p[0], p[1]) for p in pts]

    def __setitem__(self, idx, data):
        if idx is 0:
            self.x = data
        elif idx is 1:
            self.y = data

    def __getitem__(self, idx):
        if idx is 0:
            return self.x
        if idx is 1:
            return self.y


@dataclass
class Pose(Point):
    theta: float

    @property
    def get_point(self):
        return Point(self.x, self.y)


def diff(p1: Point, p2: Point):
    return Point(p1.x - p2.x, p1.y - p2.y)


def add(p1: Point, p2: Point):
    return Point(p1.x + p2.x, p1.y + p2.y)


def cross(v1: Point, v2: Point):
    return v1.x * v2.y - v2.x * v1.y


def add_body_frame(p1: Pose, p2: Pose) -> Pose:
    return Pose(p1.x + p2.x * np.cos(p1.theta) - p2.y * np.sin(p1.theta),
                p1.y + p2.y * np.cos(p1.theta) + p2.x * np.sin(p1.theta), p1.theta + p2.theta)


def dot(v1: Point, v2: Point):
    return v1.x * v2.x + v1.y * v2.y


def rot(p: Point, theta):
    return Point(p.x * np.cos(theta) - p.y * np.sin(theta), p.x * np.sin(theta) + p.y * np.cos(theta))


def unit_vec(v: Point):
    n = distance(v, Point(0, 0))
    return Point(n.x / norm, n.y / norm)


def unit_vec2(p: float):
    return Point(np.cos(p), np.sin(p))


def distance(p1: Point, p2: Point):
    return np.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)


def trans_rot(pts: Union[Point, List[Point]], x: float, y: float, theta: float):
    if type(pts) is Point:
        pts = [pts]

    return [Point(p.x * np.cos(theta) - p.y * np.sin(theta) + x, p.x * np.sin(theta) + p.y * np.cos(theta) + y) for p in
            pts]
