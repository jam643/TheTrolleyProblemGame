import pygame
import utils.pgutils.pgutils as pgutils


class WallSprite(pygame.sprite.Sprite):
    def __init__(self, glob_to_screen: pgutils.GlobToScreen, height: float, x_init: int, door_height,
                 door_pose):
        pygame.sprite.Sprite.__init__(self)

        self.glob_to_screen = glob_to_screen
        self.door_height = door_height
        self.door_pose = door_pose
        self.is_dissolving = False
        self.width = 50
        self.height = height
        self.image = pygame.Surface([self.width, self.height])
        self.update_image(pgutils.COLOR3)
        self.rect = self.image.get_rect()
        self.rect.x = x_init
        self.pose = self.glob_to_screen.get_glob_from_pxl(pygame.Vector2(self.rect.x, self.rect.y))

    def update_image(self, color):
        self.image.fill(color)
        self.image.set_colorkey(pgutils.BLACK)

        if self.is_dissolving:
            self.door_height += self.glob_to_screen.sim_dt / 0.7
            self.door_height = min(self.door_height, 2)
        pygame.draw.rect(self.image, pgutils.BLACK,
                         pygame.rect.Rect(0, (self.door_pose - self.door_height / 2) * self.height, self.width,
                                          self.height * self.door_height))

    def update(self):
        self.update_image(pgutils.COLOR3)
        pose_screen = self.glob_to_screen.get_pxl_from_glob(self.pose)
        self.rect.x = pose_screen.x
        if self.rect.bottomright[0] < 0:
            self.kill()

    def dissolve(self):
        self.is_dissolving = True


class DoorSprite(pygame.sprite.Sprite):
    def __init__(self, glob_to_screen: pgutils.GlobToScreen, height: float, x_init: int, door_height,
                 door_pose, wall_ref):
        pygame.sprite.Sprite.__init__(self)

        self.glob_to_screen = glob_to_screen
        self.door_height = door_height
        self.door_pose = door_pose
        self.wall_ref = wall_ref
        self.width = 10
        self.height = height
        self.image = pygame.Surface([self.width, self.door_height * self.height])
        self.image.fill(pgutils.BLACK)
        # self.update_image(pgutils.COLOR7)
        self.rect = self.image.get_rect(centery=self.door_pose * self.height)
        self.rect.x = x_init + 40
        self.pose = self.glob_to_screen.get_glob_from_pxl(pygame.Vector2(self.rect.x, self.rect.y))

    def update_image(self, color):
        self.image.fill(pgutils.BLACK)
        self.image.set_colorkey(pgutils.BLACK)
        pygame.draw.rect(self.image, color,
                         pygame.rect.Rect(0, (self.door_pose - self.door_height / 2) * self.height, self.width,
                                          self.height * self.door_height))

    def update(self):
        # self.update_image(pgutils.COLOR7)
        pose_screen = self.glob_to_screen.get_pxl_from_glob(self.pose)
        self.rect.x = pose_screen.x
        if self.rect.bottomright[0] < 0:
            self.kill()
