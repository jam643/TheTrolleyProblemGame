from control.PurePursuitControl import PurePursuitControl
from utils.pgutils.pgutils import *
from paths.PathBase import PathBase
from utils import math
from dynamics.CartesianDynamicBicycleModel import CartesianDynamicBicycleModel
from utils.pgutils.text import message_to_screen, HorAlign, VertAlign


class PurePursuitSprite(PurePursuitControl):
    def __init__(self, params: PurePursuitControl.Params, glob_to_screen: GlobToScreen):
        PurePursuitControl.__init__(self, params)
        self.glob_to_screen = glob_to_screen

    def draw(self, screen):
        if self.nearest_pose and self.lookahead_pose:
            self._draw_arc(screen)

            pygame.draw.circle(screen, WHITE, self.glob_to_screen.get_pxl_from_glob(self.lookahead_pose.to_vect2()), 4)
            message_to_screen("LOOKAHEAD", screen, 8, WHITE,
                              self.glob_to_screen.get_pxl_from_glob(self.lookahead_pose.to_vect2()) + pygame.Vector2(6,0),
                              hor_align=HorAlign.LEFT, vert_align=VertAlign.CENTER, normalize_pose=False)
            pygame.draw.circle(screen, WHITE, self.glob_to_screen.get_pxl_from_glob(self.car_rear_axle.to_vect2()), 4)
            pygame.draw.circle(screen, WHITE, self.glob_to_screen.get_pxl_from_glob(self.nearest_pose.to_vect2()), 4)

    def _draw_arc(self, screen):
        center = self.glob_to_screen.get_pxl_from_glob(
            math.add_body_frame(self.car_rear_axle, math.Pose(0, self.radius, 0)).to_vect2())
        rad = int(abs(self.radius) * self.glob_to_screen.pxl_per_mtr)
        if -1000 < rad < 1000:
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
