import json
import numpy as np
import pygame

from pygame import Vector2, SurfaceType
from world.tile import Tile
from world.tileset import Tileset


class Tilemap:

    def __init__(self, path: str, tileset: Tileset, tile_size: int = 8):
        with open(path, 'r') as f:
            self.map = np.array(json.load(f))

        self.tile_size = tile_size
        self.tileset = tileset
        self.image = pygame.Surface((tile_size * self.map.shape[1], tile_size * self.map.shape[0]))
        self.rect = self.image.get_rect()

    def draw(self, surface: SurfaceType) -> None:
        self.render()
        surface.blit(self.image, self.rect)

    def render(self) -> None:
        m, n = self.map.shape

        for y in range(m):
            for x in range(n):
                tile = self.map[y, x]

                if tile == Tile.GHOST_NO_UPWARD_TURN_DOT.value:
                    tile = Tile.SMALL_DOT.value
                elif tile == Tile.GHOST_NO_UPWARD_TURN.value:
                    tile = Tile.AIR.value

                if tile >= 0:
                    tile_image = self.tileset.tiles[tile]
                    self.image.blit(tile_image, (x * self.tile_size, y * self.tile_size))

    def get_tile(self, position: Vector2) -> Tile:
        if self.is_in_bounds(position):
            return Tile(self.map[int(position.y), int(position.x)])

        return Tile.AIR

    def set_tile(self, position: Vector2, tile: Tile) -> None:
        if self.is_in_bounds(position):
            self.map[int(position.y), int(position.x)] = tile.value

    def find_tile(self, tile: Tile) -> Vector2:
        position = np.where(self.map == tile.value)
        return Vector2(int(position[1][0]), int(position[0][0]))

    def get_tile_coordinates(self, position: Vector2) -> Vector2:
        h, w = self.map.shape
        return Vector2(position.x // self.tile_size % w, position.y // self.tile_size % h)

    def is_in_bounds(self, position: Vector2):
        h, w = self.map.shape
        return 0 <= position.x < w and 0 <= position.y < h
