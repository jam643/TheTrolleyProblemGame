from pgutils.pgutils import *


class TraceSprite(pygame.sprite.Sprite):
    def __init__(self, screen: pygame.Surface, glob_to_screen: GlobToScreen):
        super().__init__()
        self.glob_to_screen = glob_to_screen
        self.screen = screen

        self.trace = []
        self.trace_max_T = 3

        self.image = None
        self.rect = None

    def update(self, x, y, dt):
        self.trace.append(self.glob_to_screen.get_pxl_from_glob(x, y))

        image = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA, 32)
        image = image.convert_alpha()

        if len(self.trace) > int(self.trace_max_T / dt):
            self.trace.pop(0)

        if len(self.trace) > 1:
            pygame.draw.aalines(image, WHITE, False, self.trace)

        self.image = image
        self.rect = image.get_rect()

    def draw(self, screen):
        screen.blit(self.image, self.rect)