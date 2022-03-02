import pygame

from abc import ABC, abstractmethod
import pygame_menu

from paths.BSpline import BSplinePath
from utils.pgutils.pgutils import *
from utils import math
from sprites.CarSprite import CarSprite
from sprites.PathSprite import PathSprite
from sprites.TraceSprite import TraceSprite
from sprites.PurePursuitSprite import PurePursuitSprite
from control import ManualControl, PurePursuitControl, SpeedControl


class SceneBase(ABC):
    glob_to_screen = GlobToScreen(35, 0, 0, fps=60, play_speed=2)
    clock = pygame.time.Clock()

    def __init__(self, screen: pygame.Surface):
        super().__init__()
        self.screen = screen
        self.glob_to_screen.y_pxl_rel_glob = screen.get_height() / 2
        self.next = self
        self.time_scene_start_ms = pygame.time.get_ticks()

    @abstractmethod
    def process_input(self, events: List[type(pygame.event)], pressed_keys):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                pygame.quit()
                quit()

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def render(self):
        pass

    def get_time_s(self) -> float:
        return (pygame.time.get_ticks() - self.time_scene_start_ms) * 1e-3

    def switch_to_scene(self, next_scene):
        if next_scene is not self:
            self.time_scene_start_ms = pygame.time.get_ticks()
        self.next = next_scene

    def terminate(self):
        self.switch_to_scene(None)


class ManualDrivingScene(SceneBase):
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)

        self.car_sprite = CarSprite(self.glob_to_screen)

        self.manual_control = ManualControl.ManualControl(70 * np.pi / 180, 0.04, 0.1)
        self.steer = None
        # trace_sprite = TraceSprite(screen, glob_to_screen)

    def process_input(self, events, pressed_keys):
        self.steer = self.manual_control.update(pressed_keys)

    def update(self):
        self.car_sprite.update(self.steer, self.glob_to_screen.sim_dt)
        # trace_sprite.update(car_sprite.z[CarSprite.StateIdx.X], car_sprite.z[CarSprite.StateIdx.Y],
        #                     glob_to_screen.sim_dt)

    def render(self):
        self.screen.fill(COLOR1)

        self.car_sprite.draw(self.screen)
        # trace_sprite.draw(screen)
