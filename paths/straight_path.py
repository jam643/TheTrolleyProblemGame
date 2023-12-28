import pygame
from paths.PathBase import PathBase
from typing import List, Tuple
from utils.math import Pose


class StraightPath(PathBase):
    def get_pose_at_station(self, station: float) -> Pose:
        return Pose(x=station, y=0.0, theta=0.0)

    def get_curv_at_station(self, station: float) -> float:
        return 0.0

    def get_nearest_pose(self, point: pygame.Vector2) -> Tuple[Pose, float]:
        return Pose(x=point.x, y=0.0, theta=0.0), point.x

    def update(self, points: List[pygame.Vector2]):
        pass

    @property
    def path_points(self) -> List[pygame.Vector2]:
        return []