import numpy as np
import scipy.interpolate as scipy_interpolate
import pygame
from typing import List, Tuple
from paths.PathBase import PathBase
from utils.math import Pose


class BSplinePath(PathBase):
    def __init__(self, points: List[pygame.Vector2], n_path_points: int,
                 degree: int = 3, smoothness: float = 0, coeff: int = 0):
        self.n_path_points = n_path_points
        self.degree = degree
        self.smoothness = smoothness
        self.coeff = coeff

        self.spline_list = None
        self.spline_station = None
        self.update(points)
        self.nearest_idx = 0

    def get_pose_at_station(self, station: float) -> Pose:
        for idx, spline_station in enumerate(self.spline_station):
            if station <= spline_station:
                break

        return self.spline_list[idx]

    def get_nearest_pose(self, point: pygame.Vector2) -> Tuple[Pose, float]:
        if not self.spline_list:
            return None, None
        # prev_dist = None
        # nearest_idx = 0
        dist = [np.sqrt((point.x - p.x) ** 2 + (point.y - p.y) ** 2) for p in self.spline_list]
        nearest_idx = np.argmin(dist)
        # for idx in range(self.nearest_idx, len(self.spline_list)):
        #     dist = np.sqrt((point.x - self.spline_list[idx].x) ** 2 + (point.y - self.spline_list[idx].y) ** 2)
        #     if prev_dist and (prev_dist < dist):
        #         nearest_idx = idx - 1
        #         break
        #     if idx == len(self.spline_list) - 1:
        #         nearest_idx = idx
        #     prev_dist = dist
        self.nearest_idx = nearest_idx
        return self.spline_list[self.nearest_idx], self.spline_station[self.nearest_idx]

    def __update_spline_list(self, points: List[pygame.Vector2]):
        self.spline_list = None
        if len(points) <= 1:
            return
        elif len(points) <= self.degree:
            self.spline_list = [Pose(p.x, p.y, 0) for p in points]
            return

        self.nearest_idx = 0
        x = [p.x for p in points]
        y = [p.y for p in points]
        t = range(len(x))
        x_tup = scipy_interpolate.splrep(t, x, k=self.degree, s=self.smoothness)
        y_tup = scipy_interpolate.splrep(t, y, k=self.degree, s=self.smoothness)

        x_list = list(x_tup)
        if self.coeff is not 0:
            x_list[1] = x + [0.0] * self.coeff

        y_list = list(y_tup)

        if self.coeff is not 0:
            y_list[1] = y + [0.0] * self.coeff

        ipl_t = np.linspace(0.0, len(x) - 1, self.n_path_points * (len(x) - 1))
        rx = scipy_interpolate.splev(ipl_t, x_list)
        ry = scipy_interpolate.splev(ipl_t, y_list)

        rtheta = np.arctan2(scipy_interpolate.splev(ipl_t, y_list, der=1), scipy_interpolate.splev(ipl_t, x_list, der=1))

        self.spline_list = [Pose(rx[idx], ry[idx], rtheta[idx]) for idx in range(len(rx))]

    def update(self, points: List[pygame.Vector2]):
        self.__update_spline_list(points)

        # update spline station
        if self.spline_list:
            self.spline_station = [0]*len(self.spline_list)
            for idx in range(1, len(self.spline_list)):
                dist = np.sqrt((self.spline_list[idx].x - self.spline_list[idx-1].x)**2 + (self.spline_list[idx].y - self.spline_list[idx-1].y)**2)
                self.spline_station[idx] = self.spline_station[idx - 1] + dist


    @property
    def path_points(self) -> List[pygame.Vector2]:
        if self.spline_list is None:
            return None
        return [pygame.Vector2(p.x, p.y) for p in self.spline_list]


def approximate_b_spline_path(x: list, y: list, n_path_points: int,
                              degree: int = 3, smoothness: float = 0, coeff: int = 0) -> tuple:
    """
    approximate points with a B-Spline path

    :param x: x position list of approximated points
    :param y: y position list of approximated points
    :param n_path_points: number of path points
    :param degree: (Optional) B Spline curve degree
    :return: x and y position list of the result path
    """
    t = range(len(x))
    x_tup = scipy_interpolate.splrep(t, x, k=degree, s=smoothness)
    y_tup = scipy_interpolate.splrep(t, y, k=degree, s=smoothness)

    x_list = list(x_tup)
    if coeff is not 0:
        x_list[1] = x + [0.0] * coeff

    y_list = list(y_tup)

    if coeff is not 0:
        y_list[1] = y + [0.0] * coeff

    ipl_t = np.linspace(0.0, len(x) - 1, n_path_points)
    rx = scipy_interpolate.splev(ipl_t, x_list)
    ry = scipy_interpolate.splev(ipl_t, y_list)

    return rx, ry


def interpolate_b_spline_path(x: list, y: list, n_path_points: int,
                              degree: int = 3) -> tuple:
    """
    interpolate points with a B-Spline path

    :param x: x positions of interpolated points
    :param y: y positions of interpolated points
    :param n_path_points: number of path points
    :param degree: B-Spline degree
    :return: x and y position list of the result path
    """
    ipl_t = np.linspace(0.0, len(x) - 1, len(x))
    spl_i_x = scipy_interpolate.make_interp_spline(ipl_t, x, k=degree)
    spl_i_y = scipy_interpolate.make_interp_spline(ipl_t, y, k=degree)

    travel = np.linspace(0.0, len(x) - 1, n_path_points)
    return spl_i_x(travel), spl_i_y(travel)


def main():
    import matplotlib.pyplot as plt
    print(__file__ + " start!!")
    # way points
    way_point_x = [-1.0, 3.0, 4.0, 2.0, 1.0]
    way_point_y = [0.0, -3.0, 1.0, 1.0, 3.0]
    n_course_point = 100  # sampling number

    rax, ray = approximate_b_spline_path(way_point_x, way_point_y,
                                         n_course_point)
    # rix, riy = interpolate_b_spline_path(way_point_x, way_point_y,
    #                                      n_course_point)

    # show results
    plt.plot(way_point_x, way_point_y, '--og', label="way points")

    rax, ray = approximate_b_spline_path(way_point_x, way_point_y,
                                         n_course_point, 3)
    plt.plot(rax, ray, label="Approximated B-Spline path1")

    rax, ray = approximate_b_spline_path(way_point_x, way_point_y,
                                         n_course_point, 3, 1)
    plt.plot(rax, ray, label="Approximated B-Spline path2")

    rax, ray = approximate_b_spline_path(way_point_x, way_point_y,
                                         n_course_point, 3, 2)
    plt.plot(rax, ray, label="Approximated B-Spline path3")

    rax, ray = approximate_b_spline_path(way_point_x, way_point_y,
                                         n_course_point, 3, 0, 4)
    plt.plot(rax, ray, label="Approximated B-Spline path4")

    rax, ray = approximate_b_spline_path(way_point_x, way_point_y,
                                         n_course_point, 3, 1, 1)
    plt.plot(rax, ray, label="Approximated B-Spline path5")

    # plt.plot(rix, riy, '-b', label="Interpolated B-Spline path")
    plt.grid(True)
    plt.legend()
    plt.axis("equal")
    plt.show()


if __name__ == '__main__':
    main()
