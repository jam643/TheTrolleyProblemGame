import pygame.sprite
import pygame_menu
from dataclasses import dataclass
import numpy as np

from scenes.Scenes import SceneBase
from utils.pgutils.pgutils import *
from utils.pgutils.text import theme_default, menu_default, message_to_screen, VertAlign, HorAlign, game_font
from factory.control_factory import ControlType, ControlFactory
from factory.vehicle_factory import VehicleFactory
from factory.path_factory import PathFactory, PathGenType
from control import SpeedControl
from factory.wall_factory import WallFactory
from sprites.health_bar import HealthBar
import utils.pgutils.text as txt
from factory.wall_generators import RandomWallGenerator, WallGenerator, SinWallGenerator


@dataclass
class LevelParams:
    scroll_speed: float
    n_walls: int
    n_lives: int
    wall_generator: WallGenerator


levels_list = [LevelParams(scroll_speed=7, n_walls=4, n_lives=2,
                           wall_generator=RandomWallGenerator(time_range=(2, 4), door_height=1 / 2,
                                                              door_pose_range=(1 / 4, 3 / 4))),
               LevelParams(scroll_speed=7, n_walls=8, n_lives=3,
                           wall_generator=SinWallGenerator(3, 12, 1 / 2, 1 / 2)),
               LevelParams(scroll_speed=6, n_walls=20, n_lives=3,
                           wall_generator=SinWallGenerator(1, 16, 2 / 3, 1 / 3)),
               LevelParams(scroll_speed=8, n_walls=60, n_lives=3,
                           wall_generator=SinWallGenerator(0.3, 12, 2 / 3, 1 / 3)),
               LevelParams(scroll_speed=9, n_walls=60, n_lives=3,
                           wall_generator=SinWallGenerator(0.2, 6, 2 / 3, 1 / 3)),
               LevelParams(scroll_speed=10, n_walls=15, n_lives=3,
                           wall_generator=RandomWallGenerator(time_range=(2, 4), door_height=1 / 3,
                                                              door_pose_range=(1 / 6, 5 / 6)))]


class LevelScene(SceneBase):
    def __init__(self, screen: pygame.Surface, level_idx=0):
        super().__init__(screen)
        self.level_idx = level_idx
        self.level_params = levels_list[self.level_idx]

        self.glob_to_screen.pxl_per_mtr = 40

        self.start_time = self.glob_to_screen.time_s
        self.count_down = 6
        self.control_factory = ControlFactory(self.glob_to_screen, self.screen, ControlType.stanley, draw_plots=False)
        self.vehicle_factory = VehicleFactory(self.glob_to_screen, self.screen, draw_plots=False)
        self.path_factory = PathFactory(self.glob_to_screen, self.screen, PathGenType.manual_draw)
        self.health_bar = HealthBar(self.level_params.n_lives)

        self.speed_control = SpeedControl.SpeedControl(SpeedControl.SpeedControl.Params())
        self.steer = 0
        self.vel = self.vehicle_factory.vehicle_state.state_cog.vx

    def update(self):
        super().update()
        if (self.glob_to_screen.time_s - self.start_time) > self.count_down:
            self.next = GameScene(self.screen, self.level_idx, self.path_factory, self.vehicle_factory,
                                  self.control_factory, self.speed_control, self.health_bar)

        self.vehicle_factory.update(self.steer, self.vel, self.glob_to_screen.sim_dt)

        path = self.path_factory.update(self.glob_to_screen.time_s)
        self.steer = self.control_factory.control.update(self.vehicle_factory.vehicle_state, path)
        self.vel = self.speed_control.update(self.vehicle_factory.vehicle_state, path,
                                             self.glob_to_screen.sim_dt)

        self.glob_to_screen.x_pxl_rel_glob -= self.level_params.scroll_speed * self.glob_to_screen.sim_dt * self.glob_to_screen.pxl_per_mtr

    def render(self):
        self.screen.fill(COLOR1)
        txt.message_to_screen(text=f"LEVEL {self.level_idx + 1}",
                              screen=self.screen, fontsize=50,
                              color=txt.WHITE,
                              pose=pygame.Vector2(0.5, 0.5), hor_align=txt.HorAlign.CENTER,
                              vert_align=txt.VertAlign.CENTER)
        count_down_time = abs(
            self.count_down - (self.glob_to_screen.time_s - self.start_time)) / self.glob_to_screen.play_speed
        txt.message_to_screen(
            text=f"{np.ceil(count_down_time):.0f}",
            screen=self.screen, fontsize=int(50 * (count_down_time % 1) + 10),
            color=txt.WHITE,
            pose=pygame.Vector2(0.5, 0.6), hor_align=txt.HorAlign.CENTER,
            vert_align=txt.VertAlign.CENTER)

        self.path_factory.draw(self.screen)
        self.vehicle_factory.draw(self.screen)
        self.health_bar.draw(self.screen)

    def process_input(self, events, pressed_keys):
        super().process_input(events, pressed_keys)


class GameScene(SceneBase):
    def __init__(self, screen: pygame.Surface, level_idx: int, path_factory, vehicle_factory, control_factory,
                 speed_control, health_bar: HealthBar):
        super().__init__(screen)
        self.level_idx = level_idx
        self.level_params = levels_list[self.level_idx]

        self.glob_to_screen.pxl_per_mtr = 40
        self.control_factory = control_factory
        self.vehicle_factory = vehicle_factory
        self.path_factory = path_factory
        self.health_bar = health_bar

        menu_theme = txt.theme_default(40)
        self.menu = menu_default(self.screen, menu_theme, enabled=False)

        def start_scene_callback():
            from scenes import StartScene
            self.next = StartScene.StartScene(self.screen)

        def restart_callback():
            self.next = LevelScene(self.screen, self.level_idx)

        self.menu.add.button("MAIN MENU", start_scene_callback)
        self.menu.add.button("RESTART", restart_callback)
        self.pause_scene = False
        self.speed_control = speed_control
        self.steer = 0
        self.vel = self.vehicle_factory.vehicle_state.state_cog.vx

        self.wall_factory = WallFactory(glob_to_screen=self.glob_to_screen, screen=screen,
                                        n_walls=self.level_params.n_walls,
                                        wall_generator=self.level_params.wall_generator)

    def process_input(self, events, pressed_keys):
        super().process_input(events, pressed_keys)

        if self.menu.is_enabled():
            self.menu.update(events)

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                self.pause_scene = not self.pause_scene
                if self.pause_scene:
                    self.menu.enable()
                else:
                    self.menu.disable()

    def update(self):
        if self.pause_scene:
            return
        super().update()

        if self.health_bar.lives <= 0 and not self.vehicle_factory.car_sprite.is_colliding:
            self.next = LevelScene(self.screen, self.level_idx)

        colliding = self.wall_factory.update(self.vehicle_factory.car_sprite)
        if not self.wall_factory.wall_sprites and self.wall_factory.wall_counter >= self.level_params.n_walls:
            if len(levels_list) > self.level_idx + 1:
                self.next = LevelScene(self.screen, self.level_idx + 1)
            else:
                from scenes import StartScene
                self.next = StartScene.StartScene(self.screen)

        # propagate vehicle with previous control commands
        if colliding:
            if not self.vehicle_factory.car_sprite.is_colliding:
                self.health_bar -= 1
            self.vehicle_factory.car_sprite.set_colliding()
        self.vehicle_factory.update(self.steer, self.vel, self.glob_to_screen.sim_dt)

        if self.vehicle_factory.car_sprite.rect.left < 0:
            self.vehicle_factory.car_sprite.rect.left = 0

        path = self.path_factory.update(self.glob_to_screen.time_s)
        self.steer = self.control_factory.control.update(self.vehicle_factory.vehicle_state, path)
        self.vel = self.speed_control.update(self.vehicle_factory.vehicle_state, path,
                                             self.glob_to_screen.sim_dt)

        self.glob_to_screen.x_pxl_rel_glob -= self.level_params.scroll_speed * self.glob_to_screen.sim_dt * self.glob_to_screen.pxl_per_mtr

    def render(self):
        # if self.pause_scene:
        #     return
        self.screen.fill(COLOR1)

        self.path_factory.draw(self.screen)
        self.wall_factory.draw(self.screen)
        self.vehicle_factory.draw(self.screen)
        self.health_bar.draw(self.screen)

        if self.menu.is_enabled():
            self.menu.draw(self.screen)

        message_to_screen(text="FPS: {:.1f}".format(self.clock.get_fps()), screen=self.screen, fontsize=12,
                          color=WHITE,
                          pose=pygame.Vector2(0.01, 0.99), hor_align=HorAlign.LEFT,
                          vert_align=VertAlign.BOTTOM)
        message_to_screen(text=f"LEVEL {self.level_idx + 1}",
                          screen=self.screen, fontsize=20,
                          color=WHITE,
                          pose=pygame.Vector2(0.5, 0.), hor_align=HorAlign.CENTER,
                          vert_align=VertAlign.TOP)
        help_txt = ["P: {}".format(
            "PLAY" if self.pause_scene else "PAUSE"), "Q: QUIT"]
        for idx, text in enumerate(reversed(help_txt)):
            txt.message_to_screen(text=text,
                                  screen=self.screen, fontsize=8,
                                  color=txt.WHITE,
                                  pose=pygame.Vector2(1, 1 - idx * 0.025), hor_align=txt.HorAlign.RIGHT,
                                  vert_align=txt.VertAlign.BOTTOM)
