import pygame
import abc

from pygame import Vector2, SurfaceType
from sprite.animated_image import AnimatedImage
from enums.direction import Direction
from main import FPS, SCREEN_WIDTH, SCREEN_HEIGHT
from world.tile import Tile


class Entity(pygame.sprite.Sprite):
    __metaclass__ = abc.ABCMeta

    base_speed = FPS
    sprite_size = 0

    def __init__(self, game, start_position: Vector2 = Vector2(0, 0), image: AnimatedImage = None) -> None:
        super().__init__()
        self.start_position: Vector2 = start_position
        self.rect: pygame.Rect = pygame.Rect(
            start_position.x - self.sprite_size / 2,
            start_position.y - self.sprite_size / 2,
            self.sprite_size,
            self.sprite_size
        )
        self.image: AnimatedImage = image
        self.position: Vector2 = self.start_position.copy()
        self._direction: Vector2 = Direction.NONE
        self._queued_direction: Vector2 = Direction.NONE
        self.game = game

    def draw(self, surface: SurfaceType) -> None:
        if self.image is not None:
            self.image.draw(surface)

    def get_current_tile_coordinates(self) -> Vector2:
        return self.game.tilemap.get_tile_coordinates(self.position)

    def get_current_tile(self) -> Tile:
        return self.game.tilemap.get_tile(self.get_current_tile_coordinates())

    def _is_transparent_tile(self, tile_coordinates: Vector2) -> bool:
        return self.game.tilemap.get_tile(tile_coordinates) in [Tile.AIR, Tile.SMALL_DOT, Tile.BIG_DOT, Tile.GHOST_SLOW]

    def _align_to_grid(self, x: bool = True, y: bool = True) -> None:
        current_tile = self.get_current_tile_coordinates()

        if x:
            self.position.x = (current_tile.x + 0.5) * self.game.tilemap.tile_size

        if y:
            self.position.y = (current_tile.y + 0.5) * self.game.tilemap.tile_size

    def _get_next_tile_coordinates(self) -> Vector2:
        current_tile_coordinates = self.get_current_tile_coordinates()
        map_h, map_w = self.game.tilemap.map.shape
        next_tile_coordinates = current_tile_coordinates + self._direction

        return Vector2(next_tile_coordinates.x % map_w, next_tile_coordinates.y % map_h)

    @property
    def position(self) -> Vector2:
        return self._position

    @position.setter
    def position(self, position: Vector2):
        self._position = Vector2(position.x % SCREEN_WIDTH, position.y % SCREEN_HEIGHT)
        self.rect.centerx = int(self._position.x)
        self.rect.centery = int(self._position.y)

        if self.image is not None:
            self.image.position = self._position

    @property
    def direction(self) -> Vector2:
        if self._direction == Direction.NONE:
            return self._queued_direction

        return self._direction

    @abc.abstractmethod
    def move(self, deltatime: float) -> None:
        return

    @abc.abstractmethod
    def _get_speed(self) -> float:
        return self.base_speed
