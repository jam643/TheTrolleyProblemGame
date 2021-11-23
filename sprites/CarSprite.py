import pygame
import numpy as np

from dynamics.Vehicle import Vehicle
import utils.pgutils.pgutils as pgutils
import utils.math as math


class CarSprite(pygame.sprite.Sprite):
    def __init__(self, glob_to_screen: pgutils.GlobToScreen, params: Vehicle.Params):
        pygame.sprite.Sprite.__init__(self)

        self.params = params

        self.glob_to_screen = glob_to_screen

        self.image = None
        self.rect = None

        self.tire_len = 1.0
        self.tire_width = 0.3
        self.car_width = 1.7

    def draw(self, screen, state: Vehicle.State):
        self._update_imgs(state)
        screen.blit(self.car_shadow_image, self.car_shadow_rect)
        screen.blit(self.image, self.rect)

    def _build_car_img(self, steer: float):
        polygon_list = []
        p = self.params

        polygon_list.append(math.trans_rot(math.Point.from_list(self.tire_pnts), p.lf,
                                           self.car_width / 2 - self.tire_width / 2,
                                           -steer))
        polygon_list.append(math.trans_rot(math.Point.from_list(self.tire_pnts), p.lf,
                                           -(self.car_width / 2 - self.tire_width / 2),
                                           -steer))
        polygon_list = polygon_list + self.polygon_list_base

        return polygon_list

    def _update_imgs(self, state: Vehicle.State):
        # update polygons
        self.tire_pnts = [(-self.tire_len / 2., -self.tire_width / 2), (self.tire_len / 2, -self.tire_width / 2),
                          (self.tire_len / 2, self.tire_width / 2), (-self.tire_len / 2, self.tire_width / 2)]

        chassis_pnts = [(0, 0), (-self.params.lr, -self.car_width / 2), (-self.params.lr, self.car_width / 2),
                        (0, 0),
                        (self.params.lf, -self.car_width / 2), (self.tire_len/2 + self.params.lf, 0),
                        (self.params.lf, self.car_width / 2)]

        cog_pnt = math.Point(max(self.params.lr, self.params.lf) + self.tire_len/2, self.car_width/2 + self.tire_len/2)
        self.polygon_list_base = [math.trans_rot(math.Point.from_list(self.tire_pnts), -self.params.lr,
                                                 self.car_width / 2 - self.tire_width / 2, 0),
                                  math.trans_rot(math.Point.from_list(self.tire_pnts), -self.params.lr,
                                                 -(self.car_width / 2 - self.tire_width / 2), 0),
                                  chassis_pnts]

        # graphics
        car_image = pygame.Surface(
            [(2.0 * max(self.params.lr, self.params.lf) + self.tire_len) * self.glob_to_screen.pxl_per_mtr,
             (self.car_width + self.tire_len) * self.glob_to_screen.pxl_per_mtr], pygame.SRCALPHA)
        car_shadow_image = car_image.copy()
        car_shadow_image.set_alpha(100)

        car_polylines = self._build_car_img(state.delta)
        pgutils.draw_polygons(car_image, car_polylines, cog_pnt, [pgutils.COLOR8] * 4 + [pgutils.COLOR7],
                              self.glob_to_screen)
        pgutils.draw_polygons(car_shadow_image, car_polylines, cog_pnt, [pgutils.BLACK] * 5,
                              self.glob_to_screen)
        car_image = pygame.transform.rotate(car_image, state.theta * 180 / np.pi)
        self.car_shadow_image = pygame.transform.rotate(car_shadow_image, state.theta * 180 / np.pi)
        self.car_shadow_rect = self.car_shadow_image.get_rect(center=self.glob_to_screen.get_pxl_from_glob(
            pygame.Vector2(state.x - 0.3, state.y - 0.5)))

        self.image = car_image
        self.rect = self.image.get_rect(center=self.glob_to_screen.get_pxl_from_glob(pygame.Vector2(state.x, state.y)))
