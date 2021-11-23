import pygame_menu

from scenes.Scenes import SceneBase
from scenes import StartScene
from paths.BSpline import BSplinePath
from utils.pgutils.pgutils import *
from utils.pgutils.text import theme_default, menu_default, message_to_screen, VertAlign, HorAlign, game_font
from sprites.PathSprite import PathSprite
from sprites.PathSpriteAuto import PathSpriteAuto
from sprites.ControlFactory import ControlType, ControlFactory
from factory.vehicle_factory import VehicleFactory
from control import SpeedControl


class SandboxScene(SceneBase):
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        self.glob_to_screen.pxl_per_mtr = 40
        self.control_factory = ControlFactory(self.glob_to_screen, self.screen, ControlType.pure_pursuit)
        self.vehicle_factory = VehicleFactory(self.glob_to_screen, screen)

        menu_theme = pygame_menu.Theme(background_color=(0, 0, 0, 100), widget_font=game_font,
                             widget_background_color=(0, 0, 0, 0),
                             widget_font_color=COLOR6, widget_font_size=18,
                             title=False, title_close_button=False)
        self.menu = menu_default(self.screen, menu_theme, rows=1, columns=8, height=60, position=(50,0), enabled=True)
        self.path_menu = menu_default(self.screen, theme_default(18, widget_alignment=pygame_menu.locals.ALIGN_RIGHT))

        self.is_auto_gen_path = True
        self.path_menu.add.toggle_switch("AUTO GEN PATH", state_text=("OFF", "ON"), default=1,
                                         onchange=self._enable_auto_gen_path_callback)
        self.path_menu.add.button("BACK", pygame_menu.events.BACK)

        self.scene_menu = menu_default(self.screen, theme_default(18, widget_alignment=pygame_menu.locals.ALIGN_RIGHT))
        self.scene_menu.add.button("BACK", pygame_menu.events.BACK)

        self.menu.add.button("PATH TRACKER", self.control_factory.controller_menu)
        self.menu.add.button("VEHICLE", self.vehicle_factory.vehicle_menu)
        self.menu.add.button("PATH", self.path_menu)
        self.menu.add.button("LL CONTROL", self.path_menu)
        self.menu.add.button("SCENE", self.path_menu)
        self.scene_menu.add.toggle_switch("VISUALIZATIONS", state_text=("OFF", "ON"), onchange=self._enable_algo_viz_callback,
                                    default=1)

        def start_scene_callback(): self.next = StartScene.StartScene(self.screen)

        self.menu.add.button("MAIN MENU", start_scene_callback)
        self.is_enable_algo_viz = True

        self.path_sprite = self.path_sprite = PathSpriteAuto(BSplinePath([], 20, 3, 0, 1), 27, self.glob_to_screen,
                                                             self.screen.get_width(),
                                                             self.screen.get_height())

        self.scroll_speed = 17
        self.speed_control = SpeedControl.SpeedControl(station_setpoint=25)
        self.steer = 0
        self.vel = self.vehicle_factory.vehicle_state.state_cog.vx
        # self.trace_sprite = TraceSprite(self.glob_to_screen)

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
            self.vehicle_factory.update(self.steer, self.vel, self.glob_to_screen.sim_dt)
            if self.is_auto_gen_path:
                self.path_sprite.update(self.get_time_s())
                self.glob_to_screen.x_pxl_rel_glob -= 17
            else:
                self.path_sprite.update()
                self.glob_to_screen.x_pxl_rel_glob -= self.scroll_speed * self.glob_to_screen.pxl_per_mtr * self.glob_to_screen.sim_dt * (
                        (pygame.mouse.get_pos()[0] / self.screen.get_width()) - 0.5) * 2

            self.steer = self.control_factory.control.update(self.vehicle_factory.vehicle_state, self.path_sprite.path)
            self.vel = self.speed_control.update(self.vehicle_factory.vehicle_state, self.path_sprite.path,
                                            self.glob_to_screen.sim_dt)
            # self.trace_sprite.update(self.car_sprite.vehicle_state.pose.x,  # TODO direct access from factory/refactor
            #                          self.car_sprite.vehicle_state.pose.y,
            #                          self.glob_to_screen.sim_dt)

    def render(self):
        self.screen.fill(COLOR1)

        self.path_sprite.draw(self.screen)
        self.vehicle_factory.draw(self.screen)
        if self.is_enable_algo_viz:
            self.control_factory.control.draw(self.screen)

        if self.menu.is_enabled():
            self.menu.draw(self.screen)

        message_to_screen(text="FPS: {:.1f}".format(self.clock.get_fps()), screen=self.screen, fontsize=12,
                          color=WHITE,
                          pose=pygame.Vector2(0.01, 0.99), hor_align=HorAlign.LEFT,
                          vert_align=VertAlign.BOTTOM)
        message_to_screen(text="M: TOGGLE MENU", screen=self.screen, fontsize=12,
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
