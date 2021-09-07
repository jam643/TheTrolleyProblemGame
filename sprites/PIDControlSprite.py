from control.PIDControl import PIDControl
from utils.pgutils import *
from paths.PathBase import PathBase
from utils import math
from dynamics.CartesianDynamicBicycleModel import CartesianDynamicBicycleModel


class PIDControlSprite(PIDControl):
    def __init__(self, p, d, glob_to_screen: GlobToScreen):
        PIDControl.__init__(self, p, d)
        self.glob_to_screen = glob_to_screen

    def draw(self, screen):
        if self.nearest_pose:
            pygame.draw.line(screen, COLOR8, self.glob_to_screen.get_pxl_from_glob(self.nearest_pose.get_point.to_vect2()),
                             self.glob_to_screen.get_pxl_from_glob(math.add(self.nearest_pose.get_point, self.car_rel_path).to_vect2()))

            pygame.draw.line(screen, COLOR8, self.glob_to_screen.get_pxl_from_glob(self.lookahead_pose.get_point.to_vect2()),
                             self.glob_to_screen.get_pxl_from_glob(math.add(self.lookahead_pose.get_point, self.car_rel_path).to_vect2()))

