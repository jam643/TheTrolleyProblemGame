from abc import ABC, abstractmethod
from typing import List
import pygame
from utils.math import Pose


class PathBase(ABC):
    @abstractmethod
    def get_nearest_coord(self, point: pygame.Vector2) -> Pose:
        ...

    @abstractmethod
    def update(self, points: List[pygame.Vector2]):
        ...

    @property
    @abstractmethod
    def path_points(self) -> List[pygame.Vector2]:
        ...
