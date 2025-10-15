import pygame
import abc

from pygame import Vector2, SurfaceType

from utils.direction import Direction
from main import FPS, SCREEN_WIDTH, SCREEN_HEIGHT
from world.tile import Tile


class Entity(pygame.sprite.Sprite):
    __metaclass__ = abc.ABCMeta

    base_speed = FPS
    sprite_size = 0
    spritesheet = None
    transparent_tiles = [Tile.AIR, Tile.SMALL_DOT, Tile.BIG_DOT, Tile.GHOST_SLOW]
    animation_frame_length_ms = 60

    def __init__(self, game, start_position: Vector2 = Vector2(0, 0), image_offset_left: int = 0) -> None:
        super().__init__()
        self.start_position = start_position
        self._position = self.start_position.copy()
        self.rect = pygame.Rect(self.position.x, self.position.y, self.sprite_size, self.sprite_size)
        self.image_rect = pygame.Rect(image_offset_left, 0, self.sprite_size, self.sprite_size)
        self.image = self.spritesheet.subsurface(self.image_rect)
        self.direction = Direction.NONE
        self.queued_direction = Direction.NONE
        self.game = game
        self.last_frame_update_time = 0

    def get_current_tile_coordinates(self) -> Vector2:
        return self.game.tilemap.get_tile_coordinates(self.position)

    def _align_to_grid(self, x: bool = True, y: bool = True) -> None:
        current_tile = self.get_current_tile_coordinates()

        if x:
            self.position.x = (current_tile.x + 0.5) * self.game.tilemap.tile_size

        if y:
            self.position.y = (current_tile.y + 0.5) * self.game.tilemap.tile_size

    def _get_next_tile_coordinates(self) -> Vector2:
        current_tile_coordinates = self.get_current_tile_coordinates()
        map_h, map_w = self.game.tilemap.map.shape
        next_tile_coordinates = current_tile_coordinates + self.direction

        return Vector2(next_tile_coordinates.x % map_w, next_tile_coordinates.y % map_h)

    @property
    def position(self) -> Vector2:
        return self._position

    @position.setter
    def position(self, position: Vector2):
        self._position = Vector2(position.x % SCREEN_WIDTH, position.y % SCREEN_HEIGHT)
        self.rect.centerx = int(self._position.x)
        self.rect.centery = int(self._position.y)

    @abc.abstractmethod
    def draw(self, surface: SurfaceType) -> None:
        return

    @abc.abstractmethod
    def move(self, deltatime: float) -> None:
        return

    @abc.abstractmethod
    def _get_speed(self) -> float:
        return self.base_speed
