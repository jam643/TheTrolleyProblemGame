import numpy as np

from control.StanleyControl import StanleyControl
from utils.pgutils.pgutils import *
from sprites.sprite_bases import ControlSpriteBase
from sprites.plot import draw_arrow, PlotManager, PgPlot


class StanleyControlSprite(StanleyControl, ControlSpriteBase):
    def __init__(self, params: StanleyControl.Params, glob_to_screen: GlobToScreen, screen: pygame.Surface):
        StanleyControl.__init__(self, params)
        self.glob_to_screen = glob_to_screen

        # plotting
        self.plot_manager = PlotManager(0.1 + 0.33, 0.01, 0.01)
        t_plot_dur_ms = 3000
        width = 0.1
        height = 0.15
        self.plot_manager.add_plot("e1",
                                   PgPlot(math.Point(width, height), "LAT. ERROR [M]", screen, [-4, 4], t_plot_dur_ms,
                                          1))
        self.plot_manager.add_plot("e2", PgPlot(math.Point(width, height), "YAW ERROR [DEG]", screen, [-30, 30],
                                                t_plot_dur_ms, 10))

    def draw(self, screen):
        if self.nearest_pose and self.car_front_axle:
            draw_arrow(screen, self.nearest_pose, 2, self.glob_to_screen, WHITE)
            draw_arrow(screen, self.car_front_axle, 2, self.glob_to_screen, WHITE)
            draw_arrow(screen, math.Pose(self.car_front_axle.x, self.car_front_axle.y, self.nearest_pose.theta), 2,
                       self.glob_to_screen, WHITE)

            # draw cte line
            draw_arrow(screen, math.Pose(self.nearest_pose.x, self.nearest_pose.y, self.nearest_pose.theta + np.pi / 2),
                       self.cte, self.glob_to_screen, WHITE)

            # plots
            self.plot_manager.plots["e1"].update(1e3 * self.glob_to_screen.time_s, self.cte)
            self.plot_manager.plots["e2"].update(1e3 * self.glob_to_screen.time_s, np.rad2deg(self.theta_e))
            self.plot_manager.draw_plots(screen)

    def draw_plots(self, screen: pygame.Surface):
        pass
