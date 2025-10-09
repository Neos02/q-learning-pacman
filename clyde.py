import math

from entity import Entity
from ghost import Ghost
from tile import Tile


class Clyde(Ghost):

    def __init__(self, pacman, tilemap, start_position=(0, 0)):
        super().__init__(pacman, tilemap, start_position, 3 * Entity.sprite_scale * Ghost.sprite_size)

    def _target_pacman(self):
        pacman_coords = self._get_tile_coordinates(*self.pacman.rect.center)

        if math.dist(pacman_coords, self._get_tile_coordinates(*self.rect.center)) >= 8:
            return pacman_coords

        return self.tilemap.find_tile(Tile.CLYDE_FIXED)
