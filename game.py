import json
import sys
import pygame
from pygame import Vector2

from pygame.locals import *

from enums.ghost_state import GhostState
from sprite.blinky import Blinky
from sprite.clyde import Clyde
from sprite.inky import Inky
from main import DISPLAY_SURFACE, FPS, load_image, SCREEN_WIDTH, FONT_NUMBERS, COLOR_FONT, SCREEN_HEIGHT, DRAW_SURFACE
from sprite.pacman import Pacman
from sprite.pinky import Pinky
from world.tile import Tile
from world.tilemap import Tilemap
from world.tileset import Tileset


class Game:
    high_score_text_image = load_image("./images/high-score-text.png")
    life_image = load_image("./images/pacman.png").subsurface(
        pygame.Rect(
            Pacman.sprite_size,
            0,
            Pacman.sprite_size,
            Pacman.sprite_size
        )
    )

    dot_timer_max_value = 4
    ghost_eaten_base_value = 200

    def __init__(self):
        self.deltatime = 0
        self.tilemap = Tilemap("data/map.json", Tileset("images/tileset.png"))
        self.pacman = Pacman(self, self._load_start_position(Tile.PLAYER_START))
        self.pellet_time_seconds = 0
        self.dot_timer_seconds = self.dot_timer_max_value
        self.score = 0
        self.ghost_eaten_points = self.ghost_eaten_base_value
        self.lives = 3

        with open("data/high_score.json", 'r') as f:
            self.high_score = json.load(f)["high_score"]

        blinky = Blinky(self, self._load_start_position(Tile.GHOST_START))
        pinky = Pinky(self, self._load_start_position(Tile.GHOST_START))
        inky = Inky(blinky, self, self._load_start_position(Tile.GHOST_START))
        clyde = Clyde(self, self._load_start_position(Tile.GHOST_START))
        self.ghosts = [clyde, inky, pinky, blinky]

    def _move(self) -> None:
        self.pacman.move(self.deltatime)
        pacman_tile = self.pacman.get_current_tile_coordinates()

        for ghost in self.ghosts:
            ghost.move(self.deltatime)
            ghost_tile = ghost.get_current_tile_coordinates()

            if ghost_tile == pacman_tile:
                if ghost.state in [GhostState.FRIGHTENED, GhostState.REVERSE]:
                    ghost.eat()
                    self.score += self.ghost_eaten_points
                    self.ghost_eaten_points *= 2
                elif ghost.state != GhostState.EATEN:
                    self.game_over()

        self.pellet_time_seconds -= self.deltatime

        if self.pellet_time_seconds <= 0:
            self.ghost_eaten_points = self.ghost_eaten_base_value

            for ghost in self.ghosts:
                if ghost.state not in [GhostState.HOME, GhostState.EATEN]:
                    ghost.state = GhostState.CHASE

        self.dot_timer_seconds -= self.deltatime

        if self.dot_timer_seconds <= 0:
            for ghost in reversed(self.ghosts):
                if ghost.state == GhostState.HOME:
                    ghost.released = True
                    self.dot_timer_seconds = self.dot_timer_max_value
                    break

    def _draw(self) -> None:
        DRAW_SURFACE.fill((0, 0, 0))

        self.tilemap.draw(DRAW_SURFACE)
        self.pacman.draw(DRAW_SURFACE)

        for ghost in self.ghosts:
            ghost.draw(DRAW_SURFACE)

        DRAW_SURFACE.blit(self.high_score_text_image,
                          ((SCREEN_WIDTH - self.high_score_text_image.get_width()) / 2, 2))

        high_score_text = FONT_NUMBERS.render(f'{self.high_score}', False, COLOR_FONT)
        DRAW_SURFACE.blit(high_score_text, ((SCREEN_WIDTH - high_score_text.get_width()) / 2, 9))

        score_text = FONT_NUMBERS.render(f'{self.score}', False, COLOR_FONT)
        DRAW_SURFACE.blit(score_text, (24, 9))

        for i in range(self.lives):
            life_image_rect = self.life_image.get_rect()
            life_image_rect.left = i * self.life_image.get_width() + 2
            life_image_rect.top = SCREEN_HEIGHT - self.life_image.get_height() - 2
            DRAW_SURFACE.blit(self.life_image, life_image_rect)

        pygame.transform.scale(DRAW_SURFACE, DISPLAY_SURFACE.get_size(), DISPLAY_SURFACE)
        pygame.display.flip()

    def run(self) -> None:
        while 1:
            Game.handle_events()
            self._move()
            self._draw()
            self.deltatime = pygame.time.Clock().tick(FPS) / 1000

    def _load_start_position(self, tile: Tile) -> Vector2:
        tile_coordinates = self.tilemap.find_tile(tile)
        tile_x, tile_y = tile_coordinates

        if tile == Tile.GHOST_START and \
                (self.tilemap.get_tile(Vector2(tile_x - 1, tile_y)) is Tile.GHOST_HOUSE or
                 self.tilemap.get_tile(Vector2(tile_x + 1, tile_y)) is Tile.GHOST_HOUSE or
                 self.tilemap.get_tile(Vector2(tile_x, tile_y - 1)) is Tile.GHOST_HOUSE or
                 self.tilemap.get_tile(Vector2(tile_x, tile_y + 1)) is Tile.GHOST_HOUSE):
            self.tilemap.set_tile(tile_coordinates, Tile.GHOST_HOUSE)
        else:
            self.tilemap.set_tile(tile_coordinates, Tile.AIR)

        return (tile_coordinates * self.tilemap.tile_size +
                Vector2(0, self.tilemap.tile_size / 2))

    def eat_small_dot(self, tile_coordinates: Vector2) -> None:
        if self.tilemap.get_tile(tile_coordinates) == Tile.GHOST_NO_UPWARD_TURN_DOT:
            self.tilemap.set_tile(tile_coordinates, Tile.GHOST_NO_UPWARD_TURN)
        else:
            self.tilemap.set_tile(tile_coordinates, Tile.AIR)

        self.dot_timer_seconds = self.dot_timer_max_value
        self.score += 10

        for ghost in reversed(self.ghosts):
            if ghost.state == GhostState.HOME:
                ghost.dot_counter += 1
                break

    def eat_big_dot(self, tile_coordinates: Vector2) -> None:
        self.tilemap.set_tile(tile_coordinates, Tile.AIR)
        self.score += 50
        self.pellet_time_seconds = 6

        for ghost in self.ghosts:
            ghost.frighten()

    def die(self) -> None:
        self.lives -= 1

    def game_over(self) -> None:
        print(self.score)

        if self.score > self.high_score:
            with open("data/high_score.json", 'w') as f:
                json.dump({"high_score": self.score}, f)

        pygame.quit()
        sys.exit()

    @staticmethod
    def handle_events() -> None:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
