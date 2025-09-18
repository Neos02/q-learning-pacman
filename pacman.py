import pygame

from pygame.locals import *

from main import SCREEN_WIDTH


class Pacman(pygame.sprite.Sprite):
    speed = 200

    def __init__(self):
        super().__init__()
        self.rect = pygame.Rect(0, 0, 32, 32)
        self.velocity = (0, 0)

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 255, 0), self.rect.center, self.rect.width // 2)

    def move(self, deltatime):
        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_w]:
            self.velocity = (0, -self.speed)

        if pressed_keys[K_a]:
            self.velocity = (-self.speed, 0)

        if pressed_keys[K_s]:
            self.velocity = (0, self.speed)

        if pressed_keys[K_d]:
            self.velocity = (self.speed, 0)

        self.rect.move_ip(self.velocity[0] * deltatime, self.velocity[1] * deltatime)

        # wrap when off the screen horizontally
        if self.rect.right < 0:
            self.rect.move_ip(SCREEN_WIDTH + self.rect.width, 0)

        if self.rect.left > SCREEN_WIDTH:
            self.rect.move_ip(-SCREEN_WIDTH - self.rect.width, 0)
