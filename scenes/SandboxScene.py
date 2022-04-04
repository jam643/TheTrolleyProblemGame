import pygame_menu

from scenes.Scenes import SceneBase
from scenes import StartScene
from utils.pgutils.pgutils import *
from utils.pgutils.text import theme_default, menu_default, message_to_screen, VertAlign, HorAlign, game_font
from factory.control_factory import ControlType, ControlFactory
from factory.vehicle_factory import VehicleFactory
from factory.path_factory import PathFactory, PathGenType
from control import SpeedControl
import utils.pgutils.text as txt


class SandboxScene(SceneBase):
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        self.glob_to_screen.pxl_per_mtr = 40
        self.control_factory = ControlFactory(self.glob_to_screen, self.screen, ControlType.dlqr)
        self.vehicle_factory = VehicleFactory(self.glob_to_screen, self.screen, draw_plots=True)
        self.path_factory = PathFactory(self.glob_to_screen, self.screen, PathGenType.auto_gen)

        menu_theme = pygame_menu.Theme(background_color=(0, 0, 0, 100), widget_font=game_font,
                                       widget_background_color=(0, 0, 0, 0),
                                       widget_font_color=COLOR6, widget_font_size=18,
                                       title=False, title_close_button=False)
        self.menu = menu_default(self.screen, menu_theme, rows=1, columns=8, height=60, position=(50, 0), enabled=True)

        self.menu.add.button("PATH TRACKER", self.control_factory.controller_menu)
        self.menu.add.button("VEHICLE", self.vehicle_factory.vehicle_menu)
        self.menu.add.button("PATH", self.path_factory.menu)
        self.menu.add.button("LL CONTROL", self.path_factory.menu)
        self.menu.add.button("SCENE", self.path_factory.menu)

        def start_scene_callback(): self.next = StartScene.StartScene(self.screen)

        self.menu.add.button("MAIN MENU", start_scene_callback)
        self.is_enable_algo_viz = True
        self.pause_scene = False
        self.scroll_speed_mps = 14
        self.speed_control = SpeedControl.SpeedControl(SpeedControl.SpeedControl.Params())
        self.steer = 0
        self.vel = self.vehicle_factory.vehicle_state.state_cog.vx

    def process_input(self, events, pressed_keys):
        super().process_input(events, pressed_keys)

        if self.menu.is_enabled():
            self.menu.update(events)

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_d:
                if self.path_factory.current_path_gen_type is PathGenType.auto_gen:
                    self.path_factory.set_gen_type(PathGenType.manual_draw)
                    self.menu.disable()
                else:
                    self.path_factory.set_gen_type(PathGenType.auto_gen)
                    self.menu.enable()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.vehicle_factory.reset_init_pose()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                self.pause_scene = not self.pause_scene

    def update(self):
        if self.pause_scene:
            return
        super().update()
        # propagate vehicle with previous control commands
        self.vehicle_factory.update(self.steer, self.vel, self.glob_to_screen.sim_dt)

        path = self.path_factory.update(self.glob_to_screen.time_s)
        self.steer = self.control_factory.control.update(self.vehicle_factory.vehicle_state, path)
        self.vel = self.speed_control.update(self.vehicle_factory.vehicle_state, path,
                                             self.glob_to_screen.sim_dt)

        if self.path_factory.current_path_gen_type is PathGenType.auto_gen:  # todo move to scene_factory
            self.glob_to_screen.x_pxl_rel_glob -= self.scroll_speed_mps * self.glob_to_screen.sim_dt * self.glob_to_screen.pxl_per_mtr
        else:
            self.glob_to_screen.x_pxl_rel_glob -= self.scroll_speed_mps * self.glob_to_screen.pxl_per_mtr * self.glob_to_screen.sim_dt * (
                    (pygame.mouse.get_pos()[0] / self.screen.get_width()) - 0.5) * 2

    def render(self):
        # if self.pause_scene:
        #     return
        self.screen.fill(COLOR1)

        self.path_factory.draw(self.screen)
        self.vehicle_factory.draw(self.screen)
        if self.is_enable_algo_viz:
            self.control_factory.draw(self.screen)

        if self.menu.is_enabled():
            self.menu.draw(self.screen)

        message_to_screen(text="FPS: {:.1f}".format(self.clock.get_fps()), screen=self.screen, fontsize=12,
                          color=WHITE,
                          pose=pygame.Vector2(0.01, 0.99), hor_align=HorAlign.LEFT,
                          vert_align=VertAlign.BOTTOM)
        help_txt = ["D: {}".format(
            "DRAW PATH" if self.path_factory.current_path_gen_type is PathGenType.auto_gen else "GEN PATH"),
            "P: {}".format(
                "PLAY" if self.pause_scene else "PAUSE"), "R: RESET CAR", "Q: QUIT"]
        for idx, text in enumerate(reversed(help_txt)):
            txt.message_to_screen(text=text,
                                  screen=self.screen, fontsize=8,
                                  color=txt.WHITE,
                                  pose=pygame.Vector2(1, 1 - idx * 0.025), hor_align=txt.HorAlign.RIGHT,
                                  vert_align=txt.VertAlign.BOTTOM)

    def _enable_algo_viz_callback(self, val: bool):
        self.is_enable_algo_viz = val
