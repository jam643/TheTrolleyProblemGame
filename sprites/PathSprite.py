from paths.PathBase import PathBase
from utils.pgutils.pgutils import *
import math


class PathSprite:
    def __init__(self, sim_to_real: SimToReal):
        self.sim_to_real = sim_to_real

    def draw(self, screen: pygame.Surface, path: PathBase):
        width = 15
        if path.spline_list and len(path.spline_list) > 2:
            len_spline = len(path.spline_list)
            peak = int(0.8 * len_spline)
            path_point_global = [
                self.sim_to_real.get_sim_from_real(spline_pose)
                for spline_pose in path.spline_list
            ]
            path_pose_global = [
                utils.math.Pose(point.x, point.y, path.spline_list[idx].theta)
                for idx, point in enumerate(path_point_global)
            ]
            l1 = [
                pygame.Vector2(
                    p.x + int(idx / peak * width) * math.sin(p.theta),
                    p.y + int(idx / peak * width) * math.cos(p.theta),
                )
                for idx, p in enumerate(path_pose_global[:peak])
            ]
            l2 = [
                pygame.Vector2(
                    p.x
                    + int((len_spline - peak - idx - 1) / (len_spline - peak) * width)
                    * math.sin(p.theta),
                    p.y
                    + int((len_spline - peak - idx - 1) / (len_spline - peak) * width)
                    * math.cos(p.theta),
                )
                for idx, p in enumerate(path_pose_global[peak:])
            ]
            l3 = [
                pygame.Vector2(
                    p.x
                    - int((len_spline - peak - idx - 1) / (len_spline - peak) * width)
                    * math.sin(p.theta),
                    p.y
                    - int((len_spline - peak - idx - 1) / (len_spline - peak) * width)
                    * math.cos(p.theta),
                )
                for idx, p in enumerate(path_pose_global[peak:])
            ]
            l4 = [
                pygame.Vector2(
                    p.x - int(idx / peak * width) * math.sin(p.theta),
                    p.y - int(idx / peak * width) * math.cos(p.theta),
                )
                for idx, p in enumerate(path_pose_global[:peak])
            ]
            l3.reverse()
            l4.reverse()

            pygame.draw.lines(screen, COLOR4, False, l1 + l2 + l3 + l4, width=2)
