import numpy as np
import pygame
from pygame import gfxdraw

from control.lqr_path_tracker import DiscreteLQRPathTracker
from utils.pgutils.pgutils import *
from utils import math
from sprites.plot import PgPlot
from sprites.control_sprite import ControlSprite


class DLQRSprite(DiscreteLQRPathTracker, ControlSprite):
    def __init__(self, params: DiscreteLQRPathTracker.Params, glob_to_screen: GlobToScreen, screen: pygame.Surface):
        DiscreteLQRPathTracker.__init__(self, params)
        self.glob_to_screen = glob_to_screen

        # plotting
        start_buff = 0.1
        buff = 0.01
        width = 0.15
        height = 0.2
        self.cte_plot = PgPlot(math.Point(width, height), math.Point(start_buff, 1 - buff), screen, [-4, 4], 3000, 1)
        self.cte_plot.set_title("LAT. ERROR [M]")
        self.cte_rate_plot = PgPlot(math.Point(width, height), math.Point(buff + start_buff + width, 1 - buff),
                                       screen, [-4, 4], 3000, 1)
        self.cte_rate_plot.set_title("LAT. ERROR RATE [DEG]")
        self.heading_err_plot = PgPlot(math.Point(width, height),math.Point(2*(buff + width) + start_buff, 1 - buff),
                                       screen, [-30, 30], 3000, 10)
        self.heading_err_plot.set_title("YAW ERROR [DEG]")

    def draw(self, screen):
        if self.nearest_pose:
            pygame.draw.circle(screen, WHITE, self.glob_to_screen.get_pxl_from_glob(self.car.pose_rear_axle.to_vect2()),
                               4)
            pygame.draw.circle(screen, WHITE, self.glob_to_screen.get_pxl_from_glob(self.nearest_pose.to_vect2()), 4)

            # draw cte line
            cte_point = math.add_body_frame(
                math.Pose(self.nearest_pose.x, self.nearest_pose.y, self.nearest_pose.theta + np.pi / 2),
                math.Pose(self.cte, 0, 0))
            pygame.draw.line(screen, WHITE, self.glob_to_screen.get_pxl_from_glob(self.nearest_pose.to_vect2()),
                             self.glob_to_screen.get_pxl_from_glob(cte_point.to_vect2()))

            # draw path radius of curvature
            rad = np.inf if self.curv_ref == 0 else 1 / self.curv_ref
            d = 3
            if -1000 < rad * self.glob_to_screen.pxl_per_mtr < 1000:
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
        if self.nearest_pose:
            self.cte_plot.update(1e3*self.glob_to_screen.time_s, self.cte)
            self.cte_plot.draw(screen)
            # todo get common time
            self.heading_err_plot.update(1e3*self.glob_to_screen.time_s, self.theta_e * 180 / np.pi)
            self.heading_err_plot.draw(screen)
            self.cte_rate_plot.update(1e3*self.glob_to_screen.time_s, self.cte_dot)
            self.cte_rate_plot.draw(screen)

