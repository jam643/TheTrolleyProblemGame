import pygame_menu

from scenes.Scenes import SceneBase
from scenes.SandboxScene import SandboxScene
from utils.pgutils.pgutils import *
from utils.pgutils.text import theme_default, menu_default, message_to_screen, VertAlign, HorAlign
from factory.control_factory import ControlFactory, ControlType
from factory.vehicle_factory import VehicleFactory
from factory.path_factory import PathFactory, PathGenType
from control import SpeedControl


class StartScene(SceneBase):
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        self.glob_to_screen.pxl_per_mtr = 50

        self.control_factory = ControlFactory(glob_to_screen=self.glob_to_screen, screen=self.screen, cont_type=ControlType.pure_pursuit)
        self.vehicle_factory = VehicleFactory(self.glob_to_screen, screen)
        self.path_factory = PathFactory(self.glob_to_screen, self.screen, PathGenType.auto_gen)
        self.menu = menu_default(self.screen, theme_default(50), enabled=True)

        def sandbox_callback():
            self.next = SandboxScene(self.screen)
        self.menu.add.button("PLAY")
        self.menu.add.button("SANDBOX", sandbox_callback)
        self.menu.add.button("QUIT", pygame_menu.events.EXIT)

        self.scroll_speed = 10
        self.steer = 0
        self.vel = self.vehicle_factory.vehicle_state.state_cog.vx
        self.speed_control = SpeedControl.SpeedControl(SpeedControl.SpeedControl.Params())

    def process_input(self, events, pressed_keys):
        super().process_input(events, pressed_keys)
        self.menu.update(events)

    def update(self):
        self.vehicle_factory.update(self.steer, self.vel, self.glob_to_screen.sim_dt)
        path = self.path_factory.update(self.get_time_s())
        self.glob_to_screen.x_pxl_rel_glob -= self.scroll_speed * self.glob_to_screen.pxl_per_mtr * self.glob_to_screen.sim_dt
        self.steer = self.control_factory.control.update(self.vehicle_factory.vehicle_state, path)
        self.vel = self.speed_control.update(self.vehicle_factory.vehicle_state, path,
                                                       self.glob_to_screen.sim_dt)

    def render(self):
        self.screen.fill(COLOR1)

        self.path_factory.draw(self.screen)
        self.vehicle_factory.draw(self.screen)
        self.menu.draw(self.screen)

        message_to_screen(text="FPS: {:.1f}".format(self.clock.get_fps()), screen=self.screen, fontsize=12,
                          color=WHITE,
                          pose=pygame.Vector2(0.01, 0.99), hor_align=HorAlign.LEFT,
                          vert_align=VertAlign.BOTTOM)
