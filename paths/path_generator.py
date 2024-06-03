from abc import ABC, abstractmethod
import pygame
import numpy as np
from dataclasses import dataclass
from utils.pgutils.pgutils import SimToReal
from utils.math import Point

from paths.PathBase import PathBase


class PathGeneratorBase(ABC):
    @abstractmethod
    def update(self, path: PathBase, time_s: float) -> PathBase: ...

    @abstractmethod
    def set_params(self, params): ...


class PathManualGenerator(PathGeneratorBase):
    @dataclass
    class Params:
        max_path_length: int = 16
        update_rate_s: float = 0.2

    def __init__(self, params: Params, sim_to_real: SimToReal):
        self.sim_to_real = sim_to_real
        self._params = params

        self.path_point_list = []
        self.spline_timer = 0
        self.mouse_position = None

    def update(self, path: PathBase, time_s: float) -> PathBase:
        # todo clean up logic

        self.mouse_position = Point(*pygame.mouse.get_pos())
        if self.spline_timer > self._params.update_rate_s:
            self.path_point_list.append(
                self.sim_to_real.get_real_from_sim(self.mouse_position).to_vect2()
            )
            self.spline_timer = 0
        else:
            self.spline_timer += self.sim_to_real.sim_dt
        try:
            path.update(
                self.path_point_list
                + [self.sim_to_real.get_real_from_sim(self.mouse_position).to_vect2()]
            )
            if len(self.path_point_list) > self._params.max_path_length:
                self.path_point_list.pop(0)
        except:
            pass
        return path

    def set_params(self, params):
        self._params = params


class PathAutoGenerator(PathGeneratorBase):
    @dataclass
    class Params:
        max_path_length: int = 13
        sin_period: float = 4.0
        sin_height: float = 0.4
        update_rate_s: float = 0.2

    def __init__(
        self,
        params: Params,
        sim_to_real: SimToReal,
        screen_width: float,
        screen_height: float,
    ):
        self.sim_to_real = sim_to_real

        self.path_point_list = []
        self.spline_timer = 0
        self._params = params
        self.screen_height = screen_height
        self.create_spline_x = 0.9 * screen_width
        self.create_spline_y = 0.5 * screen_height

    def update(self, path: PathBase, time_s: float) -> PathBase:
        y_offset = (
            (self._params.sin_height / 2.0)
            * self.screen_height
            * np.cos(time_s * 2 * np.pi / self._params.sin_period)
        )
        latest_point = Point(self.create_spline_x, self.create_spline_y + y_offset)

        # append new point to path_point_list at update_rate_s
        if (time_s - self.spline_timer) > self._params.update_rate_s:
            self.path_point_list.append(
                self.sim_to_real.get_real_from_sim(latest_point).to_vect2()
            )
            self.spline_timer = time_s

        # update path with latest point for smoother animationß
        path.update(
            self.path_point_list
            + [self.sim_to_real.get_real_from_sim(latest_point).to_vect2()]
        )
        if len(self.path_point_list) > self._params.max_path_length:
            self.path_point_list.pop(0)

        return path

    def set_params(self, params):
        self._params = params
