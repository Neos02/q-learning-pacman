import pygame
from pygame import Vector2, SurfaceType
from pygame.locals import *

from sprite.animated_image import AnimatedImage
from utils.direction import Direction
from sprite.entity import Entity
from main import load_image
from world.tile import Tile


class Pacman(Entity):
    sprite_size = 13
    transparent_tiles = [Tile.AIR, Tile.SMALL_DOT, Tile.BIG_DOT, Tile.GHOST_SLOW, Tile.GHOST_NO_UPWARD_TURN,
                         Tile.GHOST_NO_UPWARD_TURN_DOT]

    def __init__(self, game, start_position: Vector2 = Vector2(0, 0)):
        super().__init__(
            game,
            start_position,
            AnimatedImage("images/pacman.png", Vector2(self.sprite_size), 60)
        )
        self.freeze_frames = 0

    def draw(self, surface: SurfaceType) -> None:
        if self.direction == Direction.NONE:
            self.image.frame_index = 0

        self.image.draw(surface)

    def move(self, deltatime: float) -> None:
        current_tile = self.get_current_tile_coordinates()

        # only allow input when player is on screen
        if self.game.tilemap.is_in_bounds(current_tile):
            self._handle_input()
            queued_tile = current_tile + self.queued_direction

            if not self._has_collision(queued_tile):
                self.direction = self.queued_direction
                self.image.direction = self.direction
                self._align_to_grid(
                    self.direction.x == 0 and self.direction.y != 0,
                    self.direction.x != 0 and self.direction.y == 0
                )
        if self.freeze_frames > 0:
            self.freeze_frames -= 1
        else:
            self._handle_collisions_and_update_position(self.position + self.direction * self._get_speed() * deltatime)

    def _handle_collisions_and_update_position(self, position: Vector2) -> None:
        current_tile = self.get_current_tile_coordinates()
        next_tile = self._get_next_tile_coordinates()

        if not self._has_collision(current_tile) and not self._has_collision(next_tile):
            self.position = Vector2(position.x, position.y)
            tile = self.game.tilemap.get_tile(current_tile)

            if tile == Tile.SMALL_DOT or tile == Tile.GHOST_NO_UPWARD_TURN_DOT:
                self.freeze_frames = 1
                self.game.eat_small_dot(current_tile)
            elif tile == Tile.BIG_DOT:
                self.freeze_frames = 3
                self.game.eat_big_dot(current_tile)
        else:
            self._align_to_grid()
            self.direction = Direction.NONE
            self.queued_direction = Direction.NONE

    def _has_collision(self, tile_coordinates: Vector2) -> bool:
        if self.game.tilemap is None:
            return False

        if self.game.tilemap.is_in_bounds(tile_coordinates):
            return self.game.tilemap.get_tile(tile_coordinates) not in self.transparent_tiles

        return False

    def _handle_input(self) -> None:
        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_a]:
            self.queued_direction = Direction.LEFT
        elif pressed_keys[K_w]:
            self.queued_direction = Direction.UP
        elif pressed_keys[K_d]:
            self.queued_direction = Direction.RIGHT
        elif pressed_keys[K_s]:
            self.queued_direction = Direction.DOWN

    def _get_speed(self) -> float:
        if self.game.pellet_time_seconds > 0:
            return self.base_speed * 1.125

        return self.base_speed
