from pygame import Vector2

from ghost import Ghost


class Inky(Ghost):

    def __init__(self, blinky, game, start_position=(0, 0)):
        super().__init__(game, start_position, 2 * Ghost.sprite_size)
        self.blinky = blinky
        self.dot_limit = 30

    def _target_pacman(self) -> Vector2:
        target_tile = self.game.pacman.get_current_tile_coordinates()
        blinky_tile = self.blinky.get_current_tile_coordinates()

        if self.game.pacman.direction[1] < 0:
            target_tile.x -= 2

        return 2 * (target_tile + self.game.pacman.direction) - blinky_tile
