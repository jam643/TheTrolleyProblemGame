import pygame
import numpy as np
import scipy
from dataclasses import dataclass
from typing import NamedTuple
import enum
from profilehooks import profile

# --- Globals ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

SCREEN_WIDTH = 1800
SCREEN_HEIGHT = 1000


@dataclass
class GlobToScreen:
    pxl_per_mtr: float
    x_pxl_rel_glob: float
    y_pxl_rel_glob: float

    fps: int
    play_speed: float

    def get_pxl_from_glob(self, point):
        return point[0] * self.pxl_per_mtr + self.x_pxl_rel_glob, -point[1] * self.pxl_per_mtr + self.y_pxl_rel_glob

    def get_pxl_from_glob(self, x, y):
        return x * self.pxl_per_mtr + self.x_pxl_rel_glob, -y * self.pxl_per_mtr + self.y_pxl_rel_glob

    @property
    def sim_dt(self):
        return self.play_speed / self.fps


def rot_and_transl(surf: pygame.Surface, image: pygame.Surface, angle: float, x: float, y: float) -> pygame.Surface:
    image_rot = pygame.transform.rotate(image, angle * 180 / np.pi)
    surf.blit(image_rot, (
        -image_rot.get_rect().centerx + surf.get_rect().centerx + x,
        -image_rot.get_rect().centery + surf.get_rect().centery + y))
    return surf


class CartesianDynamicBicycleModel:
    class StateIdx(enum.IntEnum):
        X = 0
        Y = 1
        VY = 2
        THETA = 3
        THETADOT = 4

    class ControlIdx(enum.IntEnum):
        STEER = 0

    class Params(NamedTuple):
        m: float  # Mass[kg]
        Iz: float  # Yaw inertia[kg * m ^ 2]
        lf: float  # Distance from CG to front axle[m]
        lr: float  # Distance from CG to rear axle[m]
        cf: float  # Front cornering stiffness[N / rad]
        cr: float  # Rear cornering stiffness[N / rad]

    def __init__(self):
        self.params = self.Params(m=1915, Iz=4235, lf=1.453, lr=1.522, cf=90000, cr=116000)
        self.vx = 10

        self.z = [0, 10, 0, 0, 0]

    def __repr__(self):
        return 'State[x={:.2f}, y={:.2f}, vy={:.2f}, theta={:.2f}, thetadot={:.2f}]'.format(*self.z)

    def integrate(self, u, dt):
        self.z = [self.z[idx] + dt * elem for idx, elem in enumerate(self.__zdot(self.z, u))]

    def __zdot(self, z, u):
        vy = z[self.StateIdx.VY]
        theta = z[self.StateIdx.THETA]
        thetadot = z[self.StateIdx.THETADOT]

        delta = u[self.ControlIdx.STEER]

        term1 = -self.params.cf * (np.arctan((vy + self.params.lf * thetadot) / self.vx) - delta) * np.cos(delta)
        term2 = self.params.cr * np.arctan((vy - self.params.lr * thetadot) / self.vx)
        vydot = (term1 - term2) / self.params.m - self.vx * thetadot
        thetadotdot = (self.params.lf * term1 + self.params.lr * term2) / self.params.Iz

        xdot = self.vx * np.cos(theta) + vy * np.sin(theta)
        ydot = - vy * np.cos(theta) + self.vx * np.sin(theta)

        z_dot = [None] * len(self.StateIdx)
        z_dot[self.StateIdx.X] = xdot
        z_dot[self.StateIdx.Y] = ydot
        z_dot[self.StateIdx.VY] = vydot
        z_dot[self.StateIdx.THETA] = thetadot
        z_dot[self.StateIdx.THETADOT] = thetadotdot

        return z_dot


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
            center=self.glob_to_screen.get_pxl_from_glob(self.z[self.StateIdx.X], self.z[self.StateIdx.Y]))

    def __repr__(self):
        return CartesianDynamicBicycleModel.__repr__(self)


class TraceSprite(pygame.sprite.Sprite):
    def __init__(self, screen: pygame.Surface, glob_to_screen: GlobToScreen):
        super().__init__()
        self.glob_to_screen = glob_to_screen
        self.screen = screen

        self.trace = []
        self.trace_max_T = 3

        self.image = None
        self.rect = None

    def update(self, x, y, dt):
        self.trace.append(self.glob_to_screen.get_pxl_from_glob(x, y))

        image = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA, 32)
        image = image.convert_alpha()

        if len(self.trace) > int(self.trace_max_T / dt):
            self.trace.pop(0)

        if len(self.trace) > 1:
            pygame.draw.aalines(image, WHITE, False, self.trace)

        self.image = image
        self.rect = image.get_rect()

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class ManualControl:
    def __init__(self, rwa_setpoint, p_rise, p_fall):
        super().__init__()
        self.steer = 0
        self.rwa_setpoint = rwa_setpoint
        self.p_rise = p_rise
        self.p_fall = p_fall

    def update(self, pressed_keys):
        if pressed_keys[pygame.K_RIGHT]:
            self.steer += self.p_rise * (-self.rwa_setpoint - self.steer)
        if pressed_keys[pygame.K_LEFT]:
            self.steer += self.p_rise * (self.rwa_setpoint - self.steer)

        if (not pressed_keys[pygame.K_LEFT]) and (not pressed_keys[pygame.K_RIGHT]):
            self.steer += -self.p_fall * self.steer


@profile
def main():
    # Call this function so the Pygame library can initialize itself
    pygame.init()

    # Create screen
    screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
    glob_to_screen = GlobToScreen(20, 0, SCREEN_HEIGHT / 2, fps=120, play_speed=1)

    # Set the title of the window
    pygame.display.set_caption('Project')

    car_sprite = CarSprite(glob_to_screen)
    steer = ManualControl(70 * np.pi / 180, 0.04, 0.1)
    trace_sprite = TraceSprite(screen, glob_to_screen)

    clock = pygame.time.Clock()
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        start_time = pygame.time.get_ticks()
        # updates
        pressed_keys = pygame.key.get_pressed()
        steer.update(pressed_keys)
        car_sprite.update(steer.steer, glob_to_screen.sim_dt)
        trace_sprite.update(car_sprite.z[CarSprite.StateIdx.X], car_sprite.z[CarSprite.StateIdx.Y],
                            glob_to_screen.sim_dt)
        # print(car_sprite)

        # drawing
        screen.fill(BLACK)

        car_sprite.draw(screen)
        trace_sprite.draw(screen)

        # update screen with what we've drawn
        pygame.display.flip()

        # metrics
        print('screen refresh [ms]: {:.1f}'.format(1000. / (clock.get_fps() + 0.1)))
        print('exec time [ms]: {:.1f}'.format(pygame.time.get_ticks() - start_time))

        # Pause
        clock.tick(glob_to_screen.fps)

    pygame.quit()


if __name__ == "__main__":
    main()
