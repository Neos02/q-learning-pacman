import math

from pygame import Vector2
from sprite.ghost import Ghost
from world.tile import Tile


class Clyde(Ghost):

    def __init__(self, game, start_position: Vector2 = Vector2(0, 0)) -> None:
        super().__init__(game, start_position, 3 * Ghost.sprite_size)
        self.dot_limit = 60

    def _target_pacman(self) -> Vector2:
        pacman_coords = self.game.pacman.get_current_tile_coordinates()

        if math.dist(pacman_coords, self.get_current_tile_coordinates()) >= 8:
            return pacman_coords

        return self.game.tilemap.find_tile(Tile.CLYDE_FIXED)
