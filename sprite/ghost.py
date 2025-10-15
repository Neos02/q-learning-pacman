import abc
import math
import random
import pygame

from pygame import Vector2, SurfaceType
from sprite.ghost_eye import GhostEye
from utils.direction import Direction
from sprite.entity import Entity
from main import load_image, FPS
from world.tile import Tile


class Ghost(Entity):
    abc.__metaclass__ = abc.ABCMeta

    spritesheet = load_image("images/ghosts.png")
    sprite_size = 14

    transparent_tiles = [Tile.AIR, Tile.SMALL_DOT, Tile.BIG_DOT, Tile.GHOST_HOUSE, Tile.GHOST_SLOW, Tile.GHOST_HOME]

    speed = FPS
    animation_frame_length_ms = 120
    flash_speed_ms = 300

    def __init__(self, game, start_position: Vector2 = Vector2(0, 0), image_offset_top: int = 0) -> None:
        super().__init__(game, start_position, image_offset_top)
        self.next_tile = None
        self.queued_direction = Direction.LEFT
        self.eaten = False
        self.frighened = False
        self.dot_counter = 0
        self.dot_limit = 0
        self.flash_time = 0
        self.reverse_direction = False
        self.is_released = False
        self.eyes = [GhostEye(self.position, Vector2(-3, -3)), GhostEye(self.position, Vector2(3, -3))]

    def draw(self, surface: SurfaceType) -> None:
        ticks = pygame.time.get_ticks()

        if (ticks - self.last_frame_update_time) >= self.animation_frame_length_ms:
            self.image_rect.left = (self.image_rect.left + self.sprite_size) % self.spritesheet.get_width()
            self.image = self.spritesheet.subsurface(self.image_rect)
            self.last_frame_update_time = ticks

        if not self.eaten and self.frighened:
            is_flash = self.game.pellet_time_seconds < 2 and ticks % (2 * self.flash_speed_ms) - self.flash_speed_ms > 0

            frightened_image = self.spritesheet.subsurface(
                pygame.Rect(
                    self.image_rect.left,
                    self.sprite_size * (5 if is_flash else 4),
                    self.sprite_size,
                    self.sprite_size
                )
            )

            surface.blit(frightened_image, self.rect)
            return

        if not self.eaten:
            surface.blit(self.image, self.rect)

        for eye in self.eyes:
            eye.draw(surface)

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
            self.direction = self.queued_direction
            self.next_tile = self._get_next_tile_coordinates()
            self._choose_next_direction()

        self.position = next_position
        self._align_to_grid(
            self.direction.x == 0 and self.direction.y != 0,
            self.direction.x != 0 and self.direction.y == 0
        )

        for eye in self.eyes:
            eye.move(self.position, self.direction)

    def _choose_target(self, tile_choices: list[Vector2]) -> Vector2:
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
                Vector2(self.next_tile.x - 1, self.next_tile.y),
                Vector2(self.next_tile.x + 1, self.next_tile.y),
            ]
            min_distance = math.inf
            current_tile_x, current_tile_y = self.get_current_tile_coordinates()
            target = self._choose_target(tile_choices)
            map_h, map_w = self.game.tilemap.map.shape

            for tile_coords in tile_choices:
                tile = self.game.tilemap.get_tile(tile_coords)
                is_current_tile = (tile_coords.x % map_w, tile_coords.y % map_h) == (current_tile_x % map_w,
                                                                                     current_tile_y % map_h)

                if self._is_transparent_tile(tile, tile_coords) and (not is_current_tile or self.reverse_direction):
                    self.reverse_direction = False
                    distance = math.dist(tile_coords, target)

                    if distance < min_distance:
                        min_distance = distance
                        self.queued_direction = tile_coords - self.next_tile

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
            return self.base_speed * 2
        elif self.frighened:
            return self.base_speed * 0.625
        elif self.game.tilemap.get_tile(self.get_current_tile_coordinates()) == Tile.GHOST_SLOW:
            return self.base_speed * 0.5

        return self.base_speed * 0.9375

    @abc.abstractmethod
    def _target_pacman(self) -> Vector2:
        return Vector2(0, 0)
