from abc import ABC, abstractmethod
from typing import List, Tuple
import pygame
from utils.math import Pose


class PathBase(ABC):

    @abstractmethod
    def get_pose_at_station(self, station: float) -> Pose:
        ...

    @abstractmethod
    def get_curv_at_station(self, station: float) -> float:
        ...

    @abstractmethod
    def get_nearest_pose(self, point: pygame.Vector2) -> Tuple[Pose, float]:
        ...

    @abstractmethod
    def update(self, points: List[pygame.Vector2]):
        ...

    @property
    @abstractmethod
    def path_points(self) -> List[pygame.Vector2]:
        ...
