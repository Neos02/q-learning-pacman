import json

import numpy as np
import pygame

from tile import Tile


class Tilemap:
    start_tile_id = -1

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

        for i in range(m):
            for j in range(n):
                if self.map[i, j] != Tilemap.start_tile_id:
                    tile = self.tileset.tiles[self.map[i, j]]
                    self.image.blit(tile, (j * self.tile_size, i * self.tile_size))

    def get_tile(self, x, y):
        h, w = self.map.shape

        if 0 <= x < w and 0 <= y < h:
            return Tile(self.map[y, x])

        return Tile.AIR

    def set_tile(self, x, y, tile):
        h, w = self.map.shape

        if 0 <= x < w and 0 <= y < h:
            self.map[y, x] = tile.value
