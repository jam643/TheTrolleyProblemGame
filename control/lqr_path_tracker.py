"""

Path tracking simulation with LQR steering control and PID speed control.

author Atsushi Sakai (@Atsushi_twi)

"""
import scipy.linalg as la
import math
import numpy as np
from dataclasses import dataclass

from control.ControllerBase import ControllerBase
from paths.PathBase import PathBase
from dynamics.Vehicle import Vehicle
from utils import math


def pi_2_pi(angle):
    return (angle + np.pi) % (2 * np.pi) - np.pi


def solve_DARE(A, B, Q, R):
    """
    solve a discrete time_Algebraic Riccati equation (DARE)
    """
    X = Q
    maxiter = 150
    eps = 0.1

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
    print(Xn)
    return Xn


def dlqr(A, B, Q, R):
    """Solve the discrete time lqr controller.
    x[k+1] = A x[k] + B u[k]
    cost = sum x[k].T*Q*x[k] + u[k].T*R*u[k]
    # ref Bertsekas, p.151
    """

    # first, try to solve the ricatti equation
    X = solve_DARE(A, B, Q, R)

    # compute the LQR gain
    K = la.inv(B.T @ X @ B + R) @ (B.T @ X @ A)

    eigVals, eigVecs = la.eig(A - B @ K)

    return K, X, eigVals


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

    def set_params(self, params: Params):
        self.params = params

    def draw(self, screen):
        # TODO delete
        pass

    def update(self, car: Vehicle, path: PathBase) -> float:
        nearest_pose, station = path.get_nearest_pose(car.pose_rear_axle.get_point)

        if not nearest_pose:
            return self.delta

        path_unit_normal = math.unit_vec2(nearest_pose.theta + np.pi / 2)
        cte = math.dot(math.diff(car.pose, nearest_pose), path_unit_normal)

        theta_e = pi_2_pi(car.pose.theta - nearest_pose.theta)

        curv_ref = path.get_curv_at_station(station)

        v = car.vel_cog_mag

        A = np.zeros((4, 4))
        A[0, 0] = 1.0
        A[0, 1] = self.params.dt
        A[1, 2] = v
        A[2, 2] = 1.0
        A[2, 3] = self.params.dt

        B = np.zeros((4, 1))
        B[3, 0] = v / car.params.wheel_base

        K, _, _ = dlqr(A, B, self.params.Q, self.params.R)

        x = np.zeros((4, 1))

        x[0, 0] = cte
        x[1, 0] = 0.0
        x[2, 0] = theta_e
        x[3, 0] = 0.0

        ff = np.arctan2(car.params.wheel_base * curv_ref, 1)
        fb = pi_2_pi((-K @ x)[0, 0])

        self.delta = ff + fb

        return self.delta

