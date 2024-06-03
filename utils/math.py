from dataclasses import dataclass
import numpy as np
from pygame import Vector2, Vector3
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

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)


@dataclass
class Pose(Point):
    theta: float

    @property
    def point(self):
        return Point(self.x, self.y)

    def to_vect3(self):
        return Vector3(self.x, self.y, self.theta)


def diff(p1: Point, p2: Point):
    return Point(p1.x - p2.x, p1.y - p2.y)


def add(p1: Point, p2: Point):
    return Point(p1.x + p2.x, p1.y + p2.y)


def cross(v1: Point, v2: Point):
    return v1.x * v2.y - v2.x * v1.y


# [0,0,z] x [x,y,0]
def cross3(z_mag: float, xy_vec: Point):
    return Point(-z_mag * xy_vec.y, z_mag * xy_vec.x)


# add p2 (rel p1 body frame) to p1
def add_body_frame(p1: Pose, p2: Pose) -> Pose:
    return Pose(
        p1.x + p2.x * np.cos(p1.theta) - p2.y * np.sin(p1.theta),
        p1.y + p2.y * np.cos(p1.theta) + p2.x * np.sin(p1.theta),
        p1.theta + p2.theta,
    )


def dot(v1: Point, v2: Point):
    return v1.x * v2.x + v1.y * v2.y


def norm(p: Point):
    return np.sqrt(p.x**2 + p.y**2)


def rot(p: Point, theta):
    return Point(
        p.x * np.cos(theta) - p.y * np.sin(theta),
        p.x * np.sin(theta) + p.y * np.cos(theta),
    )


def unit_vec2(p: float):
    return Point(np.cos(p), np.sin(p))


def distance(p1: Point, p2: Point):
    return np.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)


def rot_trans_3d(
    vect_3d: np.ndarray,
    angle_rad: float = 0.0,
    dx: Union[float, np.ndarray] = 0.0,
    dy: Union[float, np.ndarray] = 0.0,
    scale_vec: float = 1.0,
    scale_trans: float = 1.0,
    rotate_first: bool = True,
) -> np.ndarray:
    """
    Applies rotation and translation to a 3D vector.

    Args:
        vect_3d (np.ndarray): The input 3D vector of shape (3 x N).
        angle_rad (float, optional): The rotation angle in radians. Defaults to 0.0.
        dx (Union[float, np.ndarray], optional): The translation in the x-axis. Defaults to 0.0.
        dy (Union[float, np.ndarray], optional): The translation in the y-axis. Defaults to 0.0.
        scale_vec (float, optional): The scaling factor for rotation. Defaults to 1.0.
        scale_trans (float, optional): The scaling factor for translation. Defaults to 1.0.
        rotate_first (bool, optional): Determines whether rotation is applied before translation. Defaults to True.

    Returns:
        np.ndarray: The transformed 3D vector of shape (3 x N).
    """
    rot_mat = np.array(
        [
            [np.cos(angle_rad), -np.sin(angle_rad)],
            [np.sin(angle_rad), np.cos(angle_rad)],
        ]
    )
    if rotate_first:
        return np.vstack(
            [
                np.dot(rot_mat, scale_vec * vect_3d[:2, :])
                + scale_trans * np.vstack([dx, dy]),
                vect_3d[2, :] + angle_rad,
            ]
        )
    else:
        return np.vstack(
            [
                np.dot(
                    rot_mat,
                    scale_vec * vect_3d[:2, :] + scale_trans * np.vstack([dx, dy]),
                ),
                vect_3d[2, :] + angle_rad,
            ]
        )


def rot_trans_2d(
    vect_2d: np.ndarray,
    dx: Union[float, np.ndarray] = 0.0,
    dy: Union[float, np.ndarray] = 0.0,
    angle_rad: float = 0.0,
    scale_vec: float = 1.0,
    scale_trans: float = 1.0,
    rotate_first: bool = True,
) -> np.ndarray:
    """
    Applies rotation and translation to a 2D vector.

    Args:
        vect_2d (2 x N): The input 2D vector.
        dx (Union[float, np.ndarray], optional): The translation in the x-axis. Defaults to 0.0.
        dy (Union[float, np.ndarray], optional): The translation in the y-axis. Defaults to 0.0.
        angle_rad (float, optional): The rotation angle in radians. Defaults to 0.0.
        scale (float, optional): The scaling factor. Defaults to 1.0.

    Returns:
        np.ndarray (2 x N): The transformed 2D vector.
    """
    vec_3d = np.vstack([vect_2d, np.zeros(vect_2d.shape[1])])
    new_vec_3d = rot_trans_3d(
        vec_3d,
        angle_rad,
        dx,
        dy,
        scale_vec=scale_vec,
        scale_trans=scale_trans,
        rotate_first=rotate_first,
    )
    return new_vec_3d[:2, :]


def trans_rot(pts: Union[Point, List[Point]], x: float, y: float, theta: float):
    if type(pts) is Point:
        pts = [pts]

    return [
        Point(
            p.x * np.cos(theta) - p.y * np.sin(theta) + x,
            p.x * np.sin(theta) + p.y * np.cos(theta) + y,
        )
        for p in pts
    ]


def pi_2_pi(angle):
    return (angle + np.pi) % (2 * np.pi) - np.pi
