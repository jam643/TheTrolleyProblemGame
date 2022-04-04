import numpy as np

from paths.PathBase import PathBase
from utils import math


def get_path_unit_norm(path_pnt: math.Pose):
    return math.unit_vec2(path_pnt.theta + np.pi / 2)


def get_cross_err(path_pose: math.Pose, ref_pnt: math.Point):
    return math.dot(math.diff(ref_pnt, path_pose), get_path_unit_norm(path_pose))
