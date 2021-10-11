import pygame
import numpy as np

from dynamics.CartesianDynamicBicycleModel import CartesianDynamicBicycleModel
from paths.PathBase import PathBase
from control.ControllerBase import ControllerBase
import utils.math as math


class SpeedControl(ControllerBase):
    def __init__(self, station_setpoint):
        self.min_speed = 2
        self.max_speed = 20
        self.min_accel = -4
        self.max_accel = 3
        self.speed_cont = 10
        self.station_setpoint = station_setpoint
        self.station_to_end = None
        self.p = 1/2
        self.p_d = 1

    def update(self, car: CartesianDynamicBicycleModel, path: PathBase, dt) -> float:
        if not path:
            return self.steer_cont
        self.nearest_pose, station = path.get_nearest_pose(car.pose_rear_axle)
        if self.nearest_pose:
            station_to_end = path.spline_station[-1] - station
            station_rate = 0
            if self.station_to_end:
                station_rate = (station_to_end - self.station_to_end)/dt
            self.station_to_end = station_to_end
            accel = -self.p * (self.station_setpoint - station_to_end) + self.p_d * station_rate
            accel = max(self.min_accel, min(self.max_accel, accel))
            self.speed_cont = max(self.min_speed, min(self.max_speed, self.speed_cont + dt * accel))
        return self.speed_cont
