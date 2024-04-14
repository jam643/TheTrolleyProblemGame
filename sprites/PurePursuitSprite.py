import numpy as np
from pygame import gfxdraw

from control.PurePursuitControl import PurePursuitControl
from sprites.plot import PgPlot, PlotManager
from paths import path_utils
from utils.pgutils.pgutils import *
from utils import math
from utils.pgutils.text import message_to_screen, HorAlign, VertAlign
from sprites.sprite_bases import ControlSpriteBase


class PurePursuitSprite(PurePursuitControl, ControlSpriteBase):
    def __init__(self, params: PurePursuitControl.Params, glob_to_screen: GlobToScreen, screen: pygame.Surface):
        PurePursuitControl.__init__(self, params)
        self.glob_to_screen = glob_to_screen

        self.plot_manager = PlotManager(0.1 + 0.33, 0.01, 0.01)
        t_plot_dur_ms = 3000
        width = 0.1
        height = 0.15
        self.plot_manager.add_plot("e1",
                                   PgPlot(math.Point(width, height), "LAT. ERROR [M]", screen, [-4, 4], t_plot_dur_ms,
                                          1))

    def draw(self, screen):
        if self.nearest_pose and self.lookahead_pose:
            self._draw_arc(screen)

            pygame.draw.circle(screen, WHITE, self.glob_to_screen.get_pxl_from_glob(self.lookahead_pose.to_vect2()), 4)
            message_to_screen("LOOKAHEAD", screen, 8, WHITE,
                              self.glob_to_screen.get_pxl_from_glob(self.lookahead_pose.to_vect2()) + pygame.Vector2(6,
                                                                                                                     0),
                              hor_align=HorAlign.LEFT, vert_align=VertAlign.CENTER, normalize_pose=False)
            pygame.draw.circle(screen, WHITE, self.glob_to_screen.get_pxl_from_glob(self.car_rear_axle.to_vect2()), 4)
            pygame.draw.circle(screen, WHITE, self.glob_to_screen.get_pxl_from_glob(self.nearest_pose.to_vect2()), 4)


    def draw_plots(self, screen: pygame.Surface):
        if self.nearest_pose:
            self.plot_manager.plots["e1"].update(1e3 * self.glob_to_screen.time_s,
                                                 path_utils.get_cross_err(self.nearest_pose, self.car_ref_pnt))
            self.plot_manager.draw_plots(screen)

    def _draw_arc(self, screen):
        center = self.glob_to_screen.get_pxl_from_glob(
            math.add_body_frame(self.car_rear_axle, math.Pose(0, self.radius, 0)).to_vect2())
        rad = int(abs(self.radius) * self.glob_to_screen.pxl_per_mtr)
        if -2e3 < rad < 2e3:
            if self.radius > 0:
                arc_angles = np.array(
                    [-self.car_rear_axle.theta - 2 * self.alpha, -self.car_rear_axle.theta]) + np.pi / 2
            else:
                arc_angles = np.array(
                    [-self.car_rear_axle.theta, -self.car_rear_axle.theta - 2 * self.alpha]) - np.pi / 2
            gfxdraw.arc(screen, int(center.x), int(center.y), rad, int(np.rad2deg(arc_angles[0])),
                        int(np.rad2deg(arc_angles[1])), (255, 255, 255))
        else:
            pygame.draw.line(screen, WHITE, self.glob_to_screen.get_pxl_from_glob(self.car_rear_axle.to_vect2()),
                             self.glob_to_screen.get_pxl_from_glob(self.lookahead_pose.to_vect2()))
