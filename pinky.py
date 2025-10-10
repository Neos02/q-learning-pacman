import math

from entity import Entity
from ghost import Ghost


class Pinky(Ghost):

    def __init__(self, pacman, tilemap, start_position=(0, 0)):
        super().__init__(pacman, tilemap, start_position, Entity.sprite_scale * Ghost.sprite_size)

    def _target_pacman(self):
        target_tile_x, target_tile_y = self._get_tile_coordinates(*self.pacman.rect.center)

        if self.pacman.velocity[1] < 0:
            target_tile_x -= 4

        return (
            target_tile_x + 4 * self._get_direction(self.pacman.velocity[0]),
            target_tile_y + 4 * self._get_direction(self.pacman.velocity[1])
        )
