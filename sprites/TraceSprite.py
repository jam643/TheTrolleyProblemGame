import pygame

from utils.pgutils import *


class TraceSprite(object):
    def __init__(self, glob_to_screen: GlobToScreen):
        super().__init__()
        self.glob_to_screen = glob_to_screen

        self.trace = []
        self.trace_max_T = 3

    def update(self, x, y, dt):
        self.trace.append(pygame.Vector2(x, y))
        if len(self.trace) > int(self.trace_max_T / dt):
            self.trace.pop(0)

    def draw(self, screen):
        if len(self.trace) > 1:
            pygame.draw.aalines(screen, COLOR8, False, self.glob_to_screen.get_pxl_from_glob(self.trace))
