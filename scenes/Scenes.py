import pygame

from abc import ABC, abstractmethod

from paths.BSpline import BSplinePath
from utils.pgutils import *
from utils import math
from sprites.CarSprite import CarSprite
from sprites.PathSprite import PathSprite
from sprites.TraceSprite import TraceSprite
from sprites.PIDControlSprite import PIDControlSprite
from sprites.PurePursuitSprite import PurePursuitSprite
from control import PIDControl, ManualControl, PurePursuitControl, SpeedControl
from font import PygameText


class SceneBase(ABC):
    glob_to_screen = GlobToScreen(30, 0, SCREEN_HEIGHT / 2, fps=60, play_speed=2)
    clock = pygame.time.Clock()

    def __init__(self, screen: pygame.Surface):
        super().__init__()
        self.screen = screen
        self.next = self

    @abstractmethod
    def process_input(self, events: List[type(pygame.event)], pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                pygame.quit()
                quit()

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def render(self):
        pass

    def switch_to_scene(self, next_scene):
        self.next = next_scene

    def terminate(self):
        self.switch_to_scene(None)


class PathCreatorScene(SceneBase):
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        self.path_sprite = PathSprite(BSplinePath([], 20, 3, 0, 1), self.glob_to_screen)

    def process_input(self, events, pressed_keys):
        path = self.path_sprite.update(events)
        if path:
            self.switch_to_scene(PIDDrivingScene(path))

    def update(self):
        # self.glob_to_screen.x_pxl_rel_glob -= 5*self.glob_to_screen.pxl_per_mtr*self.glob_to_screen.sim_dt
        pass

    def render(self):
        self.screen.fill(COLOR1)
        self.path_sprite.draw(self.screen)


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


class PIDDrivingScene(SceneBase):
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)

        self.path_sprite = PathSprite(BSplinePath([], 20, 3, 0, 1), self.glob_to_screen)
        self.car_sprite = CarSprite(self.glob_to_screen)

        self.steer = None
        self.pid_control_sprite = PIDControlSprite(0.03, .00, self.glob_to_screen)
        self.trace_sprite = TraceSprite(self.glob_to_screen)

    def process_input(self, events, pressed_keys):
        self.path_sprite.update(events)

    def update(self):
        self.glob_to_screen.x_pxl_rel_glob -= 0 * self.glob_to_screen.pxl_per_mtr * self.glob_to_screen.sim_dt
        self.steer = self.pid_control_sprite.update(self.car_sprite, self.path_sprite.path)
        self.car_sprite.update(self.steer, self.glob_to_screen.sim_dt)
        self.trace_sprite.update(self.car_sprite.z[CarSprite.StateIdx.X],
                                 self.car_sprite.z[CarSprite.StateIdx.Y],
                                 self.glob_to_screen.sim_dt)

    def render(self):
        self.screen.fill(COLOR1)

        self.path_sprite.draw(self.screen)
        self.car_sprite.draw(self.screen)
        self.trace_sprite.draw(self.screen)
        self.pid_control_sprite.draw(self.screen)
        nearest_pnt, s = self.path_sprite.path.get_nearest_pose(
            math.add_body_frame(self.car_sprite.pose, math.Pose(-2 * self.car_sprite.params.lf, 0, 0)).to_vect2())
        print("station {}".format(s))
        if nearest_pnt:
            start_pnt = self.glob_to_screen.get_pxl_from_glob(pygame.Vector2(nearest_pnt.x, nearest_pnt.y))
            end_pnt = self.glob_to_screen.get_pxl_from_glob(
                pygame.Vector2(nearest_pnt.x + 5 * np.cos(nearest_pnt.theta),
                               nearest_pnt.y + 5 * np.sin(nearest_pnt.theta)))
            pygame.draw.line(self.screen, COLOR8, start_pnt, end_pnt, 3)


class PurePursuiteDrivingScene(SceneBase):
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)

        self.path_sprite = PathSprite(BSplinePath([], 20, 3, 0, 1), self.glob_to_screen)
        self.car_sprite = CarSprite(self.glob_to_screen)

        self.steer = None
        self.scroll_speed = 9
        self.control = PurePursuitSprite(self.glob_to_screen)
        self.speed_control = SpeedControl.SpeedControl()
        self.trace_sprite = TraceSprite(self.glob_to_screen)

    def process_input(self, events, pressed_keys):
        super().process_input(events, pressed_keys)
        self.path_sprite.update(events)

    def update(self):
        self.glob_to_screen.x_pxl_rel_glob -= self.scroll_speed * self.glob_to_screen.pxl_per_mtr * self.glob_to_screen.sim_dt
        self.steer = self.control.update(self.car_sprite, self.path_sprite.path)
        self.car_sprite.vx = self.speed_control.update(self.car_sprite, self.path_sprite.path,
                                                       self.glob_to_screen.sim_dt)
        self.car_sprite.update(self.steer, self.glob_to_screen.sim_dt)
        self.trace_sprite.update(self.car_sprite.z[CarSprite.StateIdx.X],
                                 self.car_sprite.z[CarSprite.StateIdx.Y],
                                 self.glob_to_screen.sim_dt)

    def render(self):
        self.screen.fill(COLOR1)

        self.path_sprite.draw(self.screen)
        self.car_sprite.draw(self.screen)
        # self.trace_sprite.draw(screen)
        self.control.draw(self.screen)

        PygameText.message_to_screen(text="FPS: {:.1f}".format(self.clock.get_fps()), screen=self.screen, fontsize=30, color=WHITE,
                                     normalized_pose=pygame.Vector2(0.01, 0.01), hor_align=PygameText.HorAlign.LEFT,
                                     vert_align=PygameText.VertAlign.TOP)

        # nearest_pnt, s = self.path_sprite.path.get_nearest_pose(
        #     math.add_body_frame(self.car_sprite.pose, math.Pose(-2*self.car_sprite.params.lf, 0, 0)).to_vect2())
        # print("station {}".format(s))
        # if self.control.lookahead_pose:
        #     start_pnt = self.glob_to_screen.get_pxl_from_glob(pygame.Vector2(self.control.lookahead_pose.x, self.control.lookahead_pose.y))
        #     end_pnt = self.glob_to_screen.get_pxl_from_glob(pygame.Vector2(self.control.lookahead_pose.x + 5 * np.cos(self.control.lookahead_pose.theta),
        #                                                                self.control.lookahead_pose.y + 5 * np.sin(self.control.lookahead_pose.theta)))
        #     pygame.draw.line(screen, WHITE, start_pnt, end_pnt, 3)
