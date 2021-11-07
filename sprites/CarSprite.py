import pygame
from pygame import gfxdraw
import numpy as np

from dynamics.CartesianDynamicBicycleModel import CartesianDynamicBicycleModel
import utils.pgutils.pgutils as pgutils
import utils.math as math


class CarSprite(pygame.sprite.Sprite, CartesianDynamicBicycleModel):
    def __init__(self, pose_init: math.Pose, glob_to_screen: pgutils.GlobToScreen):
        pygame.sprite.Sprite.__init__(self)
        CartesianDynamicBicycleModel.__init__(self, pose_init)

        self.car_width = 1.2 * self.params.lf

        self.glob_to_screen = glob_to_screen

        self.image = None
        self.rect = None

        self.tire_len = 1.0
        self.tire_width = 0.3
        # self.tire_image = pygame.Surface([self.tire_len, self.tire_width],
        #                                  pygame.SRCALPHA, 32)
        self.tire_pnts = [(-self.tire_len / 2., -self.tire_width / 2), (self.tire_len / 2, -self.tire_width / 2),
                          (self.tire_len / 2, self.tire_width / 2), (-self.tire_len / 2, self.tire_width / 2)]
        # pygame.draw.polygon(self.tire_image, COLOR8, self.tire_pnts)

        chassis_pnts = [(0, 0), (-self.params.lr, -self.car_width / 2), (-self.params.lr, self.car_width / 2), (0, 0),
                        (self.params.lf, -self.car_width / 2), (1.6 * self.params.lf, 0),
                        (self.params.lf, self.car_width / 2)]

        self.polygon_list_base = [math.trans_rot(math.Point.from_list(self.tire_pnts), -self.params.lr,
                                            self.car_width / 2 - self.tire_width / 2, 0),
                             math.trans_rot(math.Point.from_list(self.tire_pnts), -self.params.lr,
                                            -(self.car_width / 2 - self.tire_width / 2), 0),
                             chassis_pnts]
        # pgutils.draw_polygons(self.car_image_base, polygon_list, [pgutils.COLOR8, pgutils.COLOR8, pgutils.COLOR7],
        #                       self.glob_to_screen)

        # pygame.draw.polygon(self.car_image, pgutils.COLOR7, chassis_pnts)

    def build_car_img(self, steer: float):
        polygon_list = []
        polygon_list.append(math.trans_rot(math.Point.from_list(self.tire_pnts), self.params.lf,
                           self.car_width / 2 - self.tire_width / 2,
                           -steer))
        polygon_list.append(math.trans_rot(math.Point.from_list(self.tire_pnts), self.params.lf,
                           -(self.car_width / 2 - self.tire_width / 2),
                           -steer))
        polygon_list = polygon_list + self.polygon_list_base

        return polygon_list

    def draw(self, screen):
        screen.blit(self.car_shadow_image, self.car_shadow_rect)
        screen.blit(self.image, self.rect)

    def update(self, steer: float, dt: float):
        self.integrate([steer], dt)

        # graphics
        car_image = pygame.Surface(
            [1.1*(self.params.lr + self.params.lf + self.tire_len) * self.glob_to_screen.pxl_per_mtr,
             (self.car_width + self.tire_len) * self.glob_to_screen.pxl_per_mtr], pygame.SRCALPHA, 32)
        car_shadow_image = car_image.copy()
        car_shadow_image.set_alpha(100)
        pgutils.draw_polygons(car_image, self.build_car_img(steer), [pgutils.COLOR8]*4 + [pgutils.COLOR7],
                              self.glob_to_screen)
        pgutils.draw_polygons(car_shadow_image, self.build_car_img(steer), [pgutils.BLACK]*5,
                              self.glob_to_screen)
        car_image = pygame.transform.rotate(car_image, self.z[self.StateIdx.THETA] * 180 / np.pi)
        self.car_shadow_image = pygame.transform.rotate(car_shadow_image, self.z[self.StateIdx.THETA] * 180 / np.pi)
        self.car_shadow_rect = self.car_shadow_image.get_rect(center=self.glob_to_screen.get_pxl_from_glob(
                pygame.Vector2(self.z[self.StateIdx.X]-0.3, self.z[self.StateIdx.Y]-0.5)))

        self.image = car_image
        self.rect = self.image.get_rect(
            center=self.glob_to_screen.get_pxl_from_glob(
                pygame.Vector2(self.z[self.StateIdx.X], self.z[self.StateIdx.Y])))

    def __repr__(self):
        return CartesianDynamicBicycleModel.__repr__(self)
