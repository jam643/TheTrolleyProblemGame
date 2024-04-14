import enum

import pygame
import pygame_menu
from abc import ABC, abstractmethod
import numpy as np
import subprocess

from control.ControllerBase import ControllerBase
from control.lqr_path_tracker import LQRPathTrackerBase, KinematicLQRPathTracker, DynamicLQRPathTracker
from sprites.StanleyControlSprite import StanleyControlSprite, StanleyControl
from sprites.PurePursuitSprite import PurePursuitSprite, PurePursuitControl
from sprites.lqr_sprite import LQRSprite
from utils.pgutils.text import menu_config, v_frame
import utils.pgutils.pgutils as utils


class ControlType(enum.Enum):
    pure_pursuit = 0
    stanley = 1
    kinematic_lqr = 2
    dynamic_lqr = 3


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
        self._control = StanleyControlSprite(self._params, glob_to_screen, screen)

        self._menu = menu_config(screen, "STANLEY")
        f_menu = v_frame(screen, self._menu)
        f_menu.pack(self._menu.add.range_slider("K", self._params.k, (0, 5), 0.05, onchange=self._k_callback))
        f_menu.pack(self._menu.add.button("BACK", pygame_menu.events.BACK))

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
        self._control = PurePursuitSprite(self._params, glob_to_screen, screen)

        self._menu = menu_config(screen, "PURE PURSUIT")
        f_menu = v_frame(screen, self._menu)
        f_menu.pack(self._menu.add.range_slider("LOOKAHEAD K", self._params.lookahead_k, (0, 5), 0.05,
                                                onchange=self._lookahead_k_callback))
        f_menu.pack(self._menu.add.button("BACK", pygame_menu.events.BACK))

    @property
    def menu(self) -> pygame_menu.Menu:
        return self._menu

    @property
    def control(self) -> ControllerBase:
        return self._control

    def _lookahead_k_callback(self, val):
        self._params.lookahead_k = val
        self.control.set_params(self._params)


class LQRBuilder(ControlBuilderInterface):
    class LqrEnum(enum.Enum):
        kinematic = KinematicLQRPathTracker
        dynamic = DynamicLQRPathTracker

    def __init__(self, lqr_enum: LqrEnum, glob_to_screen: utils.GlobToScreen, screen: pygame.Surface):
        default_Q = np.zeros((4, 4))
        default_R = np.zeros((1, 1))
        default_Q[0, 0] = 0.1
        default_R[0, 0] = 5.0

        self._params = LQRPathTrackerBase.Params(Q=default_Q, R=default_R, dt=glob_to_screen.sim_dt)
        self._control = LQRSprite(lqr_enum.value(self._params), glob_to_screen, screen)

        self._menu = menu_config(screen, "LQR", fontsize=12)
        f_menu = v_frame(screen, self._menu)

        f_menu.pack(self._menu.add.label("STATE WEIGHTS:"))
        f_menu.pack(self._menu.add.range_slider("CTE", self._params.Q[0, 0], (0, 1), 0.01,
                                                onchange=lambda val: self._update_matrix_param(val, self._params.Q,
                                                                                               self.labels_Q, 0, 0),
                                                font_size=8))
        f_menu.pack(self._menu.add.range_slider("YAW_ERR", self._params.Q[1, 1], (0, 1), 0.01,
                                                onchange=lambda val: self._update_matrix_param(val, self._params.Q,
                                                                                               self.labels_Q, 1, 1),
                                                font_size=8))
        f_menu.pack(self._menu.add.range_slider("CTE_RATE", self._params.Q[2, 2], (0, 1), 0.01,
                                                onchange=lambda val: self._update_matrix_param(val, self._params.Q,
                                                                                               self.labels_Q, 2, 2),
                                                font_size=8))
        f_menu.pack(self._menu.add.range_slider("YAW_ERR_RATE", self._params.Q[3, 3], (0, 1), 0.01,
                                                onchange=lambda val: self._update_matrix_param(val, self._params.Q,
                                                                                               self.labels_Q, 3, 3),
                                                font_size=8))

        f_menu.pack(self._menu.add.label("INPUT WEIGHTS:", padding=(20, 0, 0, 0)))
        f_menu.pack(self._menu.add.range_slider("DELTA", self._params.R[0, 0], (0.1, 20), 0.5,
                                                onchange=lambda val: self._update_matrix_param(val, self._params.R,
                                                                                               self.labels_R, 0, 0),
                                                font_size=8))

        f_menu.pack(self._menu.add.label("MATRICES:", padding=(20, 0, 0, 0)))

        table_Q = self._menu.add.table()
        table_Q.default_cell_padding = 5
        table_Q.default_cell_border_width = 3
        self.labels_Q = self.array_to_label(self._params.Q)
        for r in self.labels_Q:
            table_Q.add_row(list(r))

        table_R = self._menu.add.table()
        table_R.default_cell_padding = 5
        table_R.default_cell_border_width = 3
        self.labels_R = self.array_to_label(self._params.R)
        table_R.add_row(self.labels_R[0, 0])

        fh = self._menu.add.frame_h(width=table_Q.get_width(), height=table_Q.get_height())
        fh.pack(self._menu.add.label("Q="))
        fh.relax()
        fh.pack(table_Q)
        fh.pack(self._menu.add.label("R="))
        fh.pack(table_R)

        f_menu.pack(fh)
        f_menu.pack(self._menu.add.button("BACK", pygame_menu.events.BACK))

    def array_to_label(self, array: np.ndarray):
        label_array = np.ndarray(array.shape, dtype=pygame_menu.widgets.Label)
        for row, col in np.ndindex(array.shape):
            label_array[row, col] = self._menu.add.label(array[row, col])
        return label_array

    def _update_matrix_param(self, val, array, labels, row, col):
        val = round(val, 1)
        array[row, col] = val
        labels[row, col].set_title("{:.1f}".format(val))
        self._control.tracker.set_params(self._params)

    @property
    def menu(self) -> pygame_menu.Menu:
        return self._menu

    @property
    def control(self) -> ControllerBase:
        return self._control


class ControlFactory:
    def __init__(self, glob_to_screen, screen, cont_type: ControlType, draw_plots=True):
        self._control_builder_map = {ControlType.pure_pursuit: PurePursuitBuilder(glob_to_screen, screen),
                                     ControlType.stanley: StanleyControlBuilder(glob_to_screen, screen),
                                     ControlType.kinematic_lqr: LQRBuilder(LQRBuilder.LqrEnum.kinematic, glob_to_screen,
                                                                           screen),
                                     ControlType.dynamic_lqr: LQRBuilder(LQRBuilder.LqrEnum.dynamic, glob_to_screen,
                                                                         screen)}

        self._current_control_type = cont_type
        self._draw_plots = draw_plots
        self._subprocess_list = []

        self.controller_menu = menu_config(title="PATH TRACKER", screen=screen)
        f_controller_menu = v_frame(screen, self.controller_menu)
        f_controller_menu.pack(self.controller_menu.add.dropselect("ALGO", [("PURE PURSUIT", ControlType.pure_pursuit),
                                                                            ("STANLEY", ControlType.stanley),
                                                                            ("KINE. LQR", ControlType.kinematic_lqr),
                                                                            ("DYN. LQR", ControlType.dynamic_lqr)],
                                                                   default=cont_type.value,
                                                                   onchange=self._change_control_callback,
                                                                    selection_box_height=7))
        self.control_algo_settings_button = f_controller_menu.pack(self.controller_menu.add.button("ALGO SETTINGS",
                                                                                                   self._get_menu()))
        f_controller_menu.pack(
            self.controller_menu.add.button("DOCS", action=lambda: self._subprocess_list.append(subprocess.Popen(
                ["pipenv", "run", "jupyter", "notebook",
                 "--MultiKernelManager.default_kernel_name=thetrolleyproblemgame",
                 "./control/docs/Path Tracking Controls.ipynb"], stdout=subprocess.PIPE))))
        f_controller_menu.pack(
            self.controller_menu.add.toggle_switch("SHOW PLOTS", default=self._draw_plots, state_text=("N", "Y"),
                                                   onchange=self._draw_plots_callback, width=80))
        f_controller_menu.pack(self.controller_menu.add.button("BACK", pygame_menu.events.BACK))

    @property
    def control(self) -> ControllerBase:
        return self._control_builder_map[self._current_control_type].control

    def draw(self, screen: pygame.Surface):
        self.control.draw(screen)
        if self._draw_plots:
            self.control.draw_plots(screen)

    def _get_menu(self) -> pygame_menu.Menu:
        return self._control_builder_map[self._current_control_type].menu

    def _change_control_callback(self, _, cont_type):
        self._current_control_type = cont_type
        # hack to dynamically change 'Algo Settings' button menu
        self.control_algo_settings_button._args = (self._get_menu(),)

    def _draw_plots_callback(self, val: bool):
        self._draw_plots = val

    def __del__(self):
        for process in self._subprocess_list:
            process.kill()
