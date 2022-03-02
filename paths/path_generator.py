from abc import ABC, abstractmethod
import pygame
import numpy as np
from dataclasses import dataclass
from utils.pgutils.pgutils import GlobToScreen

from paths.PathBase import PathBase


class PathGeneratorBase(ABC):
    @abstractmethod
    def update(self, path: PathBase, time_s: float) -> PathBase:
        ...

    @abstractmethod
    def set_params(self, params):
        ...


class PathManualGenerator(PathGeneratorBase):
    @dataclass
    class Params:
        max_path_length: int = 13
        update_rate_s: float = 0.2

    def __init__(self, params: Params, glob_to_screen: GlobToScreen):
        self.glob_to_screen = glob_to_screen
        self._params = params

        self.last_pose = []
        self.spline_timer = 0
        self.mouse_position = None

    def update(self, path: PathBase, time_s: float) -> PathBase:
        # todo clean up logic

        self.mouse_position = pygame.Vector2(pygame.mouse.get_pos())
        if (time_s - self.spline_timer) > self._params.update_rate_s:
            self.last_pose.append(self.glob_to_screen.get_glob_from_pxl(pygame.Vector2(self.mouse_position)))
            self.spline_timer = time_s
        try:
            path.update(self.last_pose + [self.glob_to_screen.get_glob_from_pxl(self.mouse_position)])
            if len(self.last_pose) > self._params.max_path_length:
                self.last_pose.pop(0)
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

    def __init__(self, params: Params, glob_to_screen: GlobToScreen, screen_width: float, screen_height: float):
        self.glob_to_screen = glob_to_screen

        self.last_pose = []
        self.spline_timer = 0
        self._params = params
        self.screen_height = screen_height
        self.create_spline_x = 0.9 * screen_width
        self.create_spline_y = 0.5 * screen_height

    def update(self, path: PathBase, time_s: float) -> PathBase:
        spline_sin = (self._params.sin_height / 2.) * self.screen_height * np.cos(
            time_s * 2 * np.pi / self._params.sin_period)
        if (time_s - self.spline_timer) > self._params.update_rate_s:
            self.last_pose.append(
                self.glob_to_screen.get_glob_from_pxl(
                    pygame.Vector2(self.create_spline_x, self.create_spline_y + spline_sin)))
            self.spline_timer = time_s
        try:
            path.update(self.last_pose + [
                self.glob_to_screen.get_glob_from_pxl(
                    pygame.Vector2(self.create_spline_x, self.create_spline_y + spline_sin))])
            if len(self.last_pose) > self._params.max_path_length:
                self.last_pose.pop(0)
        except:
            pass
        return path

    def set_params(self, params):
        self._params = params
