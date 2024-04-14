import numpy as np
from scipy import integrate
import enum
from abc import ABC, abstractmethod
from typing import List, Callable

from dynamics.Vehicle import Vehicle


class MotionModel(ABC):
    class IntScheme(enum.Enum):
        EULER = 0
        RK4 = 1

    def __init__(self, int_scheme=IntScheme.RK4):
        self._int_scheme = int_scheme
        self._int_scheme_map = {self.IntScheme.EULER: self._integrate_euler, self.IntScheme.RK4: self._integrate_rk4}

    def update(self, vehicle_state: Vehicle, steer_rate, steer_desired, vel, dt) -> Vehicle:
        u = self._to_ctrl(steer_rate, vel)
        z = self._vehicle_to_state(vehicle_state.state_cog)
        z_new = self._int_scheme_map[self._int_scheme](self._eqn_of_motn, z, u, vehicle_state.params, dt)

        vehicle_state_new = Vehicle(state_cog=self._state_to_vehicle(z_new, u, vehicle_state.params),
                                    params=vehicle_state.params)
        delta = vehicle_state_new.state_cog.delta
        vehicle_state_new.state_cog.delta = np.clip(delta, -vehicle_state.params.delta_max, vehicle_state.params.delta_max)
        return vehicle_state_new

    @staticmethod
    def _integrate_euler(eqn_of_mtn: Callable, z: List, u: List, p: Vehicle.Params, dt: float):
        return [z[idx] + dt * elem for idx, elem in enumerate(eqn_of_mtn(z, u, p))]

    @staticmethod
    def _integrate_rk4(eqn_of_mtn: Callable, z: List, u, p: Vehicle.Params, dt: float):
        soln = integrate.solve_ivp(lambda _, _z: eqn_of_mtn(_z, u, p), [0, dt], z, method='RK45')
        return soln.y[:, -1]

    @staticmethod
    @abstractmethod
    def _eqn_of_motn(z, u, p):
        pass

    @staticmethod
    @abstractmethod
    def _vehicle_to_state(vehicle_state: Vehicle.State) -> List:
        pass

    @staticmethod
    @abstractmethod
    def _state_to_vehicle(z, u, p) -> Vehicle.State:
        pass

    @staticmethod
    @abstractmethod
    def _to_ctrl(steer, vel) -> List:
        pass
