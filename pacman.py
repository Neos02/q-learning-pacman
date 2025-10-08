import pygame

from pygame.locals import *

from main import SCREEN_WIDTH, load_image
from tile import Tile


class Pacman(pygame.sprite.Sprite):
    speed = 200
    sprite_scale = 2
    spritesheet = load_image("./images/pacman.png", sprite_scale)
    sprite_size = sprite_scale * 13
    animation_frame_length_ms = 60
    transparent_tiles = [Tile.PLAYER_START, Tile.AIR, Tile.SMALL_DOT, Tile.BIG_DOT]

    def __init__(self, start_pos=(0, 0), tilemap=None):
        super().__init__()
        self.start_pos = (start_pos[0] + 2 * Pacman.sprite_scale, start_pos[1] - 2 * Pacman.sprite_scale)
        self.rect = pygame.Rect(0, 0, Pacman.sprite_size, Pacman.sprite_size)
        self.image_rect = self.rect.copy()
        self.image = Pacman.spritesheet.subsurface(self.image_rect)
        self.velocity = (0, 0)
        self.last_frame_update_time = 0
        self.rect.move_ip(*self.start_pos)
        self.tilemap = tilemap
        self.queued_velocity = (0, 0)

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
        h, w = self.tilemap.map.shape
        player_tile_x = self.rect.centerx // self.tilemap.tile_size
        player_tile_y = self.rect.centery // self.tilemap.tile_size

        if 0 <= player_tile_x < w and 0 <= player_tile_y < h:
            if pressed_keys[K_w]:
                self.queued_velocity = (0, -self.speed)

            if pressed_keys[K_a]:
                self.queued_velocity = (-self.speed, 0)

            if pressed_keys[K_s]:
                self.queued_velocity = (0, self.speed)

            if pressed_keys[K_d]:
                self.queued_velocity = (self.speed, 0)

            next_tile_x = int(player_tile_x + self.queued_velocity[0] / self.speed)
            next_tile_y = int(player_tile_y + self.queued_velocity[1] / self.speed)

            if 0 <= next_tile_x < w and 0 <= next_tile_y < h and Tile(
                    self.tilemap.map[next_tile_y, next_tile_x]) in Pacman.transparent_tiles:
                self.velocity = self.queued_velocity

                if self.velocity[0] != 0:
                    self.rect.centery = next_tile_y * self.tilemap.tile_size + self.tilemap.tile_size / 2

                if self.velocity[1] != 0:
                    self.rect.centerx = next_tile_x * self.tilemap.tile_size + self.tilemap.tile_size / 2

        next_position = (self.rect.centerx + self.velocity[0] * deltatime,
                         self.rect.centery + self.velocity[1] * deltatime)

        if not self.has_collision(next_position):
            self.rect.centerx = next_position[0]
            self.rect.centery = next_position[1]

        # wrap when off the screen horizontally
        if self.rect.right < 0:
            self.rect.move_ip(SCREEN_WIDTH + self.rect.width, 0)

        if self.rect.left > SCREEN_WIDTH:
            self.rect.move_ip(-SCREEN_WIDTH - self.rect.width, 0)

    def has_collision(self, next_position):
        if self.tilemap is None:
            return False

        h, w = self.tilemap.map.shape
        player_x = int(next_position[0] // self.tilemap.tile_size)
        player_y = int(next_position[1] // self.tilemap.tile_size)

        if player_y < 0 or player_y >= h or player_x < 0 or player_x >= w:
            return False

        return Tile(self.tilemap.map[player_y, player_x]) not in Pacman.transparent_tiles
