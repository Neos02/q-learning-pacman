import numpy as np
import pygame


class Tilemap:

    def __init__(self, tileset, size=(10, 20), tile_size=16, rect=None):
        self.size = size
        self.tile_size = tile_size
        self.tileset = tileset
        self.map = np.zeros(size, dtype=int)
        self.image = pygame.Surface((tile_size * self.size[1], tile_size * self.size[0]))
        self.rect = self.image.get_rect() if rect is None else pygame.Rect(rect)

    def draw(self, surface):
        self.render()
        surface.blit(self.image, self.rect)

    def render(self):
        m, n = self.map.shape

        for i in range(m):
            for j in range(n):
                tile = self.tileset.tiles[self.map[i, j]]
                self.image.blit(tile, (j * self.tile_size, i * self.tile_size))

    def set_random(self):
        n = len(self.tileset.tiles)
        self.map = np.random.randint(n, size=self.size)
        self.render()
