import enum

from control.ControllerBase import ControllerBase
from sprites.StanleyControlSprite import StanleyControlSprite, StanleyControl
from sprites.PurePursuitSprite import PurePursuitSprite, PurePursuitControl


class ControlType(enum.Enum):
    pure_pursuit = 1
    stanley = 2


class ControlFactory:
    def __init__(self, glob_to_screen):
        self.glob_to_screen = glob_to_screen

    def create_control(self, type: ControlType) -> ControllerBase:
        if type is ControlType.pure_pursuit:
            return PurePursuitSprite(glob_to_screen=self.glob_to_screen, params=PurePursuitControl.Params(0.7))
        elif type is ControlType.stanley:
            return StanleyControlSprite(glob_to_screen=self.glob_to_screen, params=StanleyControl.Params(1.0))
