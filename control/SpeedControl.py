from abc import ABC, abstractmethod

from dynamics.CartesianDynamicBicycleModel import CartesianDynamicBicycleModel
from paths.PathBase import PathBase


class SpeedControl:
    @abstractmethod
    class Params:
        min_speed: float = 1
        max_speed: float = 30
        min_accel: float = -50
        max_accel: float = 10
        station_setpoint: float = 18
        p: float = 0.5
        p_d: float = 1.

    def __init__(self, params: Params):
        self._params = params
        self.station_to_setpoint = None
        self.speed_cmd = 10.
        self.nearest_pose = None

    def update(self, car: CartesianDynamicBicycleModel, path: PathBase, dt) -> float:
        if not path:
            return self.speed_cmd
        self.nearest_pose, station = path.get_nearest_pose(car.pose_rear_axle)
        if self.nearest_pose:
            # station_to_end = path.spline_station[-1] - station
            station_to_setpoint = station - max(path.spline_station[-1] - self._params.station_setpoint, path.spline_station[-1]/2)
            station_rate = 0
            if self.station_to_setpoint:
                station_rate = (station_to_setpoint - self.station_to_setpoint)/dt
            self.station_to_setpoint = station_to_setpoint
            accel = -self._params.p * (station_to_setpoint) - self._params.p_d * station_rate
            accel = max(self._params.min_accel, min(self._params.max_accel, accel))
            self.speed_cmd = max(self._params.min_speed, min(self._params.max_speed, self.speed_cmd + dt * accel))
        return self.speed_cmd

