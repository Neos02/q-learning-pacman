import json
import sys
import pygame
import numpy as np

from pygame.locals import *

from blinky import Blinky
from clyde import Clyde
from inky import Inky
from main import DISPLAY_SURFACE, FPS, load_image, SCREEN_WIDTH, FONT_NUMBERS, COLOR_FONT
from pacman import Pacman
from pinky import Pinky
from tile import Tile
from tilemap import Tilemap
from tileset import Tileset


class Game:
    high_score_text_image = load_image("./images/high-score-text.png")

    dot_timer_max_value = 4
    ghost_eaten_base_value = 200

    def __init__(self):
        self.deltatime = 0
        self.tilemap = Tilemap("./maps/original.json", Tileset("./images/tileset.png"))
        self.pacman = Pacman(self, self._load_start_position(Tile.PLAYER_START))
        self.pellet_time_seconds = 0
        self.dot_timer_seconds = self.dot_timer_max_value
        self.score = 0
        self.ghost_eaten_points = self.ghost_eaten_base_value

        with open("./high_score.json", 'r') as f:
            self.high_score = json.load(f)["high_score"]

        blinky = Blinky(self, self._load_start_position(Tile.GHOST_START))
        pinky = Pinky(self, self._load_start_position(Tile.GHOST_START))
        inky = Inky(blinky, self, self._load_start_position(Tile.GHOST_START))
        clyde = Clyde(self, self._load_start_position(Tile.GHOST_START))
        self.ghosts = [clyde, inky, pinky, blinky]

    def _move(self):
        self.pacman.move(self.deltatime)
        pacman_tile = self.pacman.get_tile_coordinates(*self.pacman.rect.center)

        for ghost in self.ghosts:
            ghost.move(self.deltatime)
            ghost_tile = ghost.get_tile_coordinates(*ghost.rect.center)

            if ghost_tile == pacman_tile:
                if ghost.frighened:
                    if not ghost.eaten:
                        ghost.eaten = True
                        self.score += self.ghost_eaten_points
                        self.ghost_eaten_points *= 2
                else:
                    self.game_over()

        self.pellet_time_seconds -= self.deltatime

        if self.pellet_time_seconds <= 0:
            self.ghost_eaten_points = self.ghost_eaten_base_value

            for ghost in self.ghosts:
                ghost.frighened = False

        self.dot_timer_seconds -= self.deltatime

        if self.dot_timer_seconds <= 0:
            for ghost in reversed(self.ghosts):
                if ghost.is_in_ghost_house():
                    ghost.dot_counter = ghost.dot_limit
                    self.dot_timer_seconds = self.dot_timer_max_value
                    break

    def _draw(self):
        DISPLAY_SURFACE.fill((0, 0, 0))

        self.tilemap.draw(DISPLAY_SURFACE)
        self.pacman.draw(DISPLAY_SURFACE)

        for ghost in self.ghosts:
            ghost.draw(DISPLAY_SURFACE)

        DISPLAY_SURFACE.blit(self.high_score_text_image,
                             ((SCREEN_WIDTH - self.high_score_text_image.get_width()) / 2, 2))

        high_score_text = FONT_NUMBERS.render(f'{self.high_score}', False, COLOR_FONT)
        DISPLAY_SURFACE.blit(high_score_text, ((SCREEN_WIDTH - high_score_text.get_width()) / 2, 18))

        score_text = FONT_NUMBERS.render(f'{self.score}', False, COLOR_FONT)
        DISPLAY_SURFACE.blit(score_text, (48, 18))

        pygame.display.update()

    def run(self):
        while 1:
            Game.handle_events()
            self._move()
            self._draw()
            self.deltatime = pygame.time.Clock().tick(FPS) / 1000

    def _load_start_position(self, tile):
        position = np.where(self.tilemap.map == tile.value)
        tile_x = position[1][0]
        tile_y = position[0][0]

        if tile == Tile.GHOST_START and \
                (self.tilemap.get_tile(tile_x - 1, tile_y) is Tile.GHOST_HOUSE or
                 self.tilemap.get_tile(tile_x + 1, tile_y) is Tile.GHOST_HOUSE or
                 self.tilemap.get_tile(tile_x, tile_y - 1) is Tile.GHOST_HOUSE or
                 self.tilemap.get_tile(tile_x, tile_y + 1) is Tile.GHOST_HOUSE):
            self.tilemap.set_tile(tile_x, tile_y, Tile.GHOST_HOUSE)
        else:
            self.tilemap.set_tile(tile_x, tile_y, Tile.AIR)

        return tile_x * self.tilemap.tile_size, tile_y * self.tilemap.tile_size

    def enter_frightened_mode(self):
        self.pellet_time_seconds = 6

        for ghost in self.ghosts:
            if not ghost.is_in_ghost_house():
                ghost.next_tile = None
                ghost.reverse_direction = True
                ghost.frighened = True

    def eat_small_dot(self, tile_x, tile_y):

        if self.tilemap.get_tile(tile_x, tile_y) == Tile.GHOST_NO_UPWARD_TURN_DOT:
            self.tilemap.set_tile(tile_x, tile_y, Tile.GHOST_NO_UPWARD_TURN)
        else:
            self.tilemap.set_tile(tile_x, tile_y, Tile.AIR)

        self.dot_timer_seconds = self.dot_timer_max_value
        self.score += 10

        for ghost in reversed(self.ghosts):
            if ghost.is_in_ghost_house():
                ghost.dot_counter += 1
                break

    def eat_big_dot(self, tile_x, tile_y):
        self.tilemap.set_tile(tile_x, tile_y, Tile.AIR)
        self.enter_frightened_mode()
        self.score += 50

    def game_over(self):
        print(self.score)

        if self.score > self.high_score:
            with open("./high_score.json", 'w') as f:
                json.dump({"high_score": self.score}, f)

        pygame.quit()
        sys.exit()

    @staticmethod
    def handle_events():
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
