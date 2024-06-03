import pygame
from abc import ABC

import utils.pgutils.pgutils as utils
from utils import math
from utils.pgutils import text


class PgPlot:
    def __init__(
        self,
        size_norm: math.Point,
        title: str,
        screen: pygame.Surface,
        yrange,
        tmax,
        ytick,
        bottomleft_norm: math.Point = math.Point(0, 0),
    ):
        self._bottomleft_norm = bottomleft_norm
        self._size_norm = size_norm
        self._yrange = yrange
        self._tmax = tmax
        self._img_width = screen.get_width() * self._size_norm.x
        self._img_height = screen.get_height() * self._size_norm.y
        self._pxl_per_t = self._img_width / self._tmax
        self._pxl_per_y = self._img_height / (self._yrange[1] - self._yrange[0])

        self.image = pygame.Surface([self._img_width, self._img_height])
        self.image.set_alpha(40)
        self.image.fill((30,) * 3)

        text.message_to_screen(
            title,
            self.image,
            8,
            utils.WHITE,
            pygame.Vector2(0, 0),
            text.HorAlign.LEFT,
            text.VertAlign.TOP,
            False,
        )

        # x axis
        pygame.draw.line(
            self.image,
            (100,) * 3,
            pygame.Vector2(0, self._y_to_img(0)),
            pygame.Vector2(self.image.get_width(), self._y_to_img(0)),
        )

        # y ticks
        for y in range(yrange[0], yrange[1], ytick):
            pygame.draw.line(
                self.image,
                utils.WHITE,
                pygame.Vector2(self.image.get_width() - 3, self._y_to_img(y)),
                pygame.Vector2(self.image.get_width(), self._y_to_img(y)),
            )
            text.message_to_screen(
                "{:.2g}".format(y),
                self.image,
                6,
                utils.WHITE,
                pygame.Vector2(self._img_width - 3, self._y_to_img(y)),
                text.HorAlign.RIGHT,
                text.VertAlign.CENTER,
                False,
            )

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
            del self._tarray[: idx_old + 1]
            del self._yarray[: idx_old + 1]

    def draw(self, screen: pygame.Surface):
        if len(self._tarray) < 2:
            return
        image = self.image.copy()
        pnts = []
        for t, y in zip(self._tarray, self._yarray):
            x_img = (t - self._tarray[-1]) * self._pxl_per_t + self.image.get_width()
            pnts.append((x_img, self._y_to_img(y)))
        pygame.draw.aalines(image, utils.WHITE, False, pnts)
        screen.blit(
            image,
            image.get_rect(
                bottomleft=(
                    self._bottomleft_norm.x * screen.get_width(),
                    self._bottomleft_norm.y * screen.get_height(),
                )
            ),
        )


class PlotManager(ABC):
    def __init__(self, x_buff_init, y_buff_init, x_buff):
        self._current_x = x_buff_init
        self._x_buff = x_buff
        self._y_buff_init = y_buff_init

        self.plots = {}

    def add_plot(self, plt_name: str, plot: PgPlot):
        plot._bottomleft_norm = math.Point(self._current_x, 1 - self._y_buff_init)
        self.plots.update({plt_name: plot})
        self._current_x += plot._size_norm.x + self._x_buff

    def draw_plots(self, screen: pygame.Surface):
        for val in self.plots.values():
            val.draw(screen)


def draw_arrow(
    screen: pygame.Surface,
    pose: math.Pose,
    length_m: float,
    sim_to_real: utils.SimToReal,
    color=utils.WHITE,
):
    """
    Draw an arrow on the screen.

    Args:
        screen (pygame.Surface): The surface to draw the arrow on.
        pose (math.Pose): The pose of the arrow.
        length_m (float): The length of the arrow in meters.
        sim_to_real (utils.SimToReal): The conversion utility for converting between simulation and real-world coordinates.
        color (tuple, optional): The color of the arrow. Defaults to utils.WHITE.
    """
    line = math.trans_rot(
        [math.Point(0, 0), math.Point(length_m, 0)], pose.x, pose.y, pose.theta
    )

    arrow_width_m = 0.15 * length_m
    triangle = math.trans_rot(
        [
            math.Point(length_m, 0),
            math.Point(length_m - arrow_width_m, arrow_width_m / 2),
            math.Point(length_m - arrow_width_m, -arrow_width_m / 2),
            math.Point(length_m, 0),
        ],
        pose.x,
        pose.y,
        pose.theta,
    )

    pygame.draw.circle(
        screen, color, sim_to_real.get_sim_from_real(pose.point).to_vect2(), 4
    )
    pygame.draw.line(
        screen,
        color,
        sim_to_real.get_sim_from_real(line[0]).to_vect2(),
        sim_to_real.get_sim_from_real(line[1]).to_vect2(),
        width=2,
    )
    pygame.draw.lines(
        screen,
        color,
        True,
        [sim_to_real.get_sim_from_real(t).to_vect2() for t in triangle],
        width=2,
    )
