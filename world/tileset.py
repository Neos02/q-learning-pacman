import pygame

from main import load_image


class Tileset:

    def __init__(self, path, size=(8, 8), margin=0, spacing=0):
        self.path = path
        self.size = size
        self.margin = margin
        self.spacing = spacing
        self.image = load_image(path)
        self.rect = self.image.get_rect()
        self.tiles = []
        self.load()

    def load(self):
        self.tiles = []
        x0 = y0 = self.margin
        w, h = self.rect.size
        dx = self.size[0] + self.spacing
        dy = self.size[1] + self.spacing

        for x in range(x0, w, dx):
            for y in range(y0, h, dy):
                tile = pygame.Surface(self.size)
                tile.blit(self.image, (0, 0), (x, y, *self.size))
                self.tiles.append(tile)
