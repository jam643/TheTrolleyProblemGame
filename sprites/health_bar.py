import pygame


class HealthBar(pygame.sprite.Sprite):
    def __init__(self, n_lives: int):
        pygame.sprite.Sprite.__init__(self)

        self.lives = n_lives
        self.image = pygame.image.load('sprites/images/heart.png').convert()
        self.image.set_colorkey((1, 1, 1))
        self.rect = self.image.get_rect()

        self.buffer = pygame.Vector2(10, 10)

    def __isub__(self, other: int):
        self.lives -= other
        return self

    def draw(self, screen: pygame.Surface):
        self.rect.topright = (screen.get_width() - self.buffer.x, self.buffer.y)
        for i in range(self.lives):
            screen.blit(self.image, self.rect)
            self.rect.x -= self.buffer.x + self.rect.width
