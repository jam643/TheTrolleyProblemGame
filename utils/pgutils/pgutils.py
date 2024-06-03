from dataclasses import dataclass
import pygame
from typing import List, overload, Tuple, Union
from utils import math
import numpy as np
from functools import singledispatchmethod

# --- Globals ---
import utils.math

COLOR1 = (30, 60, 86)  # darkish blue
COLOR3 = (141, 105, 122)  # light/pale maroon
COLOR4 = (94, 88, 114)  # light/pale purple
COLOR6 = (153, 117, 119)  # lighter/paler maroon
COLOR7 = (255, 212, 163)  # light/pale, yellow
COLOR8 = (255, 236, 214)  # lighter/paler, yellow
COLOR9 = (184, 59, 94)  # maroon
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class SimToReal:
    @dataclass
    class Params:
        pxl_per_meter: float  # Pixels per meter conversion factor
        screen_ref_frame_rel_real: (
            math.Pose
        )  # Pose of the screen reference frame relative to the real-world reference frame
        fps: float  # Frames per second of the simulation
        sim_time_rel_real: float  # Simulation time relative to real-world time

    def __init__(self, params: Params):
        self.params = params
        self.time_s = 0.0

    @singledispatchmethod
    def get_sim_from_real(self, points) -> np.ndarray | math.Point:
        """
        Converts points in real-world reference frame to sim reference frame.
        """
        raise AttributeError

    @get_sim_from_real.register
    def _(self, vec: np.ndarray) -> np.ndarray:
        """
        Args:
            vec (np.ndarray): [3, N] The vector to be converted.

        Returns:
            np.ndarray: [3, N] The converted vector in simulation coordinates.
        """

        vec_rel_sim = math.rot_trans_3d(
            vec,
            angle_rad=-self.params.screen_ref_frame_rel_real.theta,
            dx=-self.params.screen_ref_frame_rel_real.x,
            dy=-self.params.screen_ref_frame_rel_real.y,
            rotate_first=False,
            scale_vec=self.params.pxl_per_meter,
            scale_trans=self.params.pxl_per_meter,
        )

        vec_rel_sim[1, :] = -vec_rel_sim[
            1, :
        ]  # Flip the y-axis to follow right-hand rule
        return vec_rel_sim

    @get_sim_from_real.register
    def _(self, pnt: math.Point) -> math.Point:
        """
        Args:
            pnt (math.Point): The real-world point to be converted.

        Returns:
            math.Point: The converted simulated point.
        """
        return math.Point(
            *(self.get_sim_from_real(np.vstack([pnt.x, pnt.y, 0]))[:2, :].flatten())
        )

    @get_sim_from_real.register
    def _(self, pose: math.Pose) -> math.Pose:
        """
        Args:
            pnt (math.Point): The real-world point to be converted.

        Returns:
            math.Point: The converted simulated point.
        """
        return math.Pose(
            *(self.get_sim_from_real(np.vstack([pose.x, pose.y, pose.theta])).flatten())
        )

    @singledispatchmethod
    def get_real_from_sim(self, points) -> np.ndarray | math.Point:
        """
        Converts points in sim reference frame to real-world reference frame.
        """
        raise AttributeError

    @get_real_from_sim.register
    def _(self, vec: np.ndarray) -> np.ndarray:
        """
        Args:
            vec (np.ndarray): [3, N] The vector to be converted.

        Returns:
            np.ndarray: [3, N] The converted vector in real-world coordinates.
        """
        vec[1, :] = -vec[1, :]  # Flip the y-axis to follow right-hand rule
        return math.rot_trans_3d(
            vec,
            angle_rad=self.params.screen_ref_frame_rel_real.theta,
            dx=self.params.screen_ref_frame_rel_real.x,
            dy=self.params.screen_ref_frame_rel_real.y,
            scale_vec=1 / self.params.pxl_per_meter,
            rotate_first=True,
        )

    @get_real_from_sim.register
    def _(self, pose: math.Pose) -> math.Pose:
        return math.Pose(
            *self.get_real_from_sim(np.vstack([pose.x, pose.y, pose.theta])).flatten()
        )

    @get_real_from_sim.register
    def _(self, pose: math.Point) -> math.Point:
        return math.Point(
            *self.get_real_from_sim(np.vstack([pose.x, pose.y, 0]))[:2, :].flatten()
        )

    @property
    def sim_dt(self) -> float:
        """
        Returns the time step for the simulation, calculated as the ratio of simulated time to frames per second.

        Returns:
            float: The time step for the simulation.
        """
        return self.params.sim_time_rel_real / self.params.fps

    def update(self):
        self.time_s += self.sim_dt


def draw_polygons(
    surf: pygame.Surface,
    polygon_list: List[np.ndarray],
    colors: List[pygame.Color],
    sim_to_real: SimToReal,
):
    """
    Draw polygons on a surface.

    Args:
        surf (pygame.Surface): The surface to draw the polygons on.
        polygon_list (List[np.ndarray]): A list of NumPy arrays representing the polygons.
        colors (List[pygame.Color]): A list of colors for each polygon.

    Returns:
        None
    """
    for idx, polygon in enumerate(polygon_list):
        polygon = [(p[0], p[1]) for p in polygon.T]
        pygame.draw.polygon(surf, colors[idx], polygon)
        pygame.draw.lines(
            surf, (0, 0, 0), True, polygon, int(sim_to_real.params.pxl_per_meter / 7)
        )
