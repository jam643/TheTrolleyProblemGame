from dynamics.CartesianDynamicBicycleModel import CartesianDynamicBicycleModel
from utils.pgutils import *


class CarSprite(pygame.sprite.Sprite, CartesianDynamicBicycleModel):
    def __init__(self, glob_to_screen: GlobToScreen):
        pygame.sprite.Sprite.__init__(self)
        CartesianDynamicBicycleModel.__init__(self)

        self.car_width = 1.5

        self.glob_to_screen = glob_to_screen

        self.image = None
        self.rect = None
        self.tire_image = pygame.Surface([1.2 * self.glob_to_screen.pxl_per_mtr, 0.5 * self.glob_to_screen.pxl_per_mtr])
        pygame.draw.ellipse(self.tire_image, WHITE, self.tire_image.get_rect())
        self.com_image = pygame.Surface([0.3 * self.glob_to_screen.pxl_per_mtr, 0.3 * self.glob_to_screen.pxl_per_mtr])
        pygame.draw.ellipse(self.com_image, WHITE, self.com_image.get_rect())

    def build_car_img(self, steer: float):
        car_image = pygame.Surface([200, 200], pygame.SRCALPHA, 32)
        car_image = car_image.convert_alpha()  # make transparent background
        car_image = rot_and_transl(car_image, self.com_image, 0, 0, 0)
        car_image = rot_and_transl(car_image, self.tire_image, 0, -self.params.lr * self.glob_to_screen.pxl_per_mtr,
                                   self.car_width * self.glob_to_screen.pxl_per_mtr / 2)
        car_image = rot_and_transl(car_image, self.tire_image, 0, -self.params.lr * self.glob_to_screen.pxl_per_mtr,
                                   -self.car_width * self.glob_to_screen.pxl_per_mtr / 2)
        car_image = rot_and_transl(car_image, self.tire_image, steer, self.params.lf * self.glob_to_screen.pxl_per_mtr,
                                   self.car_width * self.glob_to_screen.pxl_per_mtr / 2)
        car_image = rot_and_transl(car_image, self.tire_image, steer, self.params.lf * self.glob_to_screen.pxl_per_mtr,
                                   -self.car_width * self.glob_to_screen.pxl_per_mtr / 2)
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
            center=self.glob_to_screen.get_pxl_from_glob(pygame.Vector2(self.z[self.StateIdx.X], self.z[self.StateIdx.Y])))

    def __repr__(self):
        return CartesianDynamicBicycleModel.__repr__(self)