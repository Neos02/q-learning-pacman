import sys
import pygame
import numpy as np

from pygame.locals import *
from main import DISPLAY_SURFACE, FPS
from pacman import Pacman
from tilemap import Tilemap
from tileset import Tileset


class Game:

    def __init__(self):
        self.deltatime = 0
        self.tilemap = Tilemap("./maps/original.json", Tileset("./images/tileset.png"))
        player_start_pos = np.where(self.tilemap.map == Tilemap.start_tile_id)
        self.player = Pacman(
            start_pos=(player_start_pos[1][0] * self.tilemap.tile_size,
                       player_start_pos[0][0] * self.tilemap.tile_size))

    def _move(self):
        self.player.move(self.deltatime)

    def _draw(self):
        DISPLAY_SURFACE.fill((0, 0, 0))

        self.tilemap.draw(DISPLAY_SURFACE)
        self.player.draw(DISPLAY_SURFACE)

        pygame.display.update()

    def run(self):
        while 1:
            Game.handle_events()
            self._move()
            self._draw()
            self.deltatime = pygame.time.Clock().tick(FPS) / 1000

    @staticmethod
    def handle_events():
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
