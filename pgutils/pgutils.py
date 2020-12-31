from dataclasses import dataclass
import pygame
import numpy as np

# --- Globals ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

SCREEN_WIDTH = 1800
SCREEN_HEIGHT = 1000


@dataclass
class GlobToScreen:
    pxl_per_mtr: float
    x_pxl_rel_glob: float
    y_pxl_rel_glob: float

    fps: int
    play_speed: float

    def get_pxl_from_glob(self, point):
        return point[0] * self.pxl_per_mtr + self.x_pxl_rel_glob, -point[1] * self.pxl_per_mtr + self.y_pxl_rel_glob

    def get_pxl_from_glob(self, x, y):
        return x * self.pxl_per_mtr + self.x_pxl_rel_glob, -y * self.pxl_per_mtr + self.y_pxl_rel_glob

    @property
    def sim_dt(self):
        return self.play_speed / self.fps


def rot_and_transl(surf: pygame.Surface, image: pygame.Surface, angle: float, x: float, y: float) -> pygame.Surface:
    image_rot = pygame.transform.rotate(image, angle * 180 / np.pi)
    surf.blit(image_rot, (
        -image_rot.get_rect().centerx + surf.get_rect().centerx + x,
        -image_rot.get_rect().centery + surf.get_rect().centery + y))
    return surf