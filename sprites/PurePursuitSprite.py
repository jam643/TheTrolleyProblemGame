from control.PurePursuitControl import PurePursuitControl
from utils.pgutils import *
from paths.PathBase import PathBase
from utils import math
from dynamics.CartesianDynamicBicycleModel import CartesianDynamicBicycleModel


class PurePursuitSprite(PurePursuitControl):
    def __init__(self, glob_to_screen: GlobToScreen):
        PurePursuitControl.__init__(self)
        self.glob_to_screen = glob_to_screen

    def draw(self, screen):
        pass
        # if self.nearest_pose:
        #     start_pnt = self.glob_to_screen.get_pxl_from_glob(
        #         pygame.Vector2(self.car_rear_axle.x, self.car_rear_axle.y))
        #     end_pnt = self.glob_to_screen.get_pxl_from_glob(
        #         pygame.Vector2(self.car_rear_axle.x + 5 * np.cos(self.alpha + self.car_rear_axle.theta),
        #                        self.car_rear_axle.y + 5 * np.sin(self.alpha + self.car_rear_axle.theta)))
        #     pygame.draw.line(screen, WHITE, start_pnt, end_pnt, 3)

