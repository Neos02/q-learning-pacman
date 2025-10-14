import abc
import math
import random

import pygame

from entity import Entity
from main import SCREEN_WIDTH, load_image, FPS
from tile import Tile


class Ghost(Entity):
    abc.__metaclass__ = abc.ABCMeta

    spritesheet = load_image("./images/ghosts.png", Entity.sprite_scale)
    sprite_size = 14

    eye_size = (4 * Entity.sprite_scale, 5 * Entity.sprite_scale)
    eye_image = spritesheet.subsurface(pygame.Rect(sprite_size * Entity.sprite_scale * 6, 0, *eye_size))

    pupil_size = (2 * Entity.sprite_scale, 2 * Entity.sprite_scale)
    pupil_image = spritesheet.subsurface(pygame.Rect(sprite_size * Entity.sprite_scale * 6, eye_size[1], *pupil_size))

    transparent_tiles = [Tile.AIR, Tile.SMALL_DOT, Tile.BIG_DOT, Tile.GHOST_HOUSE, Tile.GHOST_SLOW, Tile.GHOST_HOME]

    regular_speed_multiplier = 0.9375
    frightened_speed_multiplier = 0.625
    tunnel_speed_multiplier = 0.5
    eaten_speed_multiplier = 2
    speed = Entity.sprite_scale * FPS
    animation_frame_length_ms = 120
    flash_speed_ms = 500

    def __init__(self, game, start_pos=(0, 0), image_offset_left=0):
        super().__init__(game, start_pos, image_offset_left)
        self.next_tile = None
        self.next_velocity = (-self.speed, 0)
        self.eaten = False
        self.frighened = True
        self.dot_counter = 0
        self.dot_limit = 0
        self.flash_time = 0

    def draw(self, surface):
        ticks = pygame.time.get_ticks()

        if (ticks - self.last_frame_update_time) >= self.animation_frame_length_ms:
            self.image_rect.top = (self.image_rect.top + self.scaled_sprite_size) % self.spritesheet.get_height()
            self.image = self.spritesheet.subsurface(self.image_rect)
            self.last_frame_update_time = ticks

        if not self.eaten and self.frighened:
            is_flash = self.game.pellet_time_seconds < 2 and ticks % (2 * self.flash_speed_ms) - self.flash_speed_ms > 0

            frightened_image = self.spritesheet.subsurface(
                pygame.Rect(
                    self.sprite_size * Entity.sprite_scale * (5 if is_flash else 4),
                    self.image_rect.top,
                    self.sprite_size * Entity.sprite_scale,
                    self.sprite_size * Entity.sprite_scale
                )
            )

            surface.blit(frightened_image, self.rect)
            return

        if not self.eaten:
            surface.blit(self.image, self.rect)

        eye_offset_x = 0
        eye_offset_y = 0
        pupil_offset_x = 0
        pupil_offset_y = 0

        if self.velocity[0] < 0:
            eye_offset_x = -self.sprite_scale
            pupil_offset_x = -self.sprite_scale
            pupil_offset_y = -self.sprite_scale
        elif self.velocity[0] > 0:
            eye_offset_x = self.sprite_scale
            pupil_offset_x = self.sprite_scale
            pupil_offset_y = -self.sprite_scale
        elif self.velocity[1] < 0:
            eye_offset_y = -2 * self.sprite_scale
            pupil_offset_y = -3 * self.sprite_scale

        # draw eyes
        surface.blit(
            self.eye_image,
            pygame.Rect(
                self.rect.centerx - self.eye_size[0] - self.sprite_scale + eye_offset_x,
                self.rect.y + 3 * self.sprite_scale + eye_offset_y,
                *self.eye_size)
        )
        surface.blit(
            self.eye_image,
            pygame.Rect(
                self.rect.centerx + self.sprite_scale + eye_offset_x,
                self.rect.y + 3 * self.sprite_scale + eye_offset_y,
                *self.eye_size
            )
        )

        # draw pupils
        surface.blit(
            self.pupil_image,
            pygame.Rect(
                self.rect.centerx - self.eye_size[0] - 2 * self.sprite_scale + self.pupil_size[
                    0] + eye_offset_x + pupil_offset_x,
                self.rect.y + 4 * self.sprite_scale + self.pupil_size[0] + eye_offset_y + pupil_offset_y,
                *self.pupil_size)
        )
        surface.blit(
            self.pupil_image,
            pygame.Rect(
                self.rect.centerx + self.pupil_size[0] + eye_offset_x + pupil_offset_x,
                self.rect.y + 4 * self.sprite_scale + self.pupil_size[0] + eye_offset_y + pupil_offset_y,
                *self.pupil_size
            )
        )

    def move(self, deltatime):
        current_tile = self.get_tile_coordinates(self.rect.centerx, self.rect.centery)

        if self.game.tilemap.get_tile(*current_tile) == Tile.GHOST_HOME:
            self.eaten = False
            self.frighened = False

        next_position = (
            self.rect.centerx + self.velocity[0] * deltatime,
            self.rect.centery + self.velocity[1] * deltatime
        )

        if self.next_tile is None or current_tile == self.next_tile and self._can_move_to_position(next_position):
            self.velocity = (
                self.next_velocity[0] * self._get_speed_multiplier(),
                self.next_velocity[1] * self._get_speed_multiplier()
            )
            self.next_tile = self._get_next_tile()
            self._choose_next_direction()

        self.rect.center = next_position
        self._realign(
            self.velocity[0] == 0 and self.velocity[1] != 0,
            self.velocity[0] != 0 and self.velocity[1] == 0
        )

        # wrap when off the screen horizontally
        if self.rect.right < 0:
            self.rect.move_ip(SCREEN_WIDTH + self.rect.width, 0)

        if self.rect.left > SCREEN_WIDTH:
            self.rect.move_ip(-SCREEN_WIDTH - self.rect.width, 0)

    def _choose_target(self, tile_choices):
        if self.eaten:
            return self.game.tilemap.find_tile(Tile.GHOST_HOME)
        elif self.is_in_ghost_house():
            return self.game.tilemap.find_tile(Tile.GHOST_GATE)
        elif self.frighened > 0:
            return tile_choices[random.randint(0, len(tile_choices) - 1)]
        else:
            return self._target_pacman()

    def _can_move_to_position(self, position):
        min_x = min(position[0], self.rect.centerx)
        max_x = max(position[0], self.rect.centerx)
        min_y = min(position[1], self.rect.centery)
        max_y = max(position[1], self.rect.centery)

        return self.next_tile is None or \
            min_x <= (0.5 + self.next_tile[0]) * self.game.tilemap.tile_size <= max_x or \
            min_y <= (0.5 + self.next_tile[1]) * self.game.tilemap.tile_size <= max_y

    def _choose_next_direction(self):
        if self._is_in_bounds(*self.next_tile):
            tile_choices = [
                (
                    self.next_tile[0],
                    self.next_tile[1] - 1
                ),
                (
                    self.next_tile[0] - 1,
                    self.next_tile[1]
                ),
                (
                    self.next_tile[0],
                    self.next_tile[1] + 1
                ),
                (
                    self.next_tile[0] + 1,
                    self.next_tile[1]
                )
            ]
            min_distance = math.inf
            current_tile_x, current_tile_y = self.get_tile_coordinates(self.rect.centerx, self.rect.centery)
            target = self._choose_target(tile_choices)
            map_h, map_w = self.game.tilemap.map.shape

            for tile_coords in tile_choices:
                tile = self.game.tilemap.get_tile(*tile_coords)

                if (self._is_transparent_tile(tile) and (tile_coords[0] % map_w, tile_coords[1] % map_h) !=
                        (current_tile_x % map_w, current_tile_y % map_h)):
                    distance = math.dist(tile_coords, target)

                    if distance < min_distance:
                        min_distance = distance
                        self.next_velocity = ((tile_coords[0] - self.next_tile[0]) * self.speed,
                                              (tile_coords[1] - self.next_tile[1]) * self.speed)

    def is_in_ghost_house(self):
        return self.game.tilemap.get_tile(
            *self.get_tile_coordinates(self.rect.centerx, self.rect.centery)
        ) == Tile.GHOST_HOUSE

    def _is_transparent_tile(self, tile):
        is_ghost_gate_transparent = self.is_in_ghost_house() and self.dot_counter >= self.dot_limit or self.eaten
        return tile in self.transparent_tiles or is_ghost_gate_transparent and tile == Tile.GHOST_GATE

    def _get_speed_multiplier(self):
        if self.eaten:
            return self.eaten_speed_multiplier

        if self.frighened > 0:
            return self.frightened_speed_multiplier

        if self.game.tilemap.get_tile(*self.get_tile_coordinates(*self.rect.center)) == Tile.GHOST_SLOW:
            return self.tunnel_speed_multiplier

        return self.regular_speed_multiplier

    @abc.abstractmethod
    def _target_pacman(self):
        return 0, 0
