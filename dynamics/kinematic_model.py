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
        DELTA = 3

    class CtrlIdx(enum.IntEnum):
        V = 0
        DELTA_RATE = 1

    @staticmethod
    def beta(lr, delta, wheel_base):
        return np.arctan(lr * np.tan(delta) / wheel_base)

    @staticmethod
    def _state_to_vehicle(z, u, p: Vehicle.Params) -> Vehicle.State:
        state_idx = CartesianKinematicBicycleModel.StateIdx
        ctrl_idx = CartesianKinematicBicycleModel.CtrlIdx
        beta = CartesianKinematicBicycleModel.beta(p.lr, z[state_idx.DELTA], p.wheel_base)
        return Vehicle.State(x=z[state_idx.X], y=z[state_idx.Y], theta=z[state_idx.THETA],
                                                     vx=u[ctrl_idx.V] * np.cos(beta),
                                                     vy=u[ctrl_idx.V] * np.sin(beta), delta=z[state_idx.DELTA],
                                                     thetadot=0.0, delta_rate=u[ctrl_idx.DELTA_RATE])

    @staticmethod
    def _vehicle_to_state(vehicle_state_cog: Vehicle.State) -> List:
        state_idx = CartesianKinematicBicycleModel.StateIdx
        z = [0.0] * len(state_idx)
        z[state_idx.X] = vehicle_state_cog.x
        z[state_idx.Y] = vehicle_state_cog.y
        z[state_idx.THETA] = vehicle_state_cog.theta
        z[state_idx.DELTA] = vehicle_state_cog.delta
        return z

    @staticmethod
    def _to_ctrl(steer_rate, vel) -> List:
        ctrl_idx = CartesianKinematicBicycleModel.CtrlIdx
        u = [0.0] * len(ctrl_idx)
        u[ctrl_idx.DELTA_RATE] = steer_rate
        u[ctrl_idx.V] = vel
        return u

    @staticmethod
    def _eqn_of_motn(z: List, u: List, p: Vehicle.Params):
        state_idx = CartesianKinematicBicycleModel.StateIdx
        ctrl_idx = CartesianKinematicBicycleModel.CtrlIdx
        theta = z[state_idx.THETA]
        delta = z[state_idx.DELTA]
        vel = u[ctrl_idx.V]

        beta = CartesianKinematicBicycleModel.beta(p.lr, delta, p.wheel_base)
        x_dot = vel * np.cos(beta + theta)
        y_dot = vel * np.sin(beta + theta)
        thetadot = vel * np.tan(delta) * np.cos(beta) / p.wheel_base
        z_dot = [None] * len(state_idx)
        z_dot[state_idx.X] = x_dot
        z_dot[state_idx.Y] = y_dot
        z_dot[state_idx.THETA] = thetadot
        z_dot[state_idx.DELTA] = u[ctrl_idx.DELTA_RATE]

        return z_dot
