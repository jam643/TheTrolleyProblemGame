import pygame
import pygame_menu
from abc import ABC, abstractmethod
from enum import Enum

from sprites.PathSprite import PathSprite
from paths.BSpline import BSplinePath
from paths.PathBase import PathBase
import paths.path_generator as path_gen
import utils.pgutils.text as txt


class PathGenType(Enum):
    auto_gen = 0
    manual_draw = 1


class PathGenBuilderInterface(ABC):
    @property
    @abstractmethod
    def menu(self) -> pygame_menu.Menu: ...

    @property
    @abstractmethod
    def path_generator(self) -> path_gen.PathGeneratorBase: ...


class PathAutoGenBuilder(PathGenBuilderInterface):
    def __init__(self, sim_to_real, screen: pygame.Surface):
        self._params = path_gen.PathAutoGenerator.Params()
        self._path_gen = path_gen.PathAutoGenerator(
            self._params, sim_to_real, screen.get_width(), screen.get_height()
        )

        self._menu = txt.menu_config(screen, "PATH AUTO GEN")
        f_menu = txt.v_frame(screen, self._menu)
        f_menu.pack(
            self._menu.add.range_slider(
                "PATH LEN",
                self._params.max_path_length,
                (5, 30),
                1,
                onchange=self._len_callback,
            )
        )
        f_menu.pack(
            self._menu.add.range_slider(
                "SIN PERIOD",
                self._params.sin_period,
                (0.5, 5),
                0.1,
                onchange=self._sin_period_callback,
            )
        )
        f_menu.pack(
            self._menu.add.range_slider(
                "SIN HEIGHT",
                self._params.sin_height,
                (0.05, 1),
                0.05,
                onchange=self._sin_height_callback,
            )
        )
        f_menu.pack(self._menu.add.button("BACK", pygame_menu.events.BACK))

    @property
    def path_generator(self) -> path_gen.PathGeneratorBase:
        return self._path_gen

    @property
    def menu(self) -> pygame_menu.Menu:
        return self._menu

    def _len_callback(self, val):
        self._params.max_path_length = val
        self._path_gen.set_params(self._params)

    def _sin_period_callback(self, val):
        self._params.sin_period = val
        self._path_gen.set_params(self._params)

    def _sin_height_callback(self, val):
        self._params.sin_height = val
        self._path_gen.set_params(self._params)


class PathManualGenBuilder(PathGenBuilderInterface):
    def __init__(self, sim_to_real, screen: pygame.Surface):
        self._params = path_gen.PathManualGenerator.Params()
        self._path_gen = path_gen.PathManualGenerator(self._params, sim_to_real)

        self._menu = txt.menu_config(screen, "PATH MANUAL GEN")
        f_menu = txt.v_frame(screen, self._menu)
        f_menu.pack(
            self._menu.add.range_slider(
                "PATH LEN",
                self._params.max_path_length,
                (5, 30),
                1,
                onchange=self._len_callback,
            )
        )
        f_menu.pack(self._menu.add.button("BACK", pygame_menu.events.BACK))

    @property
    def path_generator(self) -> path_gen.PathGeneratorBase:
        return self._path_gen

    @property
    def menu(self) -> pygame_menu.Menu:
        return self._menu

    def _len_callback(self, val):
        self._params.max_path_length = val
        self._path_gen.set_params(self._params)


class PathFactory:
    # todo split sprite/gen
    # todo map for gen type
    def __init__(self, sim_to_real, screen, path_gen_type: PathGenType):
        self.sim_to_real = sim_to_real
        self.screen = screen
        self.current_path_gen_type = path_gen_type

        self.path = BSplinePath([], 11, 3, 0, 4)

        # todo builders
        self._path_generator = {
            PathGenType.auto_gen: PathAutoGenBuilder(self.sim_to_real, self.screen),
            PathGenType.manual_draw: PathManualGenBuilder(
                self.sim_to_real, self.screen
            ),
        }

        self._path_sprite = self.path_sprite = PathSprite(self.sim_to_real)

        self.menu = txt.menu_config(self.screen, "PATH")
        menu_vframe = txt.v_frame(self.screen, self.menu)
        menu_vframe.pack(
            self.menu.add.button(
                "MANUAL GEN PARAMS", self._path_generator[PathGenType.manual_draw].menu
            )
        )
        menu_vframe.pack(
            self.menu.add.button(
                "AUTO GEN PARAMS", self._path_generator[PathGenType.auto_gen].menu
            )
        )
        menu_vframe.pack(self.menu.add.button("BACK", pygame_menu.events.BACK))

    def update(self, time_s) -> PathBase:
        self.path = self._path_generator[
            self.current_path_gen_type
        ].path_generator.update(self.path, time_s)
        return self.path

    def draw(self, screen):
        self.path_sprite.draw(screen, self.path)

    def set_gen_type(self, type: PathGenType):
        self.current_path_gen_type = type
        if type is PathGenType.auto_gen:
            self.path = BSplinePath([], 15, 3, 0, 1)
        elif type is PathGenType.manual_draw:
            self.path = BSplinePath([], 15, 3, 0, 1)
        else:
            raise ValueError("unknown pathgen type")
