import sys
import pygame
import numpy as np

from pygame.locals import *

from ghost import Ghost
from main import DISPLAY_SURFACE, FPS
from pacman import Pacman
from tile import Tile
from tilemap import Tilemap
from tileset import Tileset


class Game:

    def __init__(self):
        self.deltatime = 0
        self.tilemap = Tilemap("./maps/original.json", Tileset("./images/tileset.png"))
        self.player = Pacman(self._load_start_position(Tile.PLAYER_START), self.tilemap)
        self.ghosts = [Ghost(self.player, self.tilemap, self._load_start_position(Tile.GHOST_START))]

    def _move(self):
        self.player.move(self.deltatime)

        for ghost in self.ghosts:
            ghost.move(self.deltatime)

    def _draw(self):
        DISPLAY_SURFACE.fill((0, 0, 0))

        self.tilemap.draw(DISPLAY_SURFACE)
        self.player.draw(DISPLAY_SURFACE)

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
        self.tilemap.set_tile(position[1][0], position[0][0], Tile.AIR)
        return position[1][0] * self.tilemap.tile_size, position[0][0] * self.tilemap.tile_size

    @staticmethod
    def handle_events():
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
