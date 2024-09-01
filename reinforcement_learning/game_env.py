from utils.pgutils.pgutils import SimToReal, math
from factory.control_factory import ControlType, ControlFactory
from factory.vehicle_factory import VehicleFactory
from factory.path_factory import PathFactory, PathGenType
from control.LowLevelControl import SpeedControl, SteerControl
from factory.wall_factory import WallFactory
from sprites.health_bar import HealthBar

import gymnasium as gym
import pygame
import numpy as np
from gymnasium import spaces
from dataclasses import dataclass
from typing import Optional
from stable_baselines3.common.env_checker import check_env


class TrolleyProblemGameEnv(gym.Env):
    """Custom Environment that follows gym interface."""

    metadata = {"render_modes": ["human", "none", "save"]}

    @dataclass
    class Params:
        dt: float = 0.5
        max_time: float = 30.0
        desired_speed: float = 0.0
        desired_station: float = 0.0
        max_station: float = 10.0
        max_speed: float = 10.0
        max_acceleration: float = 10.0
        reward_weights: RewWeights = RewWeights()

    def __init__(self, screen: Optional[pygame.Surface] = None, render_mode="none", save_dir=None, params=Params()):
        super().__init__()
        self.render_mode = render_mode
        self.save_dir = save_dir
        self.params = params
        self.screen = screen

        self.action_space = spaces.Box(
            low=-self.params.max_acceleration,
            high=self.params.max_acceleration,
            shape=(1,),
            dtype=np.float32,
        )
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(2,), dtype=np.float32
        )

        self.sim_to_real = SimToReal(
            SimToReal.Params(
                pxl_per_meter=40,
                screen_ref_frame_rel_real=math.Pose(0, 0, 0),
                fps=60,
                sim_time_rel_real=2,
            )
        )
        self.clock = pygame.time.Clock()

        self.sim_to_real.params.pxl_per_meter = 40

        self.start_time = self.sim_to_real.time_s
        self.control_factory = ControlFactory(
            self.sim_to_real, self.screen, ControlType.stanley, draw_plots=False
        )
        self.vehicle_factory = VehicleFactory(
            self.sim_to_real, self.screen, draw_plots=False
        )
        self.path_factory = PathFactory(
            self.sim_to_real, self.screen, PathGenType.auto_gen
        )
        self.health_bar = HealthBar(self.level_params.n_lives)

        self.steer_desired = self.vehicle_factory.vehicle_state.state_cog.delta
        self.steer_rate = self.vehicle_factory.vehicle_state.state_cog.delta_rate
        self.vel = self.vehicle_factory.vehicle_state.state_cog.vx
        self.speed_control = SpeedControl(SpeedControl.Params())
        self.steer_control = SteerControl(SteerControl.Params())

    def step(self, action):
        
