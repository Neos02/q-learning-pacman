import pygame

from pygame.locals import *

from main import SCREEN_WIDTH, load_image


class Pacman(pygame.sprite.Sprite):
    speed = 200
    sprite_scale = 2
    spritesheet = load_image("./images/pacman.png", sprite_scale)
    sprite_size = sprite_scale * 13
    animation_frame_length_ms = 60

    def __init__(self):
        super().__init__()
        self.image = Pacman.spritesheet
        self.image_offset = 0
        self.rect = pygame.Rect(0, 0, Pacman.sprite_size, Pacman.sprite_size)
        self.velocity = (0, 0)
        self.last_frame_update_time = 0

    def draw(self, surface):
        ticks = pygame.time.get_ticks()

        if (ticks - self.last_frame_update_time) >= self.animation_frame_length_ms:
            self.image_offset = (self.image_offset + Pacman.sprite_size) % self.image.get_width()
            self.last_frame_update_time = ticks

        surface.blit(self.spritesheet, (self.rect.left, self.rect.top),
                     (self.image_offset, 0, Pacman.sprite_size, Pacman.sprite_size))

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
