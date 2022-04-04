import numpy as np
from pygame import gfxdraw

from control.lqr_path_tracker import DiscreteLQRPathTracker
from utils.pgutils.pgutils import *
from utils import math
from sprites.plot import PgPlot, PlotManager, draw_arrow
from sprites.sprite_bases import ControlSpriteBase


class DLQRSprite(DiscreteLQRPathTracker, ControlSpriteBase):
    def __init__(self, params: DiscreteLQRPathTracker.Params, glob_to_screen: GlobToScreen, screen: pygame.Surface):
        DiscreteLQRPathTracker.__init__(self, params)
        self.glob_to_screen = glob_to_screen

        # plotting
        self.plot_manager = PlotManager(0.1 + 0.22, 0.01, 0.01)
        t_plot_dur_ms = 3000
        width = 0.1
        height = 0.15
        self.plot_manager.add_plot("e1",
                                   PgPlot(math.Point(width, height), "LAT. ERROR [M]", screen, [-4, 4], t_plot_dur_ms,
                                          1))
        self.plot_manager.add_plot("e1d",
                                   PgPlot(math.Point(width, height), "LAT. ERROR RATE [M/S]", screen, [-4, 4],
                                          t_plot_dur_ms, 1))
        self.plot_manager.add_plot("e2", PgPlot(math.Point(width, height), "YAW ERROR [DEG]", screen, [-30, 30],
                                                t_plot_dur_ms, 10))
        self.plot_manager.add_plot("e2d",
                                   PgPlot(math.Point(width, height), "YAW ERROR RATE [DEG/S]", screen, [-20, 20],
                                          t_plot_dur_ms, 10))
        self.plot_manager.add_plot("solvetime",
                                   PgPlot(math.Point(width, height), "SOLVE TIME [MS]", screen, [0, 40],
                                          t_plot_dur_ms, 10))

    def draw(self, screen):
        if self.nearest_pose:
            pygame.draw.circle(screen, WHITE, self.glob_to_screen.get_pxl_from_glob(self.car.pose_rear_axle.to_vect2()),
                               4)
            pygame.draw.circle(screen, WHITE, self.glob_to_screen.get_pxl_from_glob(self.nearest_pose.to_vect2()), 4)

            draw_arrow(screen, self.nearest_pose, 2, self.glob_to_screen, WHITE)

            # draw cte line
            draw_arrow(screen, math.Pose(self.nearest_pose.x, self.nearest_pose.y, self.nearest_pose.theta + np.pi / 2),
                       self.cte, self.glob_to_screen, WHITE)

            # draw path radius of curvature
            rad = np.inf if self.curv_ref == 0 else 1 / self.curv_ref
            d = 3
            try:
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
            except Exception as e:
                pass

    def draw_plots(self, screen: pygame.Surface):
        if self.nearest_pose:
            self.plot_manager.plots["e1"].update(1e3 * self.glob_to_screen.time_s, self.cte)
            self.plot_manager.plots["e2"].update(1e3 * self.glob_to_screen.time_s, np.rad2deg(self.theta_e))
            self.plot_manager.plots["e1d"].update(1e3 * self.glob_to_screen.time_s, self.cte_dot)
            self.plot_manager.plots["e2d"].update(1e3 * self.glob_to_screen.time_s, np.rad2deg(self.theta_e_dot))
            self.plot_manager.plots["solvetime"].update(1e3 * self.glob_to_screen.time_s, self.solvetime_ms)
            self.plot_manager.draw_plots(screen)
