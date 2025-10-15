from pygame import Vector2
from sprite.ghost import Ghost


class Pinky(Ghost):

    def __init__(self, game, start_position: Vector2 = Vector2(0, 0)) -> None:
        super().__init__(game, start_position, 1)

    def _target_pacman(self) -> Vector2:
        target_tile = self.game.pacman.get_current_tile_coordinates()

        if self.game.pacman.direction.y < 0:
            target_tile.x -= 4

        return target_tile + 4 * self.game.pacman.direction
