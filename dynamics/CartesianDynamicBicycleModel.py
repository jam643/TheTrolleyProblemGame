import numpy as np
import enum
from typing import List, Callable

from dynamics.Vehicle import Vehicle
from dynamics.motion_model_base import MotionModel


class CartesianDynamicBicycleModel(MotionModel):
    class StateIdx(enum.IntEnum):
        X = 0
        Y = 1
        VY = 2
        THETA = 3
        THETADOT = 4

    class CtrlIdx(enum.IntEnum):
        VX = 0
        STEER = 1

    @staticmethod
    def _state_to_vehicle(z, u, _) -> Vehicle.State:
        state_idx = CartesianDynamicBicycleModel.StateIdx
        ctrl_idx = CartesianDynamicBicycleModel.CtrlIdx
        return Vehicle.State(x=z[state_idx.X], y=z[state_idx.Y], theta=z[state_idx.THETA],
                             vx=u[ctrl_idx.VX],
                             vy=z[state_idx.VY], delta=u[ctrl_idx.STEER],
                             thetadot=z[state_idx.THETADOT])

    @staticmethod
    def _vehicle_to_state(vehicle_state_cog: Vehicle.State) -> List:
        state_idx = CartesianDynamicBicycleModel.StateIdx
        z = [0.0] * len(state_idx)
        z[state_idx.X] = vehicle_state_cog.x
        z[state_idx.Y] = vehicle_state_cog.y
        z[state_idx.VY] = vehicle_state_cog.vy
        z[state_idx.THETA] = vehicle_state_cog.theta
        z[state_idx.THETADOT] = vehicle_state_cog.thetadot
        return z

    @staticmethod
    def _to_ctrl(steer, vel) -> List:
        ctrl_idx = CartesianDynamicBicycleModel.CtrlIdx
        u = [0.0] * len(ctrl_idx)
        u[ctrl_idx.STEER] = steer
        u[ctrl_idx.VX] = vel
        return u

    @staticmethod
    def lat_force_front_tire(cf, vy, vx, thetadot, lf, delta):
        return cf * (delta - np.arctan((vy + thetadot * lf) / vx))

    @staticmethod
    def lat_force_rear_tire(cr, vy, vx, thetadot, lr):
        return -cr * np.arctan((vy - thetadot * lr) / vx)

    @staticmethod
    def _eqn_of_motn(z: List, u: List, p: Vehicle.Params):
        state_idx = CartesianDynamicBicycleModel.StateIdx
        ctrl_idx = CartesianDynamicBicycleModel.CtrlIdx

        # unpack state
        vy = z[state_idx.VY]
        theta = z[state_idx.THETA]
        thetadot = z[state_idx.THETADOT]

        # unpack control
        vx = u[ctrl_idx.VX]
        delta = u[ctrl_idx.STEER]

        # lateral tire forces assuming linear tire model
        force_yf = CartesianDynamicBicycleModel.lat_force_front_tire(p.cf, vy, vx, thetadot, p.lf, delta)
        force_yr = CartesianDynamicBicycleModel.lat_force_rear_tire(p.cr, vy, vx, thetadot, p.lr)

        vydot = (force_yr + force_yf*np.cos(delta)) / p.m - vx * thetadot
        thetadotdot = (p.lf * force_yf * np.cos(delta) - p.lr * force_yr) / p.Iz

        xdot = vx * np.cos(theta) - vy * np.sin(theta)
        ydot = vy * np.cos(theta) + vx * np.sin(theta)

        z_dot = [None] * len(state_idx)
        z_dot[state_idx.X] = xdot
        z_dot[state_idx.Y] = ydot
        z_dot[state_idx.VY] = vydot
        z_dot[state_idx.THETA] = thetadot
        z_dot[state_idx.THETADOT] = thetadotdot

        return z_dot
