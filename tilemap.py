import json

import numpy as np
import pygame

from tile import Tile


class Tilemap:

    def __init__(self, path, tileset, tile_size=16, rect=None):
        with open(path, 'r') as f:
            self.map = np.array(json.load(f))

        self.tile_size = tile_size
        self.tileset = tileset
        self.image = pygame.Surface((tile_size * self.map.shape[1], tile_size * self.map.shape[0]))
        self.rect = self.image.get_rect() if rect is None else pygame.Rect(rect)

    def draw(self, surface):
        self.render()
        surface.blit(self.image, self.rect)

    def render(self):
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

    def get_tile(self, x, y):
        h, w = self.map.shape

        if 0 <= x < w and 0 <= y < h:
            return Tile(self.map[y, x])

        return Tile.AIR

    def set_tile(self, x, y, tile):
        h, w = self.map.shape

        if 0 <= x < w and 0 <= y < h:
            self.map[y, x] = tile.value

    def find_tile(self, tile):
        position = np.where(self.map == tile.value)
        return position[1][0], position[0][0]
