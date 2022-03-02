from paths.PathBase import PathBase
from utils.pgutils.pgutils import *
import math


class PathSprite:
    def __init__(self, glob_to_screen: GlobToScreen):
        self.glob_to_screen = glob_to_screen

    def draw(self, screen: pygame.Surface, path: PathBase):
        width = 15
        if path.spline_list and len(path.spline_list) > 2:
            len_spline = len(path.spline_list)
            peak = int(0.8 * len_spline)
            path_point_global = self.glob_to_screen.get_pxl_from_glob(path.spline_list)
            path_pose_global = [utils.math.Pose(point.x, point.y, path.spline_list[idx].theta) for idx, point in
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

            pygame.draw.lines(screen, COLOR4, False, l1 + l2 + l3 + l4, width=2)

            # points_global = self.glob_to_screen.get_pxl_from_glob(path.points)
            # pygame.draw.lines(screen, COLOR4, False, path_point_global, width=2)
            # pygame.draw.lines(screen, COLOR4, False, points_global, width=2)
