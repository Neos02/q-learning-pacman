from pygame import Vector2

from enums.direction import Direction
from sprite.ghost import Ghost


class Inky(Ghost):

    def __init__(self, game, start_position: Vector2 = Vector2(0, 0)) -> None:
        super().__init__(game, start_position, 2)
        self.dot_limit: int = 30
        self.global_dot_limit: int = 17

    def _target_pacman(self) -> Vector2:
        target_tile = self.game.pacman.get_current_tile_coordinates()
        blinky_tile = self.game.blinky.get_current_tile_coordinates()

        if self.game.pacman.direction == Direction.UP:
            target_tile.x -= 2

        return 2 * (target_tile + self.game.pacman.direction) - blinky_tile
