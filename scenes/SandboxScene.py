import pygame_menu

from scenes.Scenes import SceneBase
from utils.pgutils.pgutils import *
from utils.pgutils.text import (
    theme_default,
    menu_default,
    message_to_screen,
    VertAlign,
    HorAlign,
    game_font,
)
from factory.control_factory import ControlType, ControlFactory
from factory.vehicle_factory import VehicleFactory
from factory.path_factory import PathFactory, PathGenType
from control.LowLevelControl import SpeedControl, SteerControl
import utils.pgutils.text as txt


class SandboxScene(SceneBase):
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        self.sim_to_real.params.pxl_per_meter = 40
        self.control_factory = ControlFactory(
            self.sim_to_real, self.screen, ControlType.stanley
        )
        self.vehicle_factory = VehicleFactory(
            self.sim_to_real, self.screen, draw_plots=True
        )
        self.path_factory = PathFactory(
            self.sim_to_real, self.screen, PathGenType.auto_gen
        )

        menu_theme = pygame_menu.Theme(
            background_color=(0, 0, 0, 100),
            widget_font=game_font,
            widget_background_color=(0, 0, 0, 0),
            widget_font_color=COLOR6,
            widget_font_size=18,
            title=False,
            title_close_button=False,
        )
        self.menu = menu_default(
            self.screen,
            menu_theme,
            rows=1,
            columns=8,
            height=60,
            position=(50, 0),
            enabled=True,
        )

        self.menu.add.button("PATH TRACKER", self.control_factory.controller_menu)
        self.menu.add.button("VEHICLE", self.vehicle_factory.vehicle_menu)
        self.menu.add.button("PATH", self.path_factory.menu)
        self.menu.add.button("LL CONTROL", self.path_factory.menu)
        self.menu.add.button("SCENE", self.path_factory.menu)

        def start_scene_callback():
            from scenes import StartScene

            self.next = StartScene.StartScene(self.screen)

        self.menu.add.button("MAIN MENU", start_scene_callback)
        self.is_enable_algo_viz = True
        self.pause_scene = False
        self.scroll_speed_mps = 14
        self.steer_desired = self.vehicle_factory.vehicle_state.state_cog.delta
        self.steer_rate = self.vehicle_factory.vehicle_state.state_cog.delta_rate
        self.vel = self.vehicle_factory.vehicle_state.state_cog.vx
        self.speed_control = SpeedControl(SpeedControl.Params())
        self.steer_control = SteerControl(SteerControl.Params())

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
        self.vehicle_factory.update(
            self.steer_rate, self.steer_desired, self.vel, self.sim_to_real.sim_dt
        )

        path = self.path_factory.update(self.sim_to_real.time_s)
        self.steer_desired = self.control_factory.control.update(
            self.vehicle_factory.vehicle_state, path
        )
        self.steer_rate = self.steer_control.update(
            self.vehicle_factory.vehicle_state,
            self.steer_desired,
            self.sim_to_real.sim_dt,
        )
        self.vel = self.speed_control.update(
            self.vehicle_factory.vehicle_state, path, self.sim_to_real.sim_dt
        )

        if (
            self.path_factory.current_path_gen_type is PathGenType.auto_gen
        ):  # todo move to scene_factory
            self.sim_to_real.params.screen_ref_frame_rel_real.x += (
                self.scroll_speed_mps * self.sim_to_real.sim_dt
            )
        else:
            self.sim_to_real.params.screen_ref_frame_rel_real.x += (
                1.5
                * self.scroll_speed_mps
                * self.sim_to_real.sim_dt
                * ((pygame.mouse.get_pos()[0] / self.screen.get_width()) - 0.5)
                * 2
            )

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

        message_to_screen(
            text="FPS: {:.1f}".format(self.clock.get_fps()),
            screen=self.screen,
            fontsize=12,
            color=WHITE,
            pose=pygame.Vector2(0.01, 0.99),
            hor_align=HorAlign.LEFT,
            vert_align=VertAlign.BOTTOM,
        )
        help_txt = [
            "D: {}".format(
                "DRAW PATH"
                if self.path_factory.current_path_gen_type is PathGenType.auto_gen
                else "GEN PATH"
            ),
            "P: {}".format("PLAY" if self.pause_scene else "PAUSE"),
            "R: RESET CAR",
            "Q: QUIT",
        ]
        for idx, text in enumerate(reversed(help_txt)):
            txt.message_to_screen(
                text=text,
                screen=self.screen,
                fontsize=8,
                color=txt.WHITE,
                pose=pygame.Vector2(1, 1 - idx * 0.025),
                hor_align=txt.HorAlign.RIGHT,
                vert_align=txt.VertAlign.BOTTOM,
            )

    def _enable_algo_viz_callback(self, val: bool):
        self.is_enable_algo_viz = val
