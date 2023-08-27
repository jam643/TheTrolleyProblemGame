import pygame.sprite

from utils.pgutils.pgutils import *
from utils.pgutils import text
from sprites.wall_sprite import WallSprite, DoorSprite
from sprites.CarSprite import CarSprite
from factory.wall_generators import WallGenerator, RandomWallGenerator


class WallFactory:
    def __init__(self, glob_to_screen: GlobToScreen, screen: pygame.Surface, n_walls: int, wall_generator: WallGenerator):
        self.wall_generator = wall_generator.add_callback(self._gen_wall, glob_to_screen)
        self.glob_to_screen = glob_to_screen
        self.n_walls = n_walls

        self.wall_sprites = pygame.sprite.Group()
        self.door_sprites = pygame.sprite.Group()
        self.x_init = screen.get_width()
        self.height = screen.get_height()
        self.wall_counter = 0

    def _gen_wall(self, door_height, door_pose):
        wall_sprite = WallSprite(glob_to_screen=self.glob_to_screen, height=self.height, x_init=self.x_init,
                                 door_height=door_height, door_pose=door_pose)
        self.wall_sprites.add(wall_sprite)
        self.door_sprites.add(
            DoorSprite(glob_to_screen=self.glob_to_screen, height=self.height, x_init=self.x_init,
                       door_height=door_height, door_pose=door_pose, wall_ref=wall_sprite))

    def update(self, car_sprite: CarSprite):
        if self.wall_counter < self.n_walls:
            self.wall_generator()
        self.wall_sprites.update()
        self.door_sprites.update()

        try:
            wall_collided = pygame.sprite.spritecollideany(car_sprite, self.wall_sprites,
                                                           lambda car, wall: pygame.sprite.collide_mask(car, wall))
            door_collided = pygame.sprite.spritecollideany(car_sprite, self.door_sprites)
            if door_collided is not None:
                if not car_sprite.is_colliding:
                    self.wall_counter += 1
                    door_collided.wall_ref.dissolve()
                    if self.wall_counter >= self.n_walls:
                        idx = self.door_sprites.sprites().index(door_collided)
                        if idx < len(self.wall_sprites.sprites()) - 1:
                            [door.kill() for door in self.door_sprites.sprites()[idx + 1:]]
                            [wall.dissolve() for wall in self.wall_sprites.sprites()[idx + 1:]]
                door_collided.kill()
        except:
            return False

        if wall_collided is not None:
            wall_collided.update_image(COLOR4)
            return True

        return False

    def draw(self, screen: pygame.Surface):
        self.wall_sprites.draw(screen)
        text.message_to_screen(text=f"{self.wall_counter}/{self.n_walls} WALLS",
                               screen=screen, fontsize=20,
                               color=text.WHITE,
                               pose=pygame.Vector2(0.01, 0.), hor_align=text.HorAlign.LEFT,
                               vert_align=text.VertAlign.TOP)
