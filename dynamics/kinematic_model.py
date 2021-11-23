import numpy as np
import enum
from typing import List

from dynamics.motion_model_base import MotionModel
from dynamics.Vehicle import Vehicle


class CartesianKinematicBicycleModel(MotionModel):
    class StateIdx(enum.IntEnum):
        X = 0
        Y = 1
        THETA = 2

    class CtrlIdx(enum.IntEnum):
        V = 0
        STEER = 1

    @staticmethod
    def _beta(lr, delta, wheel_base):
        return np.arctan(lr * np.tan(delta) / wheel_base)

    @staticmethod
    def _state_to_vehicle(z, u, p: Vehicle.Params) -> Vehicle.State:
        state_idx = CartesianKinematicBicycleModel.StateIdx
        ctrl_idx = CartesianKinematicBicycleModel.CtrlIdx
        beta = CartesianKinematicBicycleModel._beta(p.lr, u[ctrl_idx.STEER], p.wheel_base)
        return Vehicle.State(x=z[state_idx.X], y=z[state_idx.Y], theta=z[state_idx.THETA],
                                                     vx=u[ctrl_idx.V] * np.cos(beta),
                                                     vy=u[ctrl_idx.V] * np.sin(beta), delta=u[ctrl_idx.STEER],
                                                     thetadot=0.0)

    @staticmethod
    def _vehicle_to_state(vehicle_state_cog: Vehicle.State) -> List:
        state_idx = CartesianKinematicBicycleModel.StateIdx
        z = [0.0] * len(state_idx)
        z[state_idx.X] = vehicle_state_cog.x
        z[state_idx.Y] = vehicle_state_cog.y
        z[state_idx.THETA] = vehicle_state_cog.theta
        return z

    @staticmethod
    def _to_ctrl(steer, vel) -> List:
        ctrl_idx = CartesianKinematicBicycleModel.CtrlIdx
        u = [0.0] * len(ctrl_idx)
        u[ctrl_idx.STEER] = steer
        u[ctrl_idx.V] = vel
        return u

    @staticmethod
    def _eqn_of_motn(z: List, u: List, p: Vehicle.Params):
        state_idx = CartesianKinematicBicycleModel.StateIdx
        ctrl_idx = CartesianKinematicBicycleModel.CtrlIdx
        theta = z[state_idx.THETA]
        delta = u[ctrl_idx.STEER]
        vel = u[ctrl_idx.V]

        beta = CartesianKinematicBicycleModel._beta(p.lr, delta, p.wheel_base)
        x_dot = vel * np.cos(beta + theta)
        y_dot = vel * np.sin(beta + theta)
        thetadot = vel * np.tan(delta) * np.cos(beta) / p.wheel_base
        z_dot = [None] * len(state_idx)
        z_dot[state_idx.X] = x_dot
        z_dot[state_idx.Y] = y_dot
        z_dot[state_idx.THETA] = thetadot

        return z_dot
