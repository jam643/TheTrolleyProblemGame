import pygame
import numpy as np

from dynamics.CartesianDynamicBicycleModel import CartesianDynamicBicycleModel
from paths.PathBase import PathBase
from control.ControllerBase import ControllerBase
import utils.math as math


class PIDControl(ControllerBase):
    def __init__(self, p, d):
        self.p = p
        self.d = d
        self.steer_cont = 0
        self.car_rel_path = math.Point(0, 0)
        self.nearest_pose = math.Pose(0,0,0)
        self.lookahead_pose = math.Pose(0,0,0)

    def update(self, car: CartesianDynamicBicycleModel, path: PathBase) -> float:
        if not path:
            return self.steer_cont
        self.nearest_pose, station = path.get_nearest_pose(car.coord)
        if self.nearest_pose:
            self.lookahead_pose = path.get_pose_at_station(station + 10)
            dist = math.distance(self.nearest_pose.get_point, car.coord)
            car_theta = car.z[car.StateIdx.THETA]
            self.car_rel_path = math.diff(car.coord, self.nearest_pose.get_point)
            sign = np.sign(
                math.cross(math.unit_vec2(car_theta), self.car_rel_path))

            lat_err_dot = math.cross(math.unit_vec2(self.nearest_pose.theta), car.vel)

            self.steer_cont = -self.p * sign * dist - self.d*lat_err_dot
        return min(0.7, max(-0.7, self.steer_cont))
