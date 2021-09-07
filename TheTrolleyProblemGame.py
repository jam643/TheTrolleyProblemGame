#!/usr/bin/env pipenv-shebang

from profilehooks import profile
from scenes.Scenes import *
import pygame


@profile
def main():
    # Call this function so the Pygame library can initialize itself
    pygame.init()

    # Set the title of the window
    pygame.display.set_caption('Project')

    flags = pygame.FULLSCREEN
    active_scene = PurePursuiteDrivingScene(pygame.display.set_mode((0, 0), flags=flags))

    while active_scene is not None:
        # process inputs
        pressed_keys = pygame.key.get_pressed()
        active_scene.process_input(events=pygame.event.get(), pressed_keys=pressed_keys)

        # updates
        active_scene.update()

        # render
        active_scene.render()

        pygame.display.flip()

        # metrics
        # print('screen refresh [ms]: {:.1f}'.format(1000. / (clock.get_fps() + 0.1)))
        # print('exec time [ms]: {:.1f}'.format(pygame.time.get_ticks() - start_time))

        # Pause
        active_scene.clock.tick(active_scene.glob_to_screen.fps)

        active_scene = active_scene.next

    pygame.quit()


if __name__ == "__main__":
    main()
