import math

from entity import Entity
from ghost import Ghost


class Inky(Ghost):

    def __init__(self, blinky, game, start_position=(0, 0)):
        super().__init__(game, start_position, 2 * Entity.sprite_scale * Ghost.sprite_size)
        self.blinky = blinky

    def _target_pacman(self):
        target_tile_x, target_tile_y = self.get_tile_coordinates(*self.game.pacman.rect.center)
        blinky_tile_x, blinky_tile_y = self.get_tile_coordinates(*self.blinky.rect.center)

        if self.game.pacman.velocity[1] < 0:
            target_tile_x -= 2

        target_tile_x += 2 * self._get_direction(self.game.pacman.velocity[0])
        target_tile_y += 2 * self._get_direction(self.game.pacman.velocity[1])

        target_tile_x += target_tile_x - blinky_tile_x
        target_tile_y += target_tile_y - blinky_tile_y

        return target_tile_x, target_tile_y
