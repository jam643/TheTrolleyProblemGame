import pygame
from enum import Enum


class HorAlign(Enum):
    LEFT = 0
    CENTER = 1
    RIGHT = 2


class VertAlign(Enum):
    TOP = 0
    CENTER = 1
    BOTTOM = 2


def message_to_screen(text, screen: pygame.Surface, fontsize=12, color: pygame.Color = (0, 0, 0),
                      normalized_pose: pygame.Vector2 = (0, 0), hor_align: HorAlign = HorAlign.CENTER,
                      vert_align: VertAlign = VertAlign.CENTER):
    font_style = pygame.font.Font("font/pixelFont.ttf", fontsize)
    text_surf = font_style.render(text, False, color)
    text_rect = text_surf.get_rect()

    screen_height = screen.get_height()
    screen_width = screen.get_width()

    x = screen_width * normalized_pose.x
    y = screen_height * normalized_pose.y

    text_rect.centery = y

    if vert_align is VertAlign.CENTER:
        text_rect.centery = y
    elif vert_align is VertAlign.TOP:
        text_rect.top = y
    elif vert_align is VertAlign.BOTTOM:
        text_rect.bottom = y

    if hor_align is HorAlign.CENTER:
        text_rect.centerx = x
    elif hor_align is HorAlign.LEFT:
        text_rect.left = x
    elif hor_align is HorAlign.RIGHT:
        text_rect.right = x

    screen.blit(text_surf, text_rect)
