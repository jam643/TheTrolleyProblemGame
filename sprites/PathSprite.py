from paths.PathBase import PathBase
from utils.pgutils import *


class PathSprite:
    def __init__(self, path: PathBase, glob_to_screen: GlobToScreen):
        self.glob_to_screen = glob_to_screen
        self.path = path

        self.last_pose = []
        self.drawing = False
        self.spline_timer = pygame.time.get_ticks()
        self.spline_update = 200
        self.mouse_position = None

    def draw(self, screen):
        if self.path.path_points:
            pygame.draw.lines(screen, WHITE, False, self.glob_to_screen.get_pxl_from_glob(self.path.path_points), width=2)

    def update(self, events):
        # todo clean up logic
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                self.mouse_position = pygame.Vector2(pygame.mouse.get_pos())
                if self.drawing and (pygame.time.get_ticks() - self.spline_timer) > self.spline_update:
                    if self.last_pose:
                        if self.last_pose[-1] == self.glob_to_screen.get_glob_from_pxl(
                                pygame.Vector2(self.mouse_position)):
                            break
                    self.last_pose.append(self.glob_to_screen.get_glob_from_pxl(pygame.Vector2(self.mouse_position)))
                    self.spline_timer = pygame.time.get_ticks()
            elif event.type == pygame.MOUSEBUTTONUP:
                self.last_pose = []
                self.drawing = False
                return self
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.drawing = True

        self.path.update(self.last_pose + [self.glob_to_screen.get_glob_from_pxl(self.mouse_position)])
        return None
