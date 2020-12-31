import pygame

class ManualControl:
    def __init__(self, rwa_setpoint, p_rise, p_fall):
        super().__init__()
        self.steer = 0
        self.rwa_setpoint = rwa_setpoint
        self.p_rise = p_rise
        self.p_fall = p_fall

    def update(self, pressed_keys):
        if pressed_keys[pygame.K_RIGHT]:
            self.steer += self.p_rise * (-self.rwa_setpoint - self.steer)
        if pressed_keys[pygame.K_LEFT]:
            self.steer += self.p_rise * (self.rwa_setpoint - self.steer)

        if (not pressed_keys[pygame.K_LEFT]) and (not pressed_keys[pygame.K_RIGHT]):
            self.steer += -self.p_fall * self.steer
