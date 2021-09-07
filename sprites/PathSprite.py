from paths.PathBase import PathBase
from utils.pgutils import *
import math


class PathSprite:
    def __init__(self, path: PathBase, glob_to_screen: GlobToScreen):
        self.glob_to_screen = glob_to_screen
        self.path = path

        self.last_pose = []
        self.drawing = False
        self.spline_timer = pygame.time.get_ticks()
        self.spline_update = 50
        self.mouse_position = None
        self.N = 40

    def draw(self, screen: pygame.Surface):
        width = 15
        if self.path.spline_list and len(self.path.spline_list) > 2:
            len_spline = len(self.path.spline_list)
            peak = int(0.8 * len_spline)
            path_point_global = self.glob_to_screen.get_pxl_from_glob(self.path.spline_list)
            path_pose_global = [utils.math.Pose(point.x, point.y, self.path.spline_list[idx].theta) for idx, point in
                                enumerate(path_point_global)]
            l1 = [pygame.Vector2(p.x + int(idx/peak*width) * math.sin(p.theta),
                                 p.y + int(idx/peak*width) * math.cos(p.theta)) for idx, p in
                  enumerate(path_pose_global[:peak])]
            l2 = [pygame.Vector2(p.x + int((len_spline - peak - idx-1)/(len_spline - peak)*width) * math.sin(p.theta),
                                 p.y + int((len_spline - peak - idx-1)/(len_spline - peak)*width) * math.cos(p.theta)) for idx, p in
                  enumerate(path_pose_global[peak:])]
            l3 = [pygame.Vector2(p.x - int((len_spline - peak - idx-1)/(len_spline - peak)*width) * math.sin(p.theta),
                                 p.y - int((len_spline - peak - idx-1)/(len_spline - peak)*width) * math.cos(p.theta)) for idx, p in
                  enumerate(path_pose_global[peak:])]
            l4 = [pygame.Vector2(p.x - int(idx/peak*width) * math.sin(p.theta),
                                 p.y - int(idx/peak*width) * math.cos(p.theta)) for idx, p in
                  enumerate(path_pose_global[:peak])]
            l3.reverse()
            l4.reverse()
            # screen2 = pygame.Surface(screen.get_size())
            pygame.draw.lines(screen, COLOR4, False, l1 + l2 + l3 + l4, width=2)
            # pygame.draw.lines(screen2, (20, 20, 20), False, l1 + l2 + l3 + l4, width=15)
            # screen.blit(screen2, screen2.get_rect(), special_flags=pygame.BLEND_RGB_ADD)
            # steps = 50
            # len_path = len(self.path.path_points)
            # for i in range(steps):
            #     pygame.draw.lines(screen, WHITE, False, self.glob_to_screen.get_pxl_from_glob(
            #         self.path.path_points[math.floor(i / steps * len_path):math.ceil((i+1) / steps * len_path)]), width=i)

    def update(self, events):
        # todo clean up logic

        self.mouse_position = pygame.Vector2(pygame.mouse.get_pos())
        if (pygame.time.get_ticks() - self.spline_timer) > self.spline_update:
            self.last_pose.append(self.glob_to_screen.get_glob_from_pxl(pygame.Vector2(self.mouse_position)))
            self.spline_timer = pygame.time.get_ticks()
        try:
            self.path.update(self.last_pose + [self.glob_to_screen.get_glob_from_pxl(self.mouse_position)])
            if len(self.last_pose) > self.N:
                self.last_pose.pop(0)
        except:
            pass
        return None
