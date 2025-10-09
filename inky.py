import math

from entity import Entity
from ghost import Ghost


class Inky(Ghost):

    def __init__(self, blinky, pacman, tilemap, start_position=(0, 0)):
        super().__init__(pacman, tilemap, start_position, 2 * Entity.sprite_scale * Ghost.sprite_size)
        self.blinky = blinky

    def _target_pacman(self):
        target_tile_x, target_tile_y = self._get_tile_coordinates(*self.pacman.rect.center)
        blinky_tile_x, blinky_tile_y = self._get_tile_coordinates(*self.blinky.rect.center)

        if self.pacman.velocity[1] < 0:
            target_tile_x -= 2

        target_tile_x += 2 * self.pacman.velocity[0] / self.pacman.speed
        target_tile_y += 2 * self.pacman.velocity[1] / self.pacman.speed

        target_tile_x += target_tile_x - blinky_tile_x
        target_tile_y += target_tile_y - blinky_tile_y

        return target_tile_x, target_tile_y
