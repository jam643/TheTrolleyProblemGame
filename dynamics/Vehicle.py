from dataclasses import dataclass
import numpy as np

from utils import math


class Vehicle:
    @dataclass
    class State:
        x: float = 0
        y: float = 0
        theta: float = 0
        delta: float = 0
        vx: float = 0  # body frame
        vy: float = 0  # body frame
        thetadot: float = 0

    @dataclass
    class Params:
        m: float = 2000  # Mass[kg]
        Iz: float = 4000  # Yaw inertia[kg * m ^ 2]
        lf: float = 1.5  # Distance from CG to front axle[m]
        lr: float = 1.5  # Distance from CG to rear axle[m]
        cf: float = 1e5  # Front cornering stiffness[N / rad]
        cr: float = 1e5  # Rear cornering stiffness[N / rad]
        delta_max: float = np.deg2rad(60)  # +/- tire angle limit [rad]

        @property
        def wheel_base(self):
            return self.lf + self.lr

    def __init__(self, state_cog: State = None, params: Params = None):
        self.state_cog = state_cog if state_cog else self.State()
        self.params = params if params else self.Params()

    def build_pose(self, pose: math.Pose):
        self.state_cog.x = pose.x
        self.state_cog.y = pose.y
        self.state_cog.theta = pose.theta
        return self

    def build_vel(self, vel: float, beta: float):
        self.state_cog.vx = vel * np.cos(beta)
        self.state_cog.vy = vel * np.sin(beta)
        return self

    @property
    def pose(self) -> math.Pose:
        return math.Pose(self.state_cog.x, self.state_cog.y, self.state_cog.theta)

    @property
    def pose_rear_axle(self) -> math.Pose:
        return math.add_body_frame(self.pose, math.Pose(-self.params.lr, 0, 0))

    @property
    def pose_front_axle(self) -> math.Pose:
        return math.add_body_frame(self.pose, math.Pose(self.params.lf, 0, 0))

    @property
    def point(self) -> math.Point:
        return math.Point(self.state_cog.x, self.state_cog.y)

    @property
    def vel_cog(self):
        return math.rot(math.Point(self.state_cog.vx, self.state_cog.vy), self.state_cog.theta)

    @property
    def vel_cog_mag(self):
        return np.sqrt(self.state_cog.vx ** 2 + self.state_cog.vy ** 2)

    def vel_at_pnt(self, pt_rel_cog: math.Point):
        return self.vel_cog + math.cross3(self.state_cog.thetadot, math.rot(pt_rel_cog, self.state_cog.theta))

