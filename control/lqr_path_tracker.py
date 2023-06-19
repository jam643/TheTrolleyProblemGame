import time
import scipy.linalg as la
import math
import numpy as np
from dataclasses import dataclass
from functools import lru_cache

from control.ControllerBase import ControllerBase
from paths.PathBase import PathBase
from paths import path_utils
from dynamics.Vehicle import Vehicle
from dynamics.kinematic_model import CartesianKinematicBicycleModel
from dynamics.CartesianDynamicBicycleModel import CartesianDynamicBicycleModel
from utils import math


def pi_2_pi(angle):
    return (angle + np.pi) % (2 * np.pi) - np.pi


def solve_DARE(A, B, Q, R):
    """
    solve a discrete time_Algebraic Riccati equation (DARE)
    """

    X = Q
    maxiter = 150
    eps = 0.01

    iter = 0
    for i in range(maxiter):
        iter += 1
        Xn = A.T @ X @ A - A.T @ X @ B @ \
             la.inv(R + B.T @ X @ B) @ B.T @ X @ A + Q
        if (abs(Xn - X)).max() < eps:
            break
        X = Xn

    print("iter: {}".format(iter))
    np.set_printoptions(suppress=True)
    return Xn


@lru_cache
def dlqr(A, B, Q, R):
    """Solve the discrete time lqr controller.
    x[k+1] = A x[k] + B u[k]
    cost = sum x[k].T*Q*x[k] + u[k].T*R*u[k]
    # ref Bertsekas, p.151
    """

    A = np.array(A)
    B = np.array(B)
    Q = np.array(Q)
    R = np.array(R)

    # first, try to solve the ricatti equation
    X = solve_DARE(A, B, Q, R)
    # X1 = la.solve_discrete_are(A, B, Q, R)
    # print(X - X1)

    # compute the LQR gain
    K = la.inv(B.T @ X @ B + R) @ (B.T @ X @ A)

    # TODO time this
    # eigVals, eigVecs = la.eig(A - B @ K)

    return K, X


def lqr(A, B, Q, R):
    X = la.solve_continuous_are(A, B, Q, R)


def arr_to_tuple_2d(X):
    return tuple(tuple(x) for x in X)


class DiscreteLQRPathTracker(ControllerBase):
    @dataclass
    class Params:
        Q: np.ndarray
        R: np.ndarray
        dt: float

        def __post_init__(self):
            # TODO add checks
            assert np.all(np.linalg.eigvals(self.Q) > 0)

    def __init__(self, params: Params):
        self.set_params(params)

        self.delta = 0.0
        self.nearest_pose = None
        self.path = None
        self.car = None
        self.cte = None
        self.curv_ref = None
        self.solvetime_ms = None

    def set_params(self, params: Params):
        self.params = params

    def update(self, car: Vehicle, path: PathBase) -> float:
        start_time_ms = time.time_ns() * 1e-6
        self.car_ref_pnt = car.pose_rear_axle.point
        self.nearest_pose, station = path.get_nearest_pose(self.car_ref_pnt)
        self.car = car
        self.path = path

        if not self.nearest_pose:
            return self.delta

        self.path_unit_normal = path_utils.get_path_unit_norm(self.nearest_pose)
        self.cte = path_utils.get_cross_err(self.nearest_pose, self.car_ref_pnt)

        self.car_vel = car.vel_at_pnt(math.Point(-car.params.lr, 0))
        self.cte_dot = math.dot(self.car_vel, self.path_unit_normal)

        self.theta_e = pi_2_pi(car.pose.theta - self.nearest_pose.theta)

        self.curv_ref = path.get_curv_at_station(station)
        if np.isnan(self.curv_ref):
            self.curv_ref = 0

        vel = math.norm(self.car_vel)

        beta = CartesianKinematicBicycleModel.beta(self.car.params.lr, self.car.state_cog.delta,
                                                   self.car.params.wheel_base)
        car_theta_dot = vel * np.tan(self.car.state_cog.delta) * np.cos(beta) / self.car.params.wheel_base  # vel*radius
        self.theta_e_dot = car_theta_dot - self.curv_ref * math.dot(self.car_vel, math.unit_vec2(
            self.nearest_pose.theta))  # TODO curv dot vel

        A = np.zeros((4, 4))
        A[0, 0] = 1.0
        A[0, 1] = self.params.dt
        A[1, 2] = np.round(vel)
        A[2, 2] = 1.0
        A[2, 3] = self.params.dt

        B = np.zeros((4, 1))
        B[3, 0] = np.round(vel) / car.params.wheel_base

        K, _ = dlqr(arr_to_tuple_2d(A), arr_to_tuple_2d(B), arr_to_tuple_2d(self.params.Q),
                    arr_to_tuple_2d(self.params.R))

        x = np.zeros((4, 1))

        x[0, 0] = self.cte
        x[1, 0] = self.cte_dot
        x[2, 0] = self.theta_e
        x[3, 0] = self.theta_e_dot

        ff = np.arctan2(car.params.wheel_base * self.curv_ref, 1)
        fb = pi_2_pi((-K @ x)[0, 0])

        self.delta = ff + fb

        self.solvetime_ms = time.time_ns() * 1e-6 - start_time_ms
        return self.delta


class DynamicLQRPathTracker(ControllerBase):
    @dataclass
    class Params:
        Q: np.ndarray
        R: np.ndarray
        dt: float

        def __post_init__(self):
            # TODO add checks
            assert np.all(np.linalg.eigvals(self.Q) > 0)

    def __init__(self, params: Params):
        self.set_params(params)

        self.delta = 0.0
        self.nearest_pose = None
        self.path = None
        self.car = None
        self.cte = None
        self.curv_ref = None
        self.solvetime_ms = None

    def set_params(self, params: Params):
        self.params = params

    def update(self, car: Vehicle, path: PathBase) -> float:
        start_time_ms = time.time_ns() * 1e-6
        self.car_ref_pnt = car.pose.point
        self.nearest_pose, station = path.get_nearest_pose(self.car_ref_pnt)
        self.car = car
        self.path = path

        if not self.nearest_pose:
            return self.delta

        self.path_unit_normal = path_utils.get_path_unit_norm(self.nearest_pose)
        self.cte = path_utils.get_cross_err(self.nearest_pose, self.car_ref_pnt)
        self.theta_e = pi_2_pi(car.pose.theta - self.nearest_pose.theta)

        self.car_vel = car.vel_cog
        self.cte_dot = math.dot(self.car_vel, self.path_unit_normal)

        self.curv_ref = path.get_curv_at_station(station)
        if np.isnan(self.curv_ref):
            self.curv_ref = 0

        vel = math.norm(self.car_vel)

        thetadot_ref = self.curv_ref * math.dot(self.car_vel, math.unit_vec2(self.nearest_pose.theta))
        self.theta_e_dot = car.state_cog.thetadot - thetadot_ref

        A = np.zeros((4, 4))
        A[0, 1] = 1.0
        A[0, 1] = self.params.dt
        A[1, 2] = np.round(vel)
        A[2, 2] = 1.0
        A[2, 3] = self.params.dt

        B = np.zeros((4, 1))
        B[3, 0] = np.round(vel) / car.params.wheel_base

        K, _ = dlqr(arr_to_tuple_2d(A), arr_to_tuple_2d(B), arr_to_tuple_2d(self.params.Q),
                    arr_to_tuple_2d(self.params.R))

        x = np.zeros((4, 1))

        x[0, 0] = self.cte
        x[1, 0] = self.cte_dot
        x[2, 0] = self.theta_e
        x[3, 0] = self.theta_e_dot

        ff = np.arctan2(car.params.wheel_base * self.curv_ref, 1)
        fb = pi_2_pi((-K @ x)[0, 0])

        self.delta = ff + fb

        self.solvetime_ms = time.time_ns() * 1e-6 - start_time_ms
        return self.delta
