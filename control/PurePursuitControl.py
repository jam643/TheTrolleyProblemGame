from dataclasses import dataclass
import numpy as np

from dynamics.CartesianDynamicBicycleModel import Vehicle
from paths.PathBase import PathBase
from control.ControllerBase import ControllerBase
import utils.math as math


class PurePursuitControl(ControllerBase):
    @dataclass
    class Params:
        lookahead_k: float

    def __init__(self, params: Params):
        self.set_params(params)
        self.nearest_pose = math.Pose(0, 0, 0)
        self.steer_cont = 0
        self.lookahead_pose = math.Pose(0, 0, 0)
        self.lookahead_dist = 0
        self.alpha = 0
        self.radius = 0
        self.car_rear_axle = None

    def set_params(self, params: Params):
        self.params = params

    def update(self, car: Vehicle, path: PathBase) -> float:
        self.path = path
        if not path:
            return self.steer_cont
        self.car_ref_pnt = car.pose_rear_axle.point
        self.nearest_pose, self.station = path.get_nearest_pose(self.car_ref_pnt)
        if self.nearest_pose:
            self.lookahead_pose = path.get_pose_at_station(self.station + car.state_cog.vx * self.params.lookahead_k)
            lookahead_in_car_frame = math.rot(math.diff(self.lookahead_pose, car.pose_rear_axle), -car.pose.theta)
            self.alpha = np.arctan2(lookahead_in_car_frame.y, lookahead_in_car_frame.x)

            self.car_rear_axle = car.pose_rear_axle
            self.lookahead_dist = math.distance(car.pose_rear_axle, self.lookahead_pose)

            self.radius = self.lookahead_dist/(2*np.sin(self.alpha))
            self.steer_cont = np.arctan((car.params.lf + car.params.lr) / self.radius)
        return min(0.7, max(-0.7, self.steer_cont))
