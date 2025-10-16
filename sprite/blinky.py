from pygame import Vector2
from enums.ghost_state import GhostState
from sprite.ghost import Ghost


class Blinky(Ghost):

    def __init__(self, game, start_position: Vector2 = Vector2(0, 0)) -> None:
        super().__init__(game, start_position, 0)

    def _target_pacman(self) -> Vector2:
        return self.game.pacman.get_current_tile_coordinates()
