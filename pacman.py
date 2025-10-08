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
        current_tile_x, current_tile_y = self._get_tile_coordinates(self.rect.centerx, self.rect.centery)

        # only allow input when player is on screen
        if self._is_in_bounds(current_tile_x, current_tile_y):
            self._handle_input()

            queued_tile_x = int(current_tile_x + self.queued_velocity[0] / self.speed)
            queued_tile_y = int(current_tile_y + self.queued_velocity[1] / self.speed)

            if self._is_in_bounds(queued_tile_x, queued_tile_y) and \
                    self._get_tile(queued_tile_x, queued_tile_y) in Pacman.transparent_tiles:
                self.velocity = self.queued_velocity
                self._realign(self.velocity[0] == 0, self.velocity[1] == 0)

        self._handle_collisions_and_update_position((
            self.rect.centerx + self.velocity[0] * deltatime,
            self.rect.centery + self.velocity[1] * deltatime
        ))

        # wrap when off the screen horizontally
        if self.rect.right < 0:
            self.rect.move_ip(SCREEN_WIDTH + self.rect.width, 0)

        if self.rect.left > SCREEN_WIDTH:
            self.rect.move_ip(-SCREEN_WIDTH - self.rect.width, 0)

    def _handle_collisions_and_update_position(self, position):
        if not self._has_collision(position):
            self.rect.centerx = position[0]
            self.rect.centery = position[1]
        else:
            self._realign()
            self.velocity = (0, 0)
            self.queued_velocity = (0, 0)

    def _has_collision(self, position):
        if self.tilemap is None:
            return False

        current_tile_x, current_tile_y = self._get_tile_coordinates(position[0], position[1])

        if self._is_in_bounds(current_tile_x, current_tile_y):
            return self._get_tile(current_tile_x, current_tile_y) not in Pacman.transparent_tiles

        return False

    def _get_tile_coordinates(self, center_x, center_y):
        return int(center_x // self.tilemap.tile_size), int(center_y // self.tilemap.tile_size)

    def _handle_input(self):
        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_w]:
            self.queued_velocity = (0, -self.speed)

        if pressed_keys[K_a]:
            self.queued_velocity = (-self.speed, 0)

        if pressed_keys[K_s]:
            self.queued_velocity = (0, self.speed)

        if pressed_keys[K_d]:
            self.queued_velocity = (self.speed, 0)

    def _realign(self, realign_x=True, realign_y=True):
        current_tile_x, current_tile_y = self._get_tile_coordinates(self.rect.centerx, self.rect.centery)

        if realign_x:
            self.rect.centerx = current_tile_x * self.tilemap.tile_size + self.tilemap.tile_size / 2

        if realign_y:
            self.rect.centery = current_tile_y * self.tilemap.tile_size + self.tilemap.tile_size / 2

    def _get_tile(self, x, y):
        return Tile(self.tilemap.map[y, x])

    def _is_in_bounds(self, tile_x, tile_y):
        h, w = self.tilemap.map.shape
        return 0 <= tile_x < w and 0 <= tile_y < h
