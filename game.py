import sys
import pygame
import numpy as np

from pygame.locals import *

from entity import Entity
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
        self.player = Pacman(self.tilemap, self._load_start_position(Tile.PLAYER_START))
        self.ghosts = [
            Ghost(
                self.player,
                self.tilemap,
                self._load_start_position(Tile.GHOST_START)
            ),
            Ghost(
                self.player,
                self.tilemap,
                self._load_start_position(Tile.GHOST_START),
                2 * Entity.sprite_scale * Ghost.sprite_size
            ),
            Ghost(
                self.player,
                self.tilemap,
                self._load_start_position(Tile.GHOST_START),
                Entity.sprite_scale * Ghost.sprite_size
            ),
            Ghost(
                self.player,
                self.tilemap,
                self._load_start_position(Tile.GHOST_START),
                3 * Entity.sprite_scale * Ghost.sprite_size
            ),
        ]

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

    @staticmethod
    def handle_events():
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
