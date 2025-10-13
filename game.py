import sys
import pygame
import numpy as np

from pygame.locals import *

from blinky import Blinky
from clyde import Clyde
from inky import Inky
from main import DISPLAY_SURFACE, FPS
from pacman import Pacman
from pinky import Pinky
from tile import Tile
from tilemap import Tilemap
from tileset import Tileset


class Game:

    def __init__(self):
        self.deltatime = 0
        self.tilemap = Tilemap("./maps/original.json", Tileset("./images/tileset.png"))
        self.pacman = Pacman(self, self._load_start_position(Tile.PLAYER_START))
        self.pellet_time_seconds = 0

        blinky = Blinky(self, self._load_start_position(Tile.GHOST_START))
        pinky = Pinky(self, self._load_start_position(Tile.GHOST_START))
        inky = Inky(blinky, self, self._load_start_position(Tile.GHOST_START))
        clyde = Clyde(self, self._load_start_position(Tile.GHOST_START))
        self.ghosts = [clyde, inky, pinky, blinky]

    def _move(self):
        self.pacman.move(self.deltatime)

        for ghost in self.ghosts:
            ghost.move(self.deltatime)

        self.pellet_time_seconds -= self.deltatime

    def _draw(self):
        DISPLAY_SURFACE.fill((0, 0, 0))

        self.tilemap.draw(DISPLAY_SURFACE)
        self.pacman.draw(DISPLAY_SURFACE)

        for ghost in self.ghosts:
            ghost.draw(DISPLAY_SURFACE)

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
            temp = ghost.next_tile
            current_tile = ghost.get_tile_coordinates(*ghost.rect.center)
            ghost.next_tile = current_tile
            ghost.next_velocity = (
                (current_tile[0] - temp[0]) * ghost.speed,
                (current_tile[1] - temp[1]) * ghost.speed,
            )

    @staticmethod
    def handle_events():
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
