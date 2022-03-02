from abc import ABC, abstractmethod

from dynamics.CartesianDynamicBicycleModel import CartesianDynamicBicycleModel
from paths.PathBase import PathBase


class SpeedControl:
    @abstractmethod
    class Params:
        min_speed: float = 2
        max_speed: float = 20
        min_accel: float = -4
        max_accel: float = 3
        station_setpoint: float = 10
        p: float = 0.5
        p_d: float = 1

    def __init__(self, params: Params):
        self._params = params
        self.station_to_end = None
        self.speed_cmd = 10.
        self.nearest_pose = None

    def update(self, car: CartesianDynamicBicycleModel, path: PathBase, dt) -> float:
        if not path:
            return self.speed_cmd
        self.nearest_pose, station = path.get_nearest_pose(car.pose_rear_axle)
        if self.nearest_pose:
            station_to_end = path.spline_station[-1] - station
            station_rate = 0
            if self.station_to_end:
                station_rate = (station_to_end - self.station_to_end)/dt
            self.station_to_end = station_to_end
            accel = -self._params.p * (self._params.station_setpoint - station_to_end) + self._params.p_d * station_rate
            accel = max(self._params.min_accel, min(self._params.max_accel, accel))
            self.speed_cmd = max(self._params.min_speed, min(self._params.max_speed, self.speed_cmd + dt * accel))
        return self.speed_cmd

