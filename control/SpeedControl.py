import pygame
import numpy as np

from dynamics.CartesianDynamicBicycleModel import CartesianDynamicBicycleModel
from paths.PathBase import PathBase
from control.ControllerBase import ControllerBase
import utils.math as math


class SpeedControl(ControllerBase):
    def __init__(self):
        self.min_speed = 2
        self.max_speed = 20
        self.min_accel = -4
        self.max_accel = 2
        self.speed_cont = 10
        self.station_setpoint = 15
        self.p = 1/5

    def update(self, car: CartesianDynamicBicycleModel, path: PathBase, dt) -> float:
        if not path:
            return self.steer_cont
        self.nearest_pose, station = path.get_nearest_pose(car.pose_rear_axle)
        if self.nearest_pose:
            station_to_end = path.spline_station[-1] - station
            accel = max(self.min_accel, min(self.max_accel, self.p*(station_to_end - self.station_setpoint)))
            self.speed_cont = max(self.min_speed, min(self.max_speed, (station_to_end - self.station_setpoint)))
        return self.speed_cont
