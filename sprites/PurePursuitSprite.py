import numpy as np
from pygame import gfxdraw

from control.PurePursuitControl import PurePursuitControl
from utils.pgutils.pgutils import *
from utils import math
from utils.pgutils.text import message_to_screen, HorAlign, VertAlign
from sprites.control_sprite import ControlSprite


class PurePursuitSprite(PurePursuitControl, ControlSprite):
    def __init__(self, params: PurePursuitControl.Params, glob_to_screen: GlobToScreen):
        PurePursuitControl.__init__(self, params)
        self.glob_to_screen = glob_to_screen

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

            # curvature
            k = self.path.get_curv_at_station(self.station)
            rad = np.inf if k == 0 else 1 / k
            d = 3
            if -1000 < rad * self.glob_to_screen.pxl_per_mtr < 2000:
                center = self.glob_to_screen.get_pxl_from_glob(
                    math.add_body_frame(self.nearest_pose, math.Pose(0, rad, 0)).to_vect2())
                arc_angles = np.array([-self.nearest_pose.theta - d / rad * np.sign(rad),
                                       -self.nearest_pose.theta + d / rad * np.sign(rad)]) + np.pi / 2 * np.sign(rad)
                gfxdraw.arc(screen, int(center.x), int(center.y), int(abs(rad * self.glob_to_screen.pxl_per_mtr)),
                            int(np.rad2deg(arc_angles[0])), int(np.rad2deg(arc_angles[1])), (255, 255, 255))
            else:
                pygame.draw.line(screen, WHITE, self.glob_to_screen.get_pxl_from_glob(
                    math.add_body_frame(self.nearest_pose, math.Pose(-d, 0, 0)).to_vect2()),
                                 self.glob_to_screen.get_pxl_from_glob(
                                     math.add_body_frame(self.nearest_pose, math.Pose(d, 0, 0)).to_vect2()))

    def draw_plots(self, screen: pygame.Surface):
        pass

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
