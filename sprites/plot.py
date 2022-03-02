import pygame
import numpy as np

import utils.pgutils.pgutils as utils
from utils import math
from utils.pgutils import text


class PgPlot:
    def __init__(self, size_norm: math.Point, bottomleft_norm: math.Point, screen: pygame.Surface, yrange, tmax, ytick):
        self._size_norm = size_norm
        self._bottomleft_norm = bottomleft_norm
        self._yrange = yrange
        self._tmax = tmax
        self._img_width = screen.get_width() * self._size_norm.x
        self._img_height = screen.get_height() * self._size_norm.y
        self._pxl_per_t = self._img_width / self._tmax
        self._pxl_per_y = self._img_height / (self._yrange[1] - self._yrange[0])

        self.image = pygame.Surface([self._img_width, self._img_height])
        self.image.set_alpha(30)

        # x axis
        pygame.draw.line(self.image, (100,) * 3, pygame.Vector2(0, self._y_to_img(0)),
                         pygame.Vector2(self.image.get_width(), self._y_to_img(0)))

        # y ticks
        for y in range(yrange[0], yrange[1], ytick):
            pygame.draw.line(self.image, utils.WHITE, pygame.Vector2(self.image.get_width() - 3, self._y_to_img(y)),
                             pygame.Vector2(self.image.get_width(), self._y_to_img(y)))
            text.message_to_screen("{:.2g}".format(y), self.image, 6, utils.WHITE,
                                   pygame.Vector2(self._img_width - 3, self._y_to_img(y)), text.HorAlign.RIGHT,
                                   text.VertAlign.CENTER, False)


        self._tarray = []
        self._yarray = []

    def _y_to_img(self, y):
        return (self._yrange[1] - y) * self._pxl_per_y

    def update(self, t: float, y: float):
        self._tarray.append(t)
        self._yarray.append(y)

        # pop off old points outside tmax
        idx_old = None
        for idx, t_ in enumerate(self._tarray):
            if self._tarray[-1] - t_ > self._tmax:
                idx_old = idx
            else:
                break

        if idx_old is not None:
            del self._tarray[:idx_old + 1]
            del self._yarray[:idx_old + 1]

    def set_title(self, title, fontsize=8):
        text.message_to_screen(title, self.image, fontsize, utils.WHITE,
                               pygame.Vector2(0, 0), text.HorAlign.LEFT,
                               text.VertAlign.TOP, False)

    def draw(self, screen: pygame.Surface):
        if len(self._tarray) < 2:
            return
        image = self.image.copy()
        pnts = []
        for t, y in zip(self._tarray, self._yarray):
            x_img = (t - self._tarray[-1]) * self._pxl_per_t + self.image.get_width()
            pnts.append((x_img, self._y_to_img(y)))
        pygame.draw.aalines(image, utils.WHITE, False, pnts)
        screen.blit(image, image.get_rect(
            bottomleft=(self._bottomleft_norm.x * screen.get_width(), self._bottomleft_norm.y * screen.get_height())))
