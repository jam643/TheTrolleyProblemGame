import pygame
import pygame_menu
import enum
import subprocess
import numpy as np

from dynamics.Vehicle import Vehicle
from dynamics.CartesianDynamicBicycleModel import CartesianDynamicBicycleModel
from dynamics.kinematic_model import CartesianKinematicBicycleModel
from utils import math
from sprites.CarSprite import CarSprite
from sprites.plot import PgPlot, PlotManager
from utils.pgutils.text import menu_config, v_frame
from control.LowLevelControl import SpeedControl, SteerControl


class MotionModelType(enum.Enum):
    dynamic_model = 0
    kinematic_model = 1


class LowLevelControlFactory:

    def __init__(self, glob_to_screen, screen, vehicle: Vehicle):
        self._current_model_type = model_type

        self.glob_to_screen = glob_to_screen
        self.screen = screen

        self.steer_desired = vehicle.state_cog.delta
        self.steer_rate = vehicle.state_cog.delta_rate
        self.vel = self.vehicle_factory.vehicle_state.state_cog.vx
        self.speed_control = SpeedControl(SpeedControl.Params())
        self.steer_control = SteerControl(SteerControl.Params())

        self._init_menus()

        # plotting
        self.plot_manager = PlotManager(0.1, 0.01, 0.01)
        width = 0.1
        height = 0.15
        self.plot_manager.add_plot("steer",
                                   PgPlot(math.Point(width, height), "STEER [DEG]", screen, [-40, 40], 3000, 20))
        self.plot_manager.add_plot("speed",
                                   PgPlot(math.Point(width, height), "SPEED (COG) [M/S]", screen, [0, 30], 3000, 5))

    def update(self, steer_rate, steer_desired, vel, dt):
        self.vehicle_state = self._motion_model_map[self._current_model_type].update(self.vehicle_state, steer_rate, steer_desired, vel, dt)
        self.car_sprite.update(self.vehicle_state.state_cog)
        return self.vehicle_state

    def draw(self, screen: pygame.Surface):
        self.car_sprite.draw(screen, self.vehicle_state.state_cog)
        if self._draw_plots:
            self.plot_manager.plots["steer"].update(1e3 * self.glob_to_screen.time_s,
                                                    np.rad2deg(self.vehicle_state.state_cog.delta))
            self.plot_manager.plots["speed"].update(1e3 * self.glob_to_screen.time_s,
                                                   self.vehicle_state.vel_cog_mag)
            self.plot_manager.draw_plots(screen)

    def _init_menus(self):
        # init menus/frames
        self.ll_control_menu = menu_config(title="LOW LEVEL CONTROL", screen=self.screen)
        f_ll_control_menu = v_frame(self.screen, self.ll_control_menu)
        self._speed_control_menu = menu_config(title="SPEED CONTROL", screen=self.screen)
        f_speed_control_menu = v_frame(self.screen, self.ll_control_menu)
        self._steer_control_menu = menu_config(title="STEER CONTROL", screen=self.screen)
        f_steer_control_menu = v_frame(self.screen, self._steer_control_menu)

        f_ll_control_menu.pack(self.ll_control_menu.add.button("SPEED CONTROL", self._speed_control_menu))
        f_ll_control_menu.pack(self.ll_control_menu.add.button("STEER CONTROL", self._steer_control_menu))
        f_ll_control_menu.pack(self.ll_control_menu.add.button("BACK", pygame_menu.events.BACK))

        f_speed_control_menu.pack(
            self._vehicle_param_menu.add.range_slider("LF", self.vehicle_state.params.lf, (0.1, 5), 0.1,
                                                      onchange=self._lf_callback))
        f_speed_control_menu.pack(
            self._vehicle_param_menu.add.range_slider("LR", self.vehicle_state.params.lr, (0.1, 5), 0.1,
                                                      onchange=self._lr_callback))
        f_speed_control_menu.pack(
            self._vehicle_param_menu.add.range_slider("MASS", self.vehicle_state.params.m, (100, 1e4), 10,
                                                      onchange=self._m_callback))
        f_speed_control_menu.pack(
            self._vehicle_param_menu.add.range_slider("CF", self.vehicle_state.params.cf, (1e4, 5e5), 1000,
                                                      onchange=self._cf_callback))
        f_speed_control_menu.pack(
            self._vehicle_param_menu.add.range_slider("CR", self.vehicle_state.params.cr, (1e4, 5e5), 1000,
                                                      onchange=self._cr_callback))
        f_speed_control_menu.pack(
            self._vehicle_param_menu.add.range_slider("MAX STEER", np.rad2deg(self.vehicle_state.params.delta_max),
                                                      (0, 90), 5,
                                                      onchange=self._max_steer_callback))
        f_speed_control_menu.pack(self._vehicle_param_menu.add.button("BACK", pygame_menu.events.BACK))

        f_steer_control_menu.pack(self._steer_control_menu.add.dropselect("INTEGRATION", [
            ("EULER", CartesianDynamicBicycleModel.IntScheme.EULER),
            ("RK4", CartesianDynamicBicycleModel.IntScheme.RK4)],
                                                                         default=1,
                                                                         onchange=self._int_scheme_callback))
        f_steer_control_menu.pack(
            self._steer_control_menu.add.dropselect("MODEL", [("DYNAMIC", MotionModelType.dynamic_model),
                                                              ("KINEMATIC", MotionModelType.kinematic_model)],
                                                    default=self._current_model_type.value,
                                                    onchange=self._model_callback))
        f_steer_control_menu.pack(self._steer_control_menu.add.button("BACK", pygame_menu.events.BACK))

    def __del__(self):
        for process in self._subprocess_list:
            process.kill()

    def _lf_callback(self, val):
        self.vehicle_state.params.lf = val

    def _lr_callback(self, val):
        self.vehicle_state.params.lr = val

    def _m_callback(self, val):
        self.vehicle_state.params.m = val

    def _cf_callback(self, val):
        self.vehicle_state.params.cf = val

    def _cr_callback(self, val):
        self.vehicle_state.params.cr = val

    def _max_steer_callback(self, val):
        self.vehicle_state.params.delta_max = np.deg2rad(val)

    def _int_scheme_callback(self, _, int_scheme):
        for _, val in self._motion_model_map.items():
            val._int_scheme = int_scheme

    def _model_callback(self, _, model_type):
        self._current_model_type = model_type

    def _draw_plots_callback(self, val):
        self._draw_plots = val

    def reset_init_pose(self):
        pose_init = self.glob_to_screen.get_pose_glob_from_pxl(
            math.Pose(self.screen.get_width() / 4, self.screen.get_height() / 2, 0))
        vel_init = 10
        self.vehicle_state = Vehicle(params=Vehicle.Params()).build_pose(pose_init).build_vel(vel_init, 0)
        self.car_sprite = CarSprite(self.glob_to_screen, self.vehicle_state.params)
        return self.vehicle_state
