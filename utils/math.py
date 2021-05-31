from dataclasses import dataclass


@dataclass
class Point:
    x: float
    y: float


@dataclass
class Pose(Point):
    theta: float
