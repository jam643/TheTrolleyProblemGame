from paths.PathBase import PathBase
from utils.pgutils.pgutils import *
import math
import numpy as np


class PathSpriteAuto:
    def __init__(self, path: PathBase, max_len_path, glob_to_screen: GlobToScreen, screen_width: float, screen_height: float):
        self.glob_to_screen = glob_to_screen
        self.path = path

        self.last_pose = []
        self.spline_timer = pygame.time.get_ticks()
        self.spline_update = 50
        self.mouse_position = None
        self.max_len_path = max_len_path
        self.create_spline_x = 0.9 * screen_width
        self.create_spline_y = 0.6 * screen_height
        self.spline_sin_height = 0.2 * screen_height
        self.spline_period = 2

    def draw(self, screen: pygame.Surface):
        width = 15
        if self.path.spline_list and len(self.path.spline_list) > 2:
            len_spline = len(self.path.spline_list)
            peak = int(0.8 * len_spline)
            path_point_global = self.glob_to_screen.get_pxl_from_glob(self.path.spline_list)
            path_pose_global = [utils.math.Pose(point.x, point.y, self.path.spline_list[idx].theta) for idx, point in
                                enumerate(path_point_global)]
            l1 = [pygame.Vector2(p.x + int(idx / peak * width) * math.sin(p.theta),
                                 p.y + int(idx / peak * width) * math.cos(p.theta)) for idx, p in
                  enumerate(path_pose_global[:peak])]
            l2 = [pygame.Vector2(
                p.x + int((len_spline - peak - idx - 1) / (len_spline - peak) * width) * math.sin(p.theta),
                p.y + int((len_spline - peak - idx - 1) / (len_spline - peak) * width) * math.cos(p.theta)) for idx, p
                  in
                  enumerate(path_pose_global[peak:])]
            l3 = [pygame.Vector2(
                p.x - int((len_spline - peak - idx - 1) / (len_spline - peak) * width) * math.sin(p.theta),
                p.y - int((len_spline - peak - idx - 1) / (len_spline - peak) * width) * math.cos(p.theta)) for idx, p
                  in
                  enumerate(path_pose_global[peak:])]
            l4 = [pygame.Vector2(p.x - int(idx / peak * width) * math.sin(p.theta),
                                 p.y - int(idx / peak * width) * math.cos(p.theta)) for idx, p in
                  enumerate(path_pose_global[:peak])]
            l3.reverse()
            l4.reverse()

            pygame.draw.lines(screen, COLOR4, False, l1 + l2 + l3 + l4, width=2)

    def update(self, time_s):

        spline_sin = self.spline_sin_height * np.cos(time_s*2*np.pi/self.spline_period)
        if (pygame.time.get_ticks() - self.spline_timer) > self.spline_update:
            self.last_pose.append(
                self.glob_to_screen.get_glob_from_pxl(pygame.Vector2(self.create_spline_x, self.create_spline_y + spline_sin)))
            self.spline_timer = pygame.time.get_ticks()
        try:
            self.path.update(self.last_pose + [
                self.glob_to_screen.get_glob_from_pxl(pygame.Vector2(self.create_spline_x, self.create_spline_y + spline_sin))])
            if len(self.last_pose) > self.max_len_path:
                self.last_pose.pop(0)
        except:
            pass
        return None
