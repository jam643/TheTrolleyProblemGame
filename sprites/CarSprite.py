from dynamics.CartesianDynamicBicycleModel import CartesianDynamicBicycleModel
from utils.pgutils import *


class CarSprite(pygame.sprite.Sprite, CartesianDynamicBicycleModel):
    def __init__(self, glob_to_screen: GlobToScreen):
        pygame.sprite.Sprite.__init__(self)
        CartesianDynamicBicycleModel.__init__(self)

        self.car_width = 1.2 * self.params.lf

        self.glob_to_screen = glob_to_screen

        self.image = None
        self.rect = None

        self.tire_len = 1.0 * self.glob_to_screen.pxl_per_mtr
        self.tire_width = 0.3 * self.glob_to_screen.pxl_per_mtr
        self.tire_image = pygame.Surface([self.tire_len, self.tire_width],
                                         pygame.SRCALPHA, 32)
        tire_pnts = [(0., 0.), (self.tire_len, 0.), (self.tire_len, self.tire_width), (0., self.tire_width)]
        pygame.draw.polygon(self.tire_image, COLOR8, tire_pnts)

    def build_car_img(self, steer: float):
        car_image = pygame.Surface([(self.params.lr + self.params.lf + self.tire_len) * self.glob_to_screen.pxl_per_mtr,
                                    (self.car_width + self.tire_len) * self.glob_to_screen.pxl_per_mtr],
                                   pygame.SRCALPHA,
                                   32)
        # car_image.set_alpha(200)
        # car_image = car_image.convert_alpha()
        chassis_pnts = [(0, 0), (-self.params.lr, -self.car_width / 2), (-self.params.lr, self.car_width / 2), (0, 0),
                        (self.params.lf, -self.car_width / 2), (1.6 * self.params.lf, 0),
                        (self.params.lf, self.car_width / 2)]
        chassis_pnts = [(p[0] * self.glob_to_screen.pxl_per_mtr + car_image.get_rect().centerx,
                         p[1] * self.glob_to_screen.pxl_per_mtr + car_image.get_rect().centery) for p in chassis_pnts]
        car_image = rot_and_transl(car_image, self.tire_image, 0, -self.params.lr * self.glob_to_screen.pxl_per_mtr,
                                   self.car_width * self.glob_to_screen.pxl_per_mtr / 2)
        car_image = rot_and_transl(car_image, self.tire_image, 0, -self.params.lr * self.glob_to_screen.pxl_per_mtr,
                                   -self.car_width * self.glob_to_screen.pxl_per_mtr / 2)
        car_image = rot_and_transl(car_image, self.tire_image, steer, self.params.lf * self.glob_to_screen.pxl_per_mtr,
                                   self.car_width * self.glob_to_screen.pxl_per_mtr / 2)
        car_image = rot_and_transl(car_image, self.tire_image, steer, self.params.lf * self.glob_to_screen.pxl_per_mtr,
                                   -self.car_width * self.glob_to_screen.pxl_per_mtr / 2)
        chassis_surf = pygame.Surface(
            [(self.params.lr + self.params.lf + self.tire_len) * self.glob_to_screen.pxl_per_mtr,
             (self.car_width + self.tire_len) * self.glob_to_screen.pxl_per_mtr],
            pygame.SRCALPHA,
            32)
        # chassis_surf.set_alpha(200)
        # chassis_surf = chassis_surf.convert_alpha()
        pygame.draw.polygon(chassis_surf, COLOR7, chassis_pnts)
        car_image = rot_and_transl(car_image, chassis_surf, 0, 0, 0)
        # car_image = car_image.convert_alpha()  # make transparent background

        # mask = pygame.mask.from_surface(car_image)
        # shadow_image = mask.to_surface(setcolor=(1,1,1))
        # shadow_image.set_colorkey(BLACK)
        # # shadow_image.convert_alpha()
        # shadow_image.set_alpha(155)
        # shadow_image = shadow_image.convert_alpha()
        # # shadow_image = rot_and_transl(car_image, shadow_image, 0, 4, 4, special_flags=pygame.BLEND_RGB_SUB)
        #
        # car_image2 = pygame.Surface([(self.params.lr + self.params.lf + self.tire_len) * self.glob_to_screen.pxl_per_mtr,
        #                             (self.car_width + self.tire_len) * self.glob_to_screen.pxl_per_mtr],
        #                            pygame.SRCALPHA,
        #                            32)
        # car_image2 = car_image2.convert_alpha()
        # car_image2 = rot_and_transl(car_image2, shadow_image, 0, -8, 6)
        # car_image2 = rot_and_transl(car_image2, car_image, 0, 0, 0)
        return car_image

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self, steer: float, dt: float):
        self.integrate([steer], dt)

        # graphics
        car_image = self.build_car_img(steer)
        car_image = pygame.transform.rotate(car_image, self.z[self.StateIdx.THETA] * 180 / np.pi)

        self.image = car_image
        self.rect = self.image.get_rect(
            center=self.glob_to_screen.get_pxl_from_glob(
                pygame.Vector2(self.z[self.StateIdx.X], self.z[self.StateIdx.Y])))

    def __repr__(self):
        return CartesianDynamicBicycleModel.__repr__(self)
