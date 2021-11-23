import enum

import pygame
import pygame_menu
from abc import ABC, abstractmethod

from control.ControllerBase import ControllerBase
from sprites.StanleyControlSprite import StanleyControlSprite, StanleyControl
from sprites.PurePursuitSprite import PurePursuitSprite, PurePursuitControl
from utils.pgutils.text import menu_default, theme_default


class ControlType(enum.Enum):
    pure_pursuit = 0
    stanley = 1


class ControlBuilderInterface(ABC):
    @property
    @abstractmethod
    def menu(self) -> pygame_menu.Menu:
        ...

    @property
    @abstractmethod
    def control(self) -> ControllerBase:
        ...


class StanleyControlBuilder(ControlBuilderInterface):
    def __init__(self, glob_to_screen, screen: pygame.Surface):
        self._params = StanleyControl.Params(1.0)
        self._control = StanleyControlSprite(self._params, glob_to_screen)

        self._menu = menu_default(screen, theme_default(18, widget_alignment=pygame_menu.locals.ALIGN_RIGHT))
        self._menu.add.range_slider("K", self._params.k, (0, 5), 0.05, onchange=self._k_callback)
        self._menu.add.button("BACK", pygame_menu.events.BACK)

    @property
    def menu(self) -> pygame_menu.Menu:
        return self._menu

    @property
    def control(self) -> ControllerBase:
        return self._control

    def _k_callback(self, val):
        self._params.k = val
        self.control.set_params(self._params)


class PurePursuitBuilder(ControlBuilderInterface):
    def __init__(self, glob_to_screen, screen: pygame.Surface):
        self._params = PurePursuitControl.Params(0.7)
        self._control = PurePursuitSprite(self._params, glob_to_screen)

        self._menu = menu_default(screen, theme_default(18, widget_alignment=pygame_menu.locals.ALIGN_RIGHT))
        self._menu.add.range_slider("LOOKAHEAD K", self._params.lookahead_k, (0, 5), 0.05,
                                   onchange=self._lookahead_k_callback)
        self._menu.add.button("BACK", pygame_menu.events.BACK)

    @property
    def menu(self) -> pygame_menu.Menu:
        return self._menu

    @property
    def control(self) -> ControllerBase:
        return self._control

    def _lookahead_k_callback(self, val):
        self._params.lookahead_k = val
        self.control.set_params(self._params)


class ControlFactory:
    def __init__(self, glob_to_screen, screen, cont_type: ControlType):
        self._control_builder_map = {ControlType.pure_pursuit: PurePursuitBuilder(glob_to_screen, screen),
                                     ControlType.stanley: StanleyControlBuilder(glob_to_screen, screen)}

        self._current_control_type = cont_type

        self.controller_menu = menu_default(screen, theme_default(18, widget_alignment=pygame_menu.locals.ALIGN_RIGHT))
        self.controller_menu.add.dropselect("ALGO", [("PURE PURSUIT", ControlType.pure_pursuit),
                                                     ("STANLEY", ControlType.stanley)], default=cont_type.value,
                                            onchange=self._change_control_callback)
        self.control_algo_settings_button = self.controller_menu.add.button("ALGO SETTINGS",
                                                                            self._get_menu())
        self.controller_menu.add.button("BACK", pygame_menu.events.BACK)

    @property
    def control(self) -> ControllerBase:
        return self._control_builder_map[self._current_control_type].control

    def _get_menu(self) -> pygame_menu.Menu:
        return self._control_builder_map[self._current_control_type].menu

    def _change_control_callback(self, _, cont_type):
        self._current_control_type = cont_type
        # hack to dynamically update 'Algo Settings' button menu
        self.control_algo_settings_button._args = (self._get_menu(),)
