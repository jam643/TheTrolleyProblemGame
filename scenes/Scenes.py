import pygame

from typing import List
from abc import ABC, abstractmethod

from paths.BSpline import BSplinePath
from utils.pgutils import *
from sprites.CarSprite import CarSprite
from sprites.PathSprite import PathSprite
from sprites.TraceSprite import TraceSprite
from control import PIDControl, ManualControl


class SceneBase(ABC):
    glob_to_screen = GlobToScreen(10, 0, SCREEN_HEIGHT / 2, fps=40, play_speed=2)

    def __init__(self):
        super().__init__()
        self.next = self

    @abstractmethod
    def process_input(self, events: List[type(pygame.event)], pressed_keys):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def render(self, screen):
        pass

    def switch_to_scene(self, next_scene):
        self.next = next_scene

    def terminate(self):
        self.switch_to_scene(None)


class PathCreatorScene(SceneBase):
    def __init__(self):
        super().__init__()
        self.path_sprite = PathSprite(BSplinePath([], 20, 3, 0, 1), self.glob_to_screen)

    def process_input(self, events, pressed_keys):
        path = self.path_sprite.update(events)
        if path:
            self.switch_to_scene(PIDDrivingScene(path))

    def update(self):
        self.glob_to_screen.x_pxl_rel_glob -= 5*self.glob_to_screen.pxl_per_mtr*self.glob_to_screen.sim_dt
        pass

    def render(self, screen):
        screen.fill(BLACK)
        self.path_sprite.draw(screen)


class ManualDrivingScene(SceneBase):
    def __init__(self):
        super().__init__()

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

    def render(self, screen):
        screen.fill(BLACK)

        self.car_sprite.draw(screen)
        # trace_sprite.draw(screen)


class PIDDrivingScene(SceneBase):
    def __init__(self, path_sprite: PathSprite):
        super().__init__()

        self.car_sprite = CarSprite(self.glob_to_screen)
        self.path_sprite = path_sprite

        self.steer = None
        self.pid_control = PIDControl.PIDControl(np.pi / 180, 0.02)
        self.trace_sprite = TraceSprite(self.glob_to_screen)

    def process_input(self, events, pressed_keys):
        pass

    def update(self):
        self.steer = self.pid_control.update(self.car_sprite)
        self.car_sprite.update(self.steer, self.glob_to_screen.sim_dt)
        self.trace_sprite.update(self.car_sprite.z[CarSprite.StateIdx.X],
                                 self.car_sprite.z[CarSprite.StateIdx.Y],
                                 self.glob_to_screen.sim_dt)

    def render(self, screen):
        screen.fill(BLACK)

        self.path_sprite.draw(screen)
        self.car_sprite.draw(screen)
        self.trace_sprite.draw(screen)
        nearest_pnt = self.path_sprite.path.get_nearest_coord(pygame.Vector2(self.car_sprite.z[CarSprite.StateIdx.X],
                                                                        self.car_sprite.z[CarSprite.StateIdx.Y]))
        start_pnt = self.glob_to_screen.get_pxl_from_glob(pygame.Vector2(nearest_pnt.x, nearest_pnt.y))
        end_pnt = self.glob_to_screen.get_pxl_from_glob(pygame.Vector2(nearest_pnt.x+5*np.cos(nearest_pnt.theta), nearest_pnt.y+5*np.sin(nearest_pnt.theta)))
        pygame.draw.line(screen, WHITE, start_pnt, end_pnt, 3)
