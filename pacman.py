import pygame

from pygame.locals import *

from main import SCREEN_WIDTH, load_image


class Pacman(pygame.sprite.Sprite):
    speed = 200
    sprite_scale = 2
    spritesheet = load_image("./images/pacman.png", sprite_scale)
    sprite_size = sprite_scale * 13
    animation_frame_length_ms = 60

    def __init__(self, start_pos=(0, 0)):
        super().__init__()
        self.start_pos = (start_pos[0] + 2 * Pacman.sprite_scale, start_pos[1] - 2 * Pacman.sprite_scale)
        self.rect = pygame.Rect(0, 0, Pacman.sprite_size, Pacman.sprite_size)
        self.image_rect = self.rect.copy()
        self.image = Pacman.spritesheet.subsurface(self.image_rect)
        self.velocity = (0, 0)
        self.last_frame_update_time = 0
        self.rect.move_ip(*self.start_pos)

    def draw(self, surface):
        ticks = pygame.time.get_ticks()

        # make pacman be closed when not moving
        if self.velocity == (0, 0):
            self.image_rect.left = 0
            self.last_frame_update_time = ticks

        if (ticks - self.last_frame_update_time) >= self.animation_frame_length_ms:
            self.image_rect.left = (self.image_rect.left + Pacman.sprite_size) % Pacman.spritesheet.get_width()
            self.image = Pacman.spritesheet.subsurface(self.image_rect)
            self.last_frame_update_time = ticks

            if self.velocity == (0, -self.speed):
                self.image = pygame.transform.rotate(self.image, -90)
            elif self.velocity == (0, self.speed):
                self.image = pygame.transform.rotate(self.image, 90)
            elif self.velocity == (self.speed, 0):
                self.image = pygame.transform.rotate(self.image, 180)

        surface.blit(self.image, self.rect)

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
