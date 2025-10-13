import math

from entity import Entity
from ghost import Ghost


class Pinky(Ghost):

    def __init__(self, game, start_position=(0, 0)):
        super().__init__(game, start_position, Entity.sprite_scale * Ghost.sprite_size)

    def _target_pacman(self):
        target_tile_x, target_tile_y = self.get_tile_coordinates(*self.game.pacman.rect.center)

        if self.game.pacman.velocity[1] < 0:
            target_tile_x -= 4

        return (
            target_tile_x + 4 * self._get_direction(self.game.pacman.velocity[0]),
            target_tile_y + 4 * self._get_direction(self.game.pacman.velocity[1])
        )
