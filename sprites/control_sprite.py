from abc import ABC, abstractmethod
import pygame


class ControlSprite(ABC):
    @abstractmethod
    def draw(self, screen: pygame.Surface):
        pass

    @abstractmethod
    def draw_plots(self, screen: pygame.Surface):
        pass
