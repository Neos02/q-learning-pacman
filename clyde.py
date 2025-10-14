import math

from entity import Entity
from ghost import Ghost
from tile import Tile


class Clyde(Ghost):

    def __init__(self, game, start_position=(0, 0)):
        super().__init__(game, start_position, 3 * Ghost.sprite_size)
        self.dot_limit = 60

    def _target_pacman(self):
        pacman_coords = self.get_tile_coordinates(*self.game.pacman.rect.center)

        if math.dist(pacman_coords, self.get_tile_coordinates(*self.rect.center)) >= 8:
            return pacman_coords

        return self.game.tilemap.find_tile(Tile.CLYDE_FIXED)
