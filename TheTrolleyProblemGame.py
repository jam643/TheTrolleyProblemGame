#!/usr/bin/env pipenv-shebang

from profilehooks import profile
from pgutils.pgutils import *
from sprites.CarSprite import CarSprite
from sprites.TraceSprite import TraceSprite
from control.ManualControl import ManualControl


@profile
def main():
    # Call this function so the Pygame library can initialize itself
    pygame.init()

    # Create screen
    screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
    glob_to_screen = GlobToScreen(20, 0, SCREEN_HEIGHT / 2, fps=120, play_speed=1)

    # Set the title of the window
    pygame.display.set_caption('Project')

    car_sprite = CarSprite(glob_to_screen)
    steer = ManualControl(70 * np.pi / 180, 0.04, 0.1)
    trace_sprite = TraceSprite(screen, glob_to_screen)

    clock = pygame.time.Clock()
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        start_time = pygame.time.get_ticks()
        # updates
        pressed_keys = pygame.key.get_pressed()
        steer.update(pressed_keys)
        car_sprite.update(steer.steer, glob_to_screen.sim_dt)
        trace_sprite.update(car_sprite.z[CarSprite.StateIdx.X], car_sprite.z[CarSprite.StateIdx.Y],
                            glob_to_screen.sim_dt)
        # print(car_sprite)

        # drawing
        screen.fill(BLACK)

        car_sprite.draw(screen)
        trace_sprite.draw(screen)

        # update screen with what we've drawn
        pygame.display.flip()

        # metrics
        # print('screen refresh [ms]: {:.1f}'.format(1000. / (clock.get_fps() + 0.1)))
        # print('exec time [ms]: {:.1f}'.format(pygame.time.get_ticks() - start_time))

        # Pause
        clock.tick(glob_to_screen.fps)

    pygame.quit()


if __name__ == "__main__":
    main()
