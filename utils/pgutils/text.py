import pygame_menu
import pygame
from enum import Enum
import os

from utils.pgutils.pgutils import *

game_font = os.path.join("utils/pgutils/pixelFont.ttf")


def theme_default(font_size: int, **kwargs) -> pygame_menu.Theme:
    return pygame_menu.Theme(background_color=pygame_menu.themes.TRANSPARENT_COLOR, widget_font=game_font, title_font=game_font, title_font_size=font_size+4,
                             widget_background_color=(0, 0, 0, 0),
                             widget_font_color=COLOR6, widget_font_size=font_size,
                             title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_UNDERLINE_TITLE, title_close_button=False, **kwargs)


def menu_default(screen: pygame.Surface, theme: pygame_menu.Theme, width=None, height=None, enabled: bool = False, title="", **kwargs) -> pygame_menu.Menu:
    if not width:
        width=screen.get_width()
    if not height:
        height=screen.get_height()
    return pygame_menu.Menu(title=title,
                            theme=theme, mouse_motion_selection=True, onclose=pygame_menu.events.RESET,
                            enabled=enabled, width=width, height=height, **kwargs)


def menu_config(screen: pygame.Surface, title="", fontsize=16) -> pygame_menu.Menu:
    return menu_default(screen, theme_default(fontsize, widget_alignment=pygame_menu.locals.ALIGN_LEFT), title=title)


def v_frame(screen: pygame.Surface, menu: pygame_menu.Menu) -> pygame_menu.widgets.Frame:
    return menu.add.frame_v(0.9 * screen.get_width(), 0.9 * screen.get_height())


class HorAlign(Enum):
    LEFT = 0
    CENTER = 1
    RIGHT = 2


class VertAlign(Enum):
    TOP = 0
    CENTER = 1
    BOTTOM = 2


def message_to_screen(text, screen: pygame.Surface, fontsize=12, color: pygame.Color = (0, 0, 0),
                      pose: pygame.Vector2 = pygame.Vector2(0, 0), hor_align: HorAlign = HorAlign.CENTER,
                      vert_align: VertAlign = VertAlign.CENTER, normalize_pose: bool = True):
    font_style = pygame.font.Font(game_font, fontsize)
    text_surf = font_style.render(text, False, color)
    text_rect = text_surf.get_rect()

    if normalize_pose:
        screen_height = screen.get_height()
        screen_width = screen.get_width()

        x = screen_width * pose.x
        y = screen_height * pose.y
    else:
        x = pose.x
        y = pose.y

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
