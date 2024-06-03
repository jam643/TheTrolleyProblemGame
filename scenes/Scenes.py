from abc import ABC, abstractmethod

from utils.pgutils.pgutils import *
from sprites.CarSprite import CarSprite
from control import ManualControl


class SceneBase(ABC):
    sim_to_real = SimToReal(
        SimToReal.Params(
            pxl_per_meter=40,
            screen_ref_frame_rel_real=math.Pose(0, 0, 0),
            fps=60,
            sim_time_rel_real=2,
        )
    )
    clock = pygame.time.Clock()

    def __init__(self, screen: pygame.Surface):
        super().__init__()
        self.screen = screen
        self.sim_to_real.params.screen_ref_frame_rel_real.y = screen.get_height() / (
            2 * self.sim_to_real.params.pxl_per_meter
        )
        self.next = self
        self.sim_to_real.time_s = 0

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
        self.sim_to_real.update()

    @abstractmethod
    def render(self):
        pass

    # returns time since scene start
    def get_time_s(self) -> float:
        return self.sim_to_real.time_s

    def switch_to_scene(self, next_scene):
        if next_scene is not self:
            self.next = next_scene

    def terminate(self):
        self.switch_to_scene(None)


class ManualDrivingScene(SceneBase):
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)

        self.car_sprite = CarSprite(self.sim_to_real)

        self.manual_control = ManualControl.ManualControl(70 * np.pi / 180, 0.04, 0.1)
        self.steer = None
        # trace_sprite = TraceSprite(screen, sim_to_real)

    def process_input(self, events, pressed_keys):
        self.steer = self.manual_control.update(pressed_keys)

    def update(self):
        self.car_sprite.update(self.steer, self.sim_to_real.sim_dt)
        # trace_sprite.update(car_sprite.z[CarSprite.StateIdx.X], car_sprite.z[CarSprite.StateIdx.Y],
        #                     sim_to_real.sim_dt)

    def render(self):
        self.screen.fill(COLOR1)

        self.car_sprite.draw(self.screen)
        # trace_sprite.draw(screen)
