from dataclasses import dataclass
import pygame
from pygame import gfxdraw
import numpy as np
from typing import List, overload, Tuple, Union
from multipledispatch import dispatch
from utils import math

# --- Globals ---
import utils.math

COLOR1 = (30, 60, 86)
COLOR3 = (141, 105, 122)
COLOR4 = (94, 88, 114)
COLOR6 = (153, 117, 119)
COLOR7 = (255, 212, 163)
COLOR8 = (255, 236, 214)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


@dataclass
class GlobToScreen:
    pxl_per_mtr: float
    x_pxl_rel_glob: float
    y_pxl_rel_glob: float

    fps: int
    play_speed: float

    @overload
    def get_pxl_from_glob(self, points: pygame.Vector2) -> pygame.Vector2:
        ...

    @overload
    def get_pxl_from_glob(self, points: List[pygame.Vector2]) -> List[pygame.Vector2]:
        ...

    def get_pxl_from_glob(self, points):
        if type(points) is list:
            return [pygame.Vector2(point.x * self.pxl_per_mtr + self.x_pxl_rel_glob,
                                   -point.y * self.pxl_per_mtr + self.y_pxl_rel_glob) for point in points]
        elif type(points) is utils.math.Point:
            return pygame.Vector2(points.x * self.pxl_per_mtr + self.x_pxl_rel_glob,
                                  -points.y * self.pxl_per_mtr + self.y_pxl_rel_glob)
        elif type(points) is pygame.Vector2:
            return pygame.Vector2(points.x * self.pxl_per_mtr + self.x_pxl_rel_glob,
                                  -points.y * self.pxl_per_mtr + self.y_pxl_rel_glob)
        else:
            raise AttributeError

    # @overload
    # def get_glob_from_pxl(self, points: pygame.Vector2) -> pygame.Vector2:
    #     ...
    #
    # @overload
    # def get_glob_from_pxl(self, points: List[pygame.Vector2]) -> List[pygame.Vector2]:
    #     ...

    def get_glob_from_pxl(self, points):
        if type(points) is list:
            return [pygame.Vector2((point.x - self.x_pxl_rel_glob) / self.pxl_per_mtr,
                                   (self.y_pxl_rel_glob - point.y) / self.pxl_per_mtr) for point in points]
        elif type(points) is pygame.Vector2:
            return pygame.Vector2((points.x - self.x_pxl_rel_glob) / self.pxl_per_mtr,
                                  (self.y_pxl_rel_glob - points.y) / self.pxl_per_mtr)
        else:
            raise AttributeError

    def get_pose_glob_from_pxl(self, poses: Union[List[math.Pose], math.Pose]):
        if type(poses) is list:
            return [math.Pose((pose.x - self.x_pxl_rel_glob) / self.pxl_per_mtr,
                                   (self.y_pxl_rel_glob - pose.y) / self.pxl_per_mtr, -pose.theta) for pose in poses]
        elif type(poses) is math.Pose:
            return math.Pose((poses.x - self.x_pxl_rel_glob) / self.pxl_per_mtr,
                                  (self.y_pxl_rel_glob - poses.y) / self.pxl_per_mtr, -poses.theta)
        else:
            raise AttributeError

    @property
    def sim_dt(self):
        return self.play_speed / self.fps


def draw_polygons(surf: pygame.Surface, polygon_list: List[List[Tuple[float, float]]], colors: List[pygame.Color],
                  glob_to_screen: GlobToScreen):
    centerx = surf.get_rect().centerx
    centery = surf.get_rect().centery
    for idx, poly in enumerate(polygon_list):
        poly_transf = [(p[0] * glob_to_screen.pxl_per_mtr + centerx,
          p[1] * glob_to_screen.pxl_per_mtr + centery) for p in poly]
        pygame.draw.polygon(surf, colors[idx], poly_transf)
        pygame.draw.lines(surf, (0,0,0), True, poly_transf, int(glob_to_screen.pxl_per_mtr / 7))