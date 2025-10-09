from ghost import Ghost


class Blinky(Ghost):

    def __init__(self, pacman, tilemap, start_position=(0, 0)):
        super().__init__(pacman, tilemap, start_position, 0)

    def _target_pacman(self):
        return self._get_tile_coordinates(*self.pacman.rect.center)
