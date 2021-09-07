import pygame
import numpy as np

from dynamics.CartesianDynamicBicycleModel import CartesianDynamicBicycleModel
from paths.PathBase import PathBase
from control.ControllerBase import ControllerBase
import utils.math as math


class PurePursuitControl(ControllerBase):
    def __init__(self):
        self.lookahead_k = 1.
        self.nearest_pose = math.Pose(0, 0, 0)
        self.steer_cont = 0
        self.lookahead_pose = math.Pose(0, 0, 0)
        self.lookahead_dist = 0
        self.alpha = 0
        self.car_rear_axle = None

    def update(self, car: CartesianDynamicBicycleModel, path: PathBase) -> float:
        if not path:
            return self.steer_cont
        self.nearest_pose, station = path.get_nearest_pose(car.pose_rear_axle)
        if self.nearest_pose:
            self.lookahead_pose = path.get_pose_at_station(station + car.vx * self.lookahead_k)
            print("posex y: {}, {}".format(car.pose_rear_axle.x, car.pose.y))
            # alpha = np.arctan2(self.lookahead_pose.y - car.pose_rear_axle.y,
            #                    self.lookahead_pose.x - car.pose_rear_axle.x) - car.pose.theta
            lookahead_in_car_frame = math.rot(math.diff(self.lookahead_pose, car.pose), -car.pose.theta)
            self.alpha = np.arctan2(lookahead_in_car_frame.y, lookahead_in_car_frame.x)

            self.car_rear_axle = car.pose_rear_axle
            self.lookahead_dist = math.distance(car.pose_rear_axle, self.lookahead_pose)

            self.steer_cont = np.arctan((2 * (car.params.lf + car.params.lr) * np.sin(self.alpha)) / (
                self.lookahead_dist))
        return min(0.7, max(-0.7, self.steer_cont))
