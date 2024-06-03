import pygame

from utils.pgutils.pgutils import *


class TraceSprite(object):
    def __init__(self, sim_to_real: SimToReal):
        super().__init__()
        self.sim_to_real = sim_to_real

        self.trace = []
        self.trace_max_T = 3

    def update(self, x, y, dt):
        self.trace.append(pygame.Vector2(x, y))
        if len(self.trace) > int(self.trace_max_T / dt):
            self.trace.pop(0)

    def draw(self, screen):
        if len(self.trace) > 1:
            pygame.draw.aalines(
                screen,
                COLOR8,
                False,
                [self.sim_to_real.get_sim_from_real(t) for t in self.trace],
            )
