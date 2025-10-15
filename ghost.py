import abc
import math
import random

import pygame
from pygame import Vector2, SurfaceType

from direction import Direction
from entity import Entity
from main import SCREEN_WIDTH, load_image, FPS
from tile import Tile


class Ghost(Entity):
    abc.__metaclass__ = abc.ABCMeta

    spritesheet = load_image("./images/ghosts.png")
    sprite_size = 14

    eye_size = (4, 5)
    eye_image = spritesheet.subsurface(pygame.Rect(sprite_size * 6, 0, *eye_size))

    pupil_size = (2, 2)
    pupil_image = spritesheet.subsurface(pygame.Rect(sprite_size * 6, eye_size[1], *pupil_size))

    transparent_tiles = [Tile.AIR, Tile.SMALL_DOT, Tile.BIG_DOT, Tile.GHOST_HOUSE, Tile.GHOST_SLOW, Tile.GHOST_HOME]

    speed = FPS
    animation_frame_length_ms = 120
    flash_speed_ms = 300

    def __init__(self, game, start_pos=(0, 0), image_offset_left=0):
        super().__init__(game, start_pos, image_offset_left)
        self.next_tile = None
        self.next_direction = Direction.LEFT
        self.eaten = False
        self.frighened = False
        self.dot_counter = 0
        self.dot_limit = 0
        self.flash_time = 0
        self.reverse_direction = False
        self.is_released = False

    def draw(self, surface: SurfaceType) -> None:
        ticks = pygame.time.get_ticks()

        if (ticks - self.last_frame_update_time) >= self.animation_frame_length_ms:
            self.image_rect.top = (self.image_rect.top + self.sprite_size) % self.spritesheet.get_height()
            self.image = self.spritesheet.subsurface(self.image_rect)
            self.last_frame_update_time = ticks

        if not self.eaten and self.frighened:
            is_flash = self.game.pellet_time_seconds < 2 and ticks % (2 * self.flash_speed_ms) - self.flash_speed_ms > 0

            frightened_image = self.spritesheet.subsurface(
                pygame.Rect(
                    self.sprite_size * (5 if is_flash else 4),
                    self.image_rect.top,
                    self.sprite_size,
                    self.sprite_size
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

        match self.direction:
            case Direction.LEFT:
                eye_offset_x = -1
                pupil_offset_x = -1
                pupil_offset_y = -1
            case Direction.RIGHT:
                eye_offset_x = 1
                pupil_offset_x = 1
                pupil_offset_y = -1
            case Direction.UP:
                eye_offset_y = -2
                pupil_offset_y = -3

        # draw eyes
        surface.blit(
            self.eye_image,
            pygame.Rect(
                self.rect.centerx - self.eye_size[0] - 1 + eye_offset_x,
                self.rect.y + 3 + eye_offset_y,
                *self.eye_size)
        )
        surface.blit(
            self.eye_image,
            pygame.Rect(
                self.rect.centerx + 1 + eye_offset_x,
                self.rect.y + 3 + eye_offset_y,
                *self.eye_size
            )
        )

        # draw pupils
        surface.blit(
            self.pupil_image,
            pygame.Rect(
                self.rect.centerx - self.eye_size[0] - 2 + self.pupil_size[
                    0] + eye_offset_x + pupil_offset_x,
                self.rect.y + 4 + self.pupil_size[0] + eye_offset_y + pupil_offset_y,
                *self.pupil_size)
        )
        surface.blit(
            self.pupil_image,
            pygame.Rect(
                self.rect.centerx + self.pupil_size[0] + eye_offset_x + pupil_offset_x,
                self.rect.y + 4 + self.pupil_size[0] + eye_offset_y + pupil_offset_y,
                *self.pupil_size
            )
        )

    def move(self, deltatime: float) -> None:
        if self.dot_counter == self.dot_limit:
            self.is_released = True

        if not self.is_released:
            return

        current_tile_coordinates = self.get_current_tile_coordinates()

        if self.game.tilemap.get_tile(current_tile_coordinates) == Tile.GHOST_HOME:
            self.eaten = False
            self.frighened = False

        next_position = self.position + self.direction * self._get_speed() * deltatime

        if self.next_tile is None or current_tile_coordinates == self.next_tile \
                and self._can_move_to_position(next_position):
            self.direction = self.next_direction
            self.next_tile = self._get_next_tile_coordinates()
            self._choose_next_direction()

        self.position = next_position
        self.rect.center = self.position
        self._align_to_grid(
            self.direction.x == 0 and self.direction.y != 0,
            self.direction.x != 0 and self.direction.y == 0
        )

        # wrap when off the screen horizontally
        if self.rect.right < 0:
            self.rect.move_ip(SCREEN_WIDTH + self.rect.width, 0)

        if self.rect.left > SCREEN_WIDTH:
            self.rect.move_ip(-SCREEN_WIDTH - self.rect.width, 0)

    def _choose_target(self, tile_choices) -> Vector2:
        if self.eaten:
            return self.game.tilemap.find_tile(Tile.GHOST_HOME)
        elif self.is_in_ghost_house():
            return self.game.tilemap.find_tile(Tile.GHOST_GATE)
        elif self.reverse_direction:
            return self.get_current_tile_coordinates() - self.direction
        elif self.frighened:
            return tile_choices[random.randint(0, len(tile_choices) - 1)]
        else:
            return self._target_pacman()

    def _can_move_to_position(self, position: Vector2) -> bool:
        min_x = min(position.x, self.position.x)
        max_x = max(position.x, self.position.x)
        min_y = max(position.y, self.position.y)
        max_y = max(position.y, self.position.y)

        return self.next_tile is None or \
            min_x <= (0.5 + self.next_tile.x) * self.game.tilemap.tile_size <= max_x or \
            min_y <= (0.5 + self.next_tile.y) * self.game.tilemap.tile_size <= max_y

    def _choose_next_direction(self) -> None:
        if self.game.tilemap.is_in_bounds(self.next_tile):
            tile_choices = [
                Vector2(self.next_tile.x, self.next_tile.y - 1),
                Vector2(self.next_tile.x, self.next_tile.y + 1),
                Vector2(self.next_tile.x - 1, self.next_tile.y - 1),
                Vector2(self.next_tile.x + 1, self.next_tile.y - 1),
            ]
            min_distance = math.inf
            current_tile_x, current_tile_y = self.get_current_tile_coordinates()
            target = self._choose_target(tile_choices)
            map_h, map_w = self.game.tilemap.map.shape

            for tile_coords in tile_choices:
                tile = self.game.tilemap.get_tile(tile_coords)
                is_current_tile = (tile_coords[0] % map_w, tile_coords[1] % map_h) == (current_tile_x % map_w,
                                                                                       current_tile_y % map_h)

                if self._is_transparent_tile(tile, tile_coords) and (not is_current_tile or self.reverse_direction):
                    self.reverse_direction = False
                    distance = math.dist(tile_coords, target)

                    if distance < min_distance:
                        min_distance = distance
                        self.next_velocity = ((tile_coords[0] - self.next_tile[0]) * self.speed,
                                              (tile_coords[1] - self.next_tile[1]) * self.speed)

    def is_in_ghost_house(self) -> bool:
        return self.game.tilemap.get_tile(self.get_current_tile_coordinates()) in [Tile.GHOST_HOUSE, Tile.GHOST_GATE]

    def _is_transparent_tile(self, tile: Tile, tile_coords: Vector2) -> bool:
        is_ghost_gate_transparent = self.is_in_ghost_house() and self.is_released or self.eaten
        _, current_tile_y = self.get_current_tile_coordinates()

        return tile in self.transparent_tiles \
            or is_ghost_gate_transparent and tile == Tile.GHOST_GATE \
            or current_tile_y <= tile_coords[1] and tile in [Tile.GHOST_NO_UPWARD_TURN, Tile.GHOST_NO_UPWARD_TURN_DOT]

    def _get_speed(self) -> float:
        if self.eaten:
            return 2
        elif self.frighened:
            return 0.625
        elif self.game.tilemap.get_tile(self.get_current_tile_coordinates()) == Tile.GHOST_SLOW:
            return 0.5

        return 0.9375

    @abc.abstractmethod
    def _target_pacman(self) -> Vector2:
        return Vector2(0, 0)
