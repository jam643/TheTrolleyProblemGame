import pygame_menu
import copy

from scenes.Scenes import SceneBase
from scenes import StartScene
from paths.BSpline import BSplinePath
from utils.pgutils.pgutils import *
from utils.pgutils.text import theme_default, menu_default, message_to_screen, VertAlign, HorAlign
from utils import math
from sprites.CarSprite import CarSprite
from sprites.PathSprite import PathSprite
from sprites.PathSpriteAuto import PathSpriteAuto
from sprites.TraceSprite import TraceSprite
from sprites.PurePursuitSprite import PurePursuitSprite
from sprites.ControlFactory import ControlType, ControlFactory
from control import SpeedControl


class SandboxScene(SceneBase):
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        self.glob_to_screen.pxl_per_mtr = 40
        self.control_factory = ControlFactory(self.glob_to_screen, self.screen, ControlType.pure_pursuit)

        self.menu = menu_default(self.screen, theme_default(20), columns=3, rows=5)
        self.path_menu = menu_default(self.screen, theme_default(20))

        self.path_menu.add.toggle_switch("AUTO GEN PATH", state_text=("OFF", "ON"),
                                         onchange=self._enable_auto_gen_path_callback)
        self.path_menu.add.button("BACK", pygame_menu.events.BACK)

        self.menu.add.button("CONTROLLER", self.control_factory.controller_menu)
        self.menu.add.button("PATH", self.path_menu)
        self.menu.add.toggle_switch("VISUALIZATIONS", state_text=("OFF", "ON"), onchange=self._enable_algo_viz_callback,
                                    default=1)

        def start_scene_callback(): self.next = StartScene.StartScene(self.screen)

        self.menu.add.button("MAIN MENU", start_scene_callback)
        self.menu.add.button("RETURN", pygame_menu.events.CLOSE)
        self.is_enable_algo_viz = True
        self.is_auto_gen_path = False

        self.path_sprite = PathSprite(BSplinePath([], 20, 3, 0, 1), self.glob_to_screen)
        self.car_sprite = CarSprite(
            pose_init=self.glob_to_screen.get_pose_glob_from_pxl(math.Pose(0,
                                                                           screen.get_height() / 2, 0)),
            glob_to_screen=self.glob_to_screen)

        self.steer = None
        self.scroll_speed = 12
        self.speed_control = SpeedControl.SpeedControl(station_setpoint=25)
        self.trace_sprite = TraceSprite(self.glob_to_screen)

    def process_input(self, events, pressed_keys):
        super().process_input(events, pressed_keys)

        if self.menu.is_enabled():
            self.menu.update(events)

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                if self.menu.is_enabled():
                    self.menu.disable()
                else:
                    self.menu.enable()

    def update(self):
        if not self.menu.is_enabled() or self.is_auto_gen_path:
            if self.is_auto_gen_path:
                self.path_sprite.update(self.get_time_s())
            else:
                self.path_sprite.update()

            self.glob_to_screen.x_pxl_rel_glob -= self.scroll_speed * self.glob_to_screen.pxl_per_mtr * self.glob_to_screen.sim_dt
            self.steer = self.control_factory.control.update(self.car_sprite, self.path_sprite.path)
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
        if self.is_enable_algo_viz:
            self.control_factory.control.draw(self.screen)

        if self.menu.is_enabled():
            self.menu.draw(self.screen)

        message_to_screen(text="FPS: {:.1f}".format(self.clock.get_fps()), screen=self.screen, fontsize=30,
                          color=WHITE,
                          pose=pygame.Vector2(0.01, 0.01), hor_align=HorAlign.LEFT,
                          vert_align=VertAlign.TOP)
        message_to_screen(text="M: TOGGLE MENU", screen=self.screen, fontsize=20,
                          color=WHITE,
                          pose=pygame.Vector2(1, 1), hor_align=HorAlign.RIGHT,
                          vert_align=VertAlign.BOTTOM)

    def _enable_algo_viz_callback(self, val: bool):
        self.is_enable_algo_viz = val

    def _enable_auto_gen_path_callback(self, val: bool):
        self.is_auto_gen_path = val
        if val:
            self.path_sprite = PathSpriteAuto(BSplinePath([], 20, 3, 0, 1), 27, self.glob_to_screen,
                                              self.screen.get_width(),
                                              self.screen.get_height())
        else:
            self.path_sprite = PathSprite(BSplinePath([], 20, 3, 0, 1), self.glob_to_screen)
