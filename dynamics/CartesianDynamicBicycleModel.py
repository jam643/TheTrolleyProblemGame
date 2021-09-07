import numpy as np
from typing import NamedTuple
import enum
from abc import ABC, abstractmethod
import pygame

import utils.math as math


class CarModel(ABC):
    @property
    @abstractmethod
    def vel(self):
        pass


class CartesianDynamicBicycleModel(CarModel):
    class StateIdx(enum.IntEnum):
        X = 0
        Y = 1
        VY = 2
        THETA = 3
        THETADOT = 4

    class ControlIdx(enum.IntEnum):
        STEER = 0

    class Params(NamedTuple):
        m: float  # Mass[kg]
        Iz: float  # Yaw inertia[kg * m ^ 2]
        lf: float  # Distance from CG to front axle[m]
        lr: float  # Distance from CG to rear axle[m]
        cf: float  # Front cornering stiffness[N / rad]
        cr: float  # Rear cornering stiffness[N / rad]

    def __init__(self):
        self.params = self.Params(m=1915, Iz=4235, lf=1.453, lr=1.522, cf=90000, cr=116000)
        self.vx = 10

        self.z = [0, 10, 0, 0, 0]

    def __repr__(self):
        return 'State[x={:.2f}, y={:.2f}, vy={:.2f}, theta={:.2f}, thetadot={:.2f}]'.format(*self.z)

    def integrate(self, u, dt):
        self.z = [self.z[idx] + dt * elem for idx, elem in enumerate(self.__zdot(self.z, u))]

    @property
    def vel(self):
        theta = self.z[self.StateIdx.THETA]
        return math.Point(self.vx * np.cos(theta) - self.z[self.StateIdx.VY] * np.sin(theta),
                          self.vx * np.sin(theta) + self.z[self.StateIdx.VY] * np.cos(theta))

    @property
    def pose(self):
        return math.Pose(self.z[self.StateIdx.X], self.z[self.StateIdx.Y], self.z[self.StateIdx.THETA])

    @property
    def pose_rear_axle(self):
        return math.add_body_frame(self.pose, math.Pose(-self.params.lr, 0, 0))

    @property
    def coord(self):
        return math.Point(self.z[self.StateIdx.X], self.z[self.StateIdx.Y])

    def __zdot(self, z, u):
        vy = z[self.StateIdx.VY]
        theta = z[self.StateIdx.THETA]
        thetadot = z[self.StateIdx.THETADOT]

        delta = u[self.ControlIdx.STEER]

        term1 = -self.params.cf * (np.arctan((vy + self.params.lf * thetadot) / self.vx) - delta) * np.cos(delta)
        term2 = self.params.cr * np.arctan((vy - self.params.lr * thetadot) / self.vx)
        vydot = (term1 - term2) / self.params.m - self.vx * thetadot
        thetadotdot = (self.params.lf * term1 + self.params.lr * term2) / self.params.Iz

        xdot = self.vx * np.cos(theta) - vy * np.sin(theta)
        ydot = vy * np.cos(theta) + self.vx * np.sin(theta)

        z_dot = [None] * len(self.StateIdx)
        z_dot[self.StateIdx.X] = xdot
        z_dot[self.StateIdx.Y] = ydot
        z_dot[self.StateIdx.VY] = vydot
        z_dot[self.StateIdx.THETA] = thetadot
        z_dot[self.StateIdx.THETADOT] = thetadotdot

        return z_dot
