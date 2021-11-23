import pygame
import pygame_menu
import enum

from dynamics.Vehicle import Vehicle
from dynamics.CartesianDynamicBicycleModel import CartesianDynamicBicycleModel
from dynamics.kinematic_model import CartesianKinematicBicycleModel
from utils import math
from sprites.CarSprite import CarSprite
from utils.pgutils.text import menu_default, theme_default


class MotionModelType(enum.Enum):
    dynamic_model = 0
    kinematic_model = 1


class VehicleFactory:

    def __init__(self, glob_to_screen, screen, model_type: MotionModelType = MotionModelType.dynamic_model):
        self._current_model_type = model_type

        self.glob_to_screen = glob_to_screen
        self.screen = screen
        self.vehicle_state = self._reset_init_pose()
        self.car_sprite = CarSprite(glob_to_screen, self.vehicle_state.params)

        self._motion_model_map = {MotionModelType.dynamic_model: CartesianDynamicBicycleModel(),
                                  MotionModelType.kinematic_model: CartesianKinematicBicycleModel()}

        self.vehicle_menu = menu_default(screen, theme_default(18, widget_alignment=pygame_menu.locals.ALIGN_RIGHT))
        self._vehicle_param_menu = menu_default(screen,
                                                theme_default(18, widget_alignment=pygame_menu.locals.ALIGN_RIGHT))
        self._motion_model_menu = menu_default(screen,
                                               theme_default(18, widget_alignment=pygame_menu.locals.ALIGN_RIGHT))
        self.vehicle_menu.add.button("VEHICLE PARAMS", self._vehicle_param_menu)
        self.vehicle_menu.add.button("MOTION MODEL", self._motion_model_menu)
        self.vehicle_menu.add.button("RESET VEHICLE", action=self._reset_init_pose)
        self.vehicle_menu.add.button("BACK", pygame_menu.events.BACK)
        self._vehicle_param_menu.add.range_slider("lf", self.vehicle_state.params.lf, (0.1, 5), 0.1,
                                                  onchange=self._lf_callback)
        self._vehicle_param_menu.add.range_slider("lr", self.vehicle_state.params.lr, (0.1, 5), 0.1,
                                                  onchange=self._lr_callback)
        self._vehicle_param_menu.add.range_slider("mass", self.vehicle_state.params.m, (100, 1e4), 10,
                                                  onchange=self._m_callback)
        self._vehicle_param_menu.add.range_slider("cf", self.vehicle_state.params.cf, (1e4, 5e5), 1000,
                                                  onchange=self._cf_callback)
        self._vehicle_param_menu.add.range_slider("cr", self.vehicle_state.params.cr, (1e4, 5e5), 1000,
                                                  onchange=self._cr_callback)
        self._vehicle_param_menu.add.button("BACK", pygame_menu.events.BACK)

        self._motion_model_menu.add.dropselect("INTEGRATION", [("EULER", CartesianDynamicBicycleModel.IntScheme.EULER),
                                                               ("RK4", CartesianDynamicBicycleModel.IntScheme.RK4)],
                                               default=1,
                                               onchange=self._int_scheme_callback)
        self._motion_model_menu.add.dropselect("MODEL", [("DYNAMIC", MotionModelType.dynamic_model),
                                                         ("KINEMATIC", MotionModelType.kinematic_model)],
                                               default=self._current_model_type.value,
                                               onchange=self._model_callback)
        self._motion_model_menu.add.button("BACK", pygame_menu.events.BACK)

    def update(self, steer, vel, dt):
        self.vehicle_state = self._motion_model_map[self._current_model_type].update(self.vehicle_state, steer, vel, dt)
        return self.vehicle_state

    def draw(self, screen: pygame.Surface):
        self.car_sprite.draw(screen, self.vehicle_state.state_cog)

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

    def _int_scheme_callback(self, _, int_scheme):
        for _, val in self._motion_model_map.items():
            val._int_scheme = int_scheme

    def _model_callback(self, _, model_type):
        self._current_model_type = model_type

    def _reset_init_pose(self):
        pose_init = self.glob_to_screen.get_pose_glob_from_pxl(
            math.Pose(self.screen.get_width() / 2, self.screen.get_height() / 2, 0))
        vel_init = 10
        self.vehicle_state = Vehicle().build_pose(pose_init).build_vel(vel_init, 0)
        return self.vehicle_state
