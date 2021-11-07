import numpy as np
from dataclasses import dataclass

from dynamics.CartesianDynamicBicycleModel import CartesianDynamicBicycleModel
from paths.PathBase import PathBase
from control.ControllerBase import ControllerBase
import utils.math as math


class StanleyControl(ControllerBase):
    @dataclass
    class Params:
        k: float

    def __init__(self, params: Params):
        self.set_params(params)

        self.nearest_pose = math.Pose(0, 0, 0)
        self.steer_cont = 0
        self.car_front_axle = None
        self.cte = None
        self.path_unit_normal = None

    def set_params(self, params: Params):
        self.params = params

    def update(self, car: CartesianDynamicBicycleModel, path: PathBase) -> float:
        if not path:
            return self.steer_cont
        self.car_front_axle = car.pose_front_axle
        self.nearest_pose, station = path.get_nearest_pose(self.car_front_axle)
        if self.nearest_pose:
            theta_e = car.pose.theta - self.nearest_pose.theta
            self.path_unit_normal = math.unit_vec2(self.nearest_pose.theta + np.pi/2)
            self.cte = math.dot(math.diff(car.pose, self.nearest_pose), self.path_unit_normal)
            self.steer_cont = -theta_e + np.arctan2(-self.params.k*self.cte, car.vx)
        return min(0.7, max(-0.7, self.steer_cont))
