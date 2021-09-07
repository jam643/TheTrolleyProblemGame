from dataclasses import dataclass
import pygame
import numpy as np
from typing import List, overload
from multipledispatch import dispatch

# --- Globals ---
import utils.math

COLOR1 = (20, 50, 76)
COLOR3 = (141, 105, 122)
COLOR4 = (84, 78, 104)
COLOR7 = (255, 212, 163)
COLOR8 = (255, 236, 214)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

SCREEN_WIDTH = 1800
SCREEN_HEIGHT = 1000


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

    @overload
    def get_glob_from_pxl(self, points: pygame.Vector2) -> pygame.Vector2:
        ...

    @overload
    def get_glob_from_pxl(self, points: List[pygame.Vector2]) -> List[pygame.Vector2]:
        ...

    def get_glob_from_pxl(self, points):
        if type(points) is list:
            return [pygame.Vector2((point.x - self.x_pxl_rel_glob) / self.pxl_per_mtr,
                                   (self.y_pxl_rel_glob - point.y) / self.pxl_per_mtr) for point in points]
        elif type(points) is pygame.Vector2:
            return pygame.Vector2((points.x - self.x_pxl_rel_glob) / self.pxl_per_mtr,
                                  (self.y_pxl_rel_glob - points.y) / self.pxl_per_mtr)
        else:
            raise AttributeError

    @property
    def sim_dt(self):
        return self.play_speed / self.fps


def rot_and_transl(surf: pygame.Surface, image: pygame.Surface, angle: float, x: float, y: float,
                   special_flags=0) -> pygame.Surface:
    # image_rot = pygame.transform.rotate(image, angle * 180 / np.pi)
    image_rot = image
    surf.blit(image_rot, (
        -image_rot.get_rect().centerx + surf.get_rect().centerx + x,
        -image_rot.get_rect().centery + surf.get_rect().centery + y), special_flags=special_flags)
    return surf
