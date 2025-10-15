from pygame import Vector2

from ghost import Ghost


class Blinky(Ghost):

    def __init__(self, game, start_position=(0, 0)):
        super().__init__(game, start_position, 0)

    def _target_pacman(self) -> Vector2:
        return self.game.pacman.get_current_tile_coordinates()
