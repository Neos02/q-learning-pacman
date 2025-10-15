import math

from entity import Entity
from ghost import Ghost


class Pinky(Ghost):

    def __init__(self, game, start_position=(0, 0)):
        super().__init__(game, start_position, Ghost.sprite_size)

    def _target_pacman(self):
        target_tile_x, target_tile_y = self.game.pacman.get_current_tile_coordinates()

        if self.game.pacman.direction[1] < 0:
            target_tile_x -= 4

        return (
            target_tile_x + 4 * self.game.pacman.direction.x,
            target_tile_y + 4 * self.game.pacman.direction.y
        )
