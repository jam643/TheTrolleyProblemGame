import numpy as np
from abc import ABC, abstractmethod
from typing import Callable
from scipy.signal import chirp

from utils.pgutils.pgutils import GlobToScreen


class WallGenerator(ABC):
    def add_callback(self, callback: Callable, glob_to_screen: GlobToScreen):
        self.callback = callback
        self.glob_to_screen = glob_to_screen
        return self

    @abstractmethod
    def __call__(self):
        pass


class RandomWallGenerator(WallGenerator):
    def __init__(self, time_range, door_pose_range, door_height):
        self.counter = 0
        self.time_range = time_range
        self.door_pose_range = door_pose_range
        self.door_height = door_height
        self.time_to_gen = self._uniform(self.time_range[0], self.time_range[1])
        self.time_since_last_wall = 0

    def _uniform(self, start, end):
        np.random.seed(self.counter)
        self.counter += 1
        return np.random.uniform(start, end)

    def __call__(self):
        self.time_since_last_wall += self.glob_to_screen.sim_dt
        if self.time_since_last_wall >= self.time_to_gen:
            door_pose = self._uniform(self.door_pose_range[0], self.door_pose_range[1])
            self.callback(self.door_height, door_pose)
            self.time_to_gen = self._uniform(self.time_range[0], self.time_range[1])
            self.time_since_last_wall = 0


class SinWallGenerator(WallGenerator):
    def __init__(self, gen_time, sin_period, amplitude, door_height):
        self.counter = 0
        self.gen_time = gen_time
        self.sin_period = sin_period
        self.amplitude = amplitude
        self.door_height = door_height
        self.time_since_last_wall = gen_time

    def __call__(self):
        self.time_since_last_wall += self.glob_to_screen.sim_dt
        if self.time_since_last_wall >= self.gen_time:
            door_pose = (self.amplitude * np.sin(2 * np.pi / self.sin_period * self.glob_to_screen.time_s) + 1) / 2
            self.callback(self.door_height, door_pose)
            self.time_since_last_wall = 0


class ChirpWallGenerator(WallGenerator):
    def __init__(self, gen_time, period_start, period_end, t_end, amplitude, door_height):
        self.counter = 0
        self.gen_time = gen_time
        self.period_start = period_start
        self.period_end = period_end
        self.t_end = t_end
        self.amplitude = amplitude
        self.door_height = door_height
        self.time_since_last_wall = gen_time

    def __call__(self):
        self.time_since_last_wall += self.glob_to_screen.sim_dt
        if self.time_since_last_wall >= self.gen_time:
            door_pose = (self.amplitude * chirp(self.glob_to_screen.time_s, 1 / self.period_start, self.t_end,
                                                1 / self.period_end) + 1) / 2
            self.callback(self.door_height, door_pose)
            self.time_since_last_wall = 0
