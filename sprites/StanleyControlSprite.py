from pygame import gfxdraw

from control.StanleyControl import StanleyControl
from utils.pgutils.pgutils import *
from paths.PathBase import PathBase
from utils import math
from dynamics.CartesianDynamicBicycleModel import CartesianDynamicBicycleModel
from utils.pgutils.text import message_to_screen, HorAlign, VertAlign


class StanleyControlSprite(StanleyControl):
    def __init__(self, params: StanleyControl.Params, glob_to_screen: GlobToScreen):
        StanleyControl.__init__(self, params)
        self.glob_to_screen = glob_to_screen

    def draw(self, screen):
        if self.nearest_pose and self.car_front_axle:
            pygame.draw.circle(screen, WHITE, self.glob_to_screen.get_pxl_from_glob(self.car_front_axle.to_vect2()), 4)
            pygame.draw.circle(screen, WHITE, self.glob_to_screen.get_pxl_from_glob(self.nearest_pose.to_vect2()), 4)
