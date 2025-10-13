from ghost import Ghost


class Blinky(Ghost):

    def __init__(self, game, start_position=(0, 0)):
        super().__init__(game, start_position, 0)

    def _target_pacman(self):
        return self.get_tile_coordinates(*self.game.pacman.rect.center)
