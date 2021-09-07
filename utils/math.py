from dataclasses import dataclass
import numpy as np
from pygame import Vector2


@dataclass
class Point:
    x: float
    y: float

    def to_vect2(self):
        return Vector2(self.x, self.y)


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
    return Point(p.x*np.cos(theta) - p.y*np.sin(theta), p.x*np.sin(theta)+p.y*np.cos(theta))


def unit_vec(v: Point):
    n = distance(v, Point(0, 0))
    return Point(n.x / norm, n.y / norm)


def unit_vec2(p: float):
    return Point(np.cos(p), np.sign(p))


def distance(p1: Point, p2: Point):
    return np.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)
