import pygame
import numpy as np

from dynamics.Vehicle import Vehicle
import utils.pgutils.pgutils as pgutils
import utils.math as math


class CarSprite(pygame.sprite.Sprite):
    def __init__(self, sim_to_real: pgutils.SimToReal, params: Vehicle.Params):
        pygame.sprite.Sprite.__init__(self)

        self.params = params

        self.sim_to_real = sim_to_real

        self.image = None
        self.rect = None

        self.tire_len = 1.0
        self.tire_width = 0.3
        self.car_width = 1.7

        self.collide_timer = 0
        self.collide_duration = 1.3
        self.is_colliding = False

    def draw(self, screen, state: Vehicle.State):
        screen.blit(self.car_shadow_image, self.car_shadow_rect)
        screen.blit(self.image, self.rect)

    @staticmethod
    def _make_box_polygon(d_front: float, d_rear: float, d_left: float, d_right: float):
        return np.array(
            [[-d_rear, d_front, d_front, -d_rear], [-d_right, -d_right, d_left, d_left]]
        )

    def _build_car_img(self, steer: float):
        polygon_list = []
        p = self.params

        polygon_list.append(
            math.trans_rot(
                math.Point.from_list(self.tire_pnts),
                p.lf,
                self.car_width / 2 - self.tire_width / 2,
                -steer,
            )
        )
        polygon_list.append(
            math.trans_rot(
                math.Point.from_list(self.tire_pnts),
                p.lf,
                -(self.car_width / 2 - self.tire_width / 2),
                -steer,
            )
        )
        polygon_list = polygon_list + self.polygon_list_base

        return polygon_list

    def update(self, state: Vehicle.State):
        # update polygons
        self.tire_pnts = self._make_box_polygon(
            self.tire_len / 2.0,
            self.tire_len / 2.0,
            self.tire_width / 2,
            self.tire_width / 2,
        )

        chassis_pnts = np.array(
            [
                [
                    0,
                    -self.params.lr,
                    -self.params.lr,
                    0,
                    self.params.lf,
                    self.tire_len / 2 + self.params.lf,
                    self.params.lf,
                ],
                [
                    0,
                    -self.car_width / 2,
                    self.car_width / 2,
                    0,
                    -self.car_width / 2,
                    0,
                    self.car_width / 2,
                ],
            ]
        )

        cog_pnt = math.Point(
            max(self.params.lr, self.params.lf) + self.tire_len / 2,
            self.car_width / 2 + self.tire_len / 2,
        )
        polygon_list = []
        polygon_list.append(
            math.rot_trans_2d(
                self.tire_pnts,
                dx=-self.params.lr,
                dy=self.car_width / 2 - self.tire_width / 2,
            )
        )
        polygon_list.append(
            math.rot_trans_2d(
                self.tire_pnts,
                dx=-self.params.lr,
                dy=-(self.car_width / 2 - self.tire_width / 2),
            )
        )
        polygon_list.append(
            math.rot_trans_2d(
                self.tire_pnts,
                dx=self.params.lf,
                dy=self.car_width / 2 - self.tire_width / 2,
                angle_rad=-state.delta,
            )
        )
        polygon_list.append(
            math.rot_trans_2d(
                self.tire_pnts,
                dx=self.params.lf,
                dy=-(self.car_width / 2 - self.tire_width / 2),
                angle_rad=-state.delta,
            )
        )
        polygon_list.append(chassis_pnts)

        polygon_list_image_frame = [
            math.rot_trans_2d(
                polygon,
                dx=cog_pnt.x,
                dy=cog_pnt.y,
                scale_trans=self.sim_to_real.params.pxl_per_meter,
                scale_vec=self.sim_to_real.params.pxl_per_meter,
            )
            for polygon in polygon_list
        ]

        # graphics
        car_image = pygame.Surface(
            [
                (2.1 * max(self.params.lr, self.params.lf) + self.tire_len)
                * self.sim_to_real.params.pxl_per_meter,
                (self.car_width + self.tire_len)
                * self.sim_to_real.params.pxl_per_meter,
            ],
            pygame.SRCALPHA,
        )
        car_shadow_image = car_image.copy()
        car_shadow_image.set_alpha(100)

        chassis_color = pgutils.COLOR7
        if self.is_colliding:
            time_since_collision = self.sim_to_real.time_s - self.collide_timer
            if time_since_collision > self.collide_duration:
                self.is_colliding = False
                return
            transform_shape = np.sin(
                time_since_collision * np.pi / self.collide_duration
            )
            chassis_color = pygame.Color(pgutils.COLOR7).lerp(
                pygame.Color(pgutils.COLOR9), transform_shape
            )

        pgutils.draw_polygons(
            car_image,
            polygon_list_image_frame,
            [pgutils.COLOR8] * 4 + [chassis_color],
            self.sim_to_real,
        )
        pgutils.draw_polygons(
            car_shadow_image,
            polygon_list_image_frame,
            [pgutils.BLACK] * 5,
            self.sim_to_real,
        )

        car_image = pygame.transform.rotate(car_image, state.theta * 180 / np.pi)
        self.car_shadow_image = pygame.transform.rotate(
            car_shadow_image, state.theta * 180 / np.pi
        )

        self.car_shadow_rect = self.car_shadow_image.get_rect(
            center=self.sim_to_real.get_sim_from_real(
                math.Point(state.x - 0.3, state.y - 0.5)
            ).to_vect2()
        )

        self.image = car_image
        self.rect = self.image.get_rect(
            center=self.sim_to_real.get_sim_from_real(
                math.Point(state.x, state.y)
            ).to_vect2()
        )

        if self.is_colliding:
            time_since_collision = self.sim_to_real.time_s - self.collide_timer
            if time_since_collision > self.collide_duration:
                self.is_colliding = False
            transform_shape = np.sin(
                time_since_collision * np.pi / self.collide_duration
            )
            self.image = pygame.transform.smoothscale_by(
                self.image, 1 + 0.3 * transform_shape
            )
            self.car_shadow_image = pygame.transform.smoothscale_by(
                self.car_shadow_image, 1 + 0.2 * transform_shape
            )
            self.rect = self.image.get_rect(
                center=self.sim_to_real.get_sim_from_real(
                    math.Point(state.x, state.y + 0.5 * transform_shape)
                ).to_vect2()
            )

    def set_colliding(self):
        if not self.is_colliding:
            self.is_colliding = True
            self.collide_timer = self.sim_to_real.time_s
