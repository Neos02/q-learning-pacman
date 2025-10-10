import pygame
import abc

from tile import Tile


class Entity(pygame.sprite.Sprite):
    __metaclass__ = abc.ABCMeta

    speed = 200
    sprite_scale = 2
    sprite_size = 0
    spritesheet = None
    transparent_tiles = [Tile.AIR, Tile.SMALL_DOT, Tile.BIG_DOT, Tile.GHOST_SLOW]

    def __init__(self, tilemap, start_pos=(0, 0), image_offset_left=0):
        super().__init__()
        self.scaled_sprite_size = self.sprite_size * self.sprite_scale
        self.rect = pygame.Rect(0, 0, self.scaled_sprite_size, self.scaled_sprite_size)
        self.image_rect = self.rect.copy()
        self.image_rect.left = image_offset_left
        self.image = self.spritesheet.subsurface(self.image_rect)
        self.velocity = (0, 0)
        self.start_pos = (start_pos[0] + 2 * self.sprite_scale, start_pos[1] - 2 * self.sprite_scale)
        self.rect.move_ip(*self.start_pos)
        self.tilemap = tilemap

    @abc.abstractmethod
    def draw(self, surface):
        return

    @abc.abstractmethod
    def move(self, deltatime):
        return

    def _get_tile_coordinates(self, center_x, center_y):
        return int(center_x // self.tilemap.tile_size), int(center_y // self.tilemap.tile_size)

    def _realign(self, realign_x=True, realign_y=True):
        current_tile_x, current_tile_y = self._get_tile_coordinates(self.rect.centerx, self.rect.centery)

        if realign_x:
            self.rect.centerx = current_tile_x * self.tilemap.tile_size + self.tilemap.tile_size / 2

        if realign_y:
            self.rect.centery = current_tile_y * self.tilemap.tile_size + self.tilemap.tile_size / 2

    def _is_in_bounds(self, tile_x, tile_y):
        h, w = self.tilemap.map.shape
        return 0 <= tile_x < w and 0 <= tile_y < h

    def _get_next_tile(self):
        direction_x, direction_y = self._get_direction(self.velocity[0]), self._get_direction(self.velocity[1])
        current_tile_x, current_tile_y = self._get_tile_coordinates(self.rect.centerx, self.rect.centery)
        map_h, map_w = self.tilemap.map.shape

        return (current_tile_x + direction_x) % map_w, (current_tile_y + direction_y) % map_h

    @staticmethod
    def _get_direction(value):
        return 1 if value > 0 else -1 if value < 0 else 0
