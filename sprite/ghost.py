import abc
import math
import random

from pygame import Vector2, SurfaceType

from enums.direction import Direction
from enums.ghost_state import GhostState
from sprite.animated_image import AnimatedImage
from sprite.ghost_eye import GhostEye
from sprite.entity import Entity
from world.tile import Tile


class Ghost(Entity):
    abc.__metaclass__ = abc.ABCMeta
    sprite_size = 14
    flash_speed_ms = 300
    flash_time_ms = 1500

    def __init__(self, game, start_position: Vector2 = Vector2(0, 0), sprite_index: int = 0) -> None:
        super().__init__(
            game,
            start_position,
            AnimatedImage(
                "images/ghosts.png",
                start_position,
                Vector2(self.sprite_size),
                120,
                sprite_index
            )
        )
        self.state: GhostState = GhostState.HOME
        self.released: bool = False
        self.dot_counter: int = 0
        self.dot_limit: int = 0
        self.global_dot_limit: int = 0
        self.eyes: list[GhostEye] = [GhostEye(self.position, Vector2(-3, -3)), GhostEye(self.position, Vector2(3, -3))]
        self.sprite_index: int = sprite_index
        self.next_tile: Vector2 = self._get_next_tile_coordinates()
        self._queued_direction: Vector2 = Direction.LEFT

    def draw(self, surface: SurfaceType) -> None:
        self._update_ghost_image()

        if self.state != GhostState.EATEN:
            self.image.draw(surface)

        if self.state not in [GhostState.FRIGHTENED, GhostState.REVERSE]:
            for eye in self.eyes:
                eye.draw(surface)

    def move(self, deltatime: float) -> None:
        if self.state == GhostState.CHASE or not self.game.global_dot_counter_active \
                and self.state == GhostState.HOME and self.dot_counter >= self.dot_limit:
            self.released = True

        if self.state == GhostState.HOME and not self._is_in_ghost_house():
            self.state = GhostState.CHASE

        if self.state == GhostState.EATEN and self._is_in_ghost_house():
            self.reset(False)

        if self.released and self.get_current_tile_coordinates() == self.next_tile:
            self._direction = self._queued_direction
            self.next_tile = self._get_next_tile_coordinates()
            self._choose_next_direction()

        self.position = self.position + self._direction * self._get_speed() * deltatime
        self._align_to_grid(
            self._direction in [Direction.UP, Direction.DOWN],
            self._direction in [Direction.LEFT, Direction.RIGHT]
        )

        for eye in self.eyes:
            eye.move(self.position, self._direction)

    def eat(self) -> None:
        self.state = GhostState.EATEN

    def frighten(self) -> None:
        if self.state not in [GhostState.HOME, GhostState.EATEN]:
            self.state = GhostState.REVERSE
            self.next_tile = self._get_next_tile_coordinates()

    def reset(self, reset_position: bool = True) -> None:
        super().reset(reset_position)
        self._queued_direction = Direction.LEFT
        self.state = GhostState.HOME
        self.next_tile = self._get_next_tile_coordinates()
        self.released = False

    def _is_in_ghost_house(self) -> bool:
        return self.get_current_tile() in [Tile.GHOST_HOUSE, Tile.GHOST_HOUSE_FIXED, Tile.GHOST_GATE]

    def _update_ghost_image(self) -> None:
        if self.state in [GhostState.FRIGHTENED, GhostState.REVERSE]:
            flash_delta = self.flash_time_ms - self.game.pellet_time_seconds * 1000
            is_white_flash = flash_delta > 0 and flash_delta % (2 * self.flash_speed_ms) - self.flash_speed_ms > 0

            if is_white_flash:
                self.image.sprite_index = 5
            else:
                self.image.sprite_index = 4
        else:
            self.image.sprite_index = self.sprite_index

    def _choose_target(self, tile_choices: list[Vector2]) -> Vector2:
        match self.state:
            case GhostState.HOME:
                return self.game.tilemap.find_tile(Tile.GHOST_GATE)
            case GhostState.CHASE:
                return self._target_pacman()
            case GhostState.EATEN:
                return self.game.tilemap.find_tile(Tile.GHOST_HOUSE_FIXED)
            case GhostState.FRIGHTENED:
                return tile_choices[random.randint(0, len(tile_choices) - 1)]
            case _:
                raise ValueError(f'Unknown ghost state: {self.state}')

    def _choose_next_direction(self) -> None:
        if not self.game.tilemap.is_in_bounds(self.next_tile):
            return

        if self.state == GhostState.REVERSE:
            self.state = GhostState.FRIGHTENED
            self._queued_direction = -self.direction
            return

        perpendicular_direction = Vector2(self.direction.y, self.direction.x)
        tile_choices = [
            self.next_tile + self._direction,
            self.next_tile + perpendicular_direction,
            self.next_tile - perpendicular_direction,
        ]
        min_distance = math.inf
        target = self._choose_target(tile_choices)

        for tile_coords in tile_choices:
            if self._is_transparent_tile(tile_coords):
                distance = math.dist(tile_coords, target)

                if distance < min_distance:
                    min_distance = distance
                    self._queued_direction = tile_coords - self.next_tile

    def _is_transparent_tile(self, tile_coordinates: Vector2) -> bool:
        current_tile_coordinates = self.get_current_tile_coordinates()
        tile = self.game.tilemap.get_tile(tile_coordinates)

        if self.state in [GhostState.HOME, GhostState.EATEN] and tile == Tile.GHOST_GATE:
            return True

        if current_tile_coordinates.y <= tile_coordinates.y \
                and tile in [Tile.GHOST_NO_UPWARD_TURN, Tile.GHOST_NO_UPWARD_TURN_DOT]:
            return True

        return tile in [Tile.AIR, Tile.SMALL_DOT, Tile.BIG_DOT, Tile.GHOST_HOUSE, Tile.GHOST_SLOW,
                        Tile.GHOST_HOUSE_FIXED]

    def _get_speed(self) -> float:
        match self.state:
            case GhostState.EATEN:
                return self.base_speed * 2
            case GhostState.FRIGHTENED | GhostState.REVERSE:
                return self.base_speed * 0.625
            case _:
                if self.game.tilemap.get_tile(self.get_current_tile_coordinates()) == Tile.GHOST_SLOW:
                    return self.base_speed * 0.5

                return self.base_speed * 0.9375

    @abc.abstractmethod
    def _target_pacman(self) -> Vector2:
        return Vector2(0, 0)
