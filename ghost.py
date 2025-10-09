import math

import pygame

from entity import Entity
from main import SCREEN_WIDTH, load_image
from tile import Tile


class Ghost(Entity):
    spritesheet = load_image("./images/ghosts.png", Entity.sprite_scale)
    sprite_size = 14

    eye_size = (4 * Entity.sprite_scale, 5 * Entity.sprite_scale)
    eye_image = spritesheet.subsurface(pygame.Rect(sprite_size * Entity.sprite_scale * 4, 0, *eye_size))

    pupil_size = (2 * Entity.sprite_scale, 2 * Entity.sprite_scale)
    pupil_image = spritesheet.subsurface(pygame.Rect(sprite_size * Entity.sprite_scale * 4, eye_size[1], *pupil_size))

    transparent_tiles = [Tile.AIR, Tile.SMALL_DOT, Tile.BIG_DOT, Tile.GHOST_HOUSE]

    def __init__(self, pacman, tilemap, start_pos=(0, 0), image_offset_left=0):
        super().__init__(tilemap, start_pos, image_offset_left)
        self.pacman = pacman
        self.next_tile = None
        self.next_velocity = (-self.speed, 0)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

        eye_offset_x = 0
        eye_offset_y = 0
        pupil_offset_x = 0
        pupil_offset_y = 0

        if self.velocity[0] < 0:
            eye_offset_x = -self.sprite_scale
            pupil_offset_x = -self.sprite_scale
            pupil_offset_y = -self.sprite_scale
        elif self.velocity[0] > 0:
            eye_offset_x = self.sprite_scale
            pupil_offset_x = self.sprite_scale
            pupil_offset_y = -self.sprite_scale
        elif self.velocity[1] < 0:
            eye_offset_y = -2 * self.sprite_scale
            pupil_offset_y = -3 * self.sprite_scale

        # draw eyes
        surface.blit(
            self.eye_image,
            pygame.Rect(
                self.rect.centerx - self.eye_size[0] - self.sprite_scale + eye_offset_x,
                self.rect.y + 3 * self.sprite_scale + eye_offset_y,
                *self.eye_size)
        )
        surface.blit(
            self.eye_image,
            pygame.Rect(
                self.rect.centerx + self.sprite_scale + eye_offset_x,
                self.rect.y + 3 * self.sprite_scale + eye_offset_y,
                *self.eye_size
            )
        )

        # draw pupils
        surface.blit(
            self.pupil_image,
            pygame.Rect(
                self.rect.centerx - self.eye_size[0] - 2 * self.sprite_scale + self.pupil_size[
                    0] + eye_offset_x + pupil_offset_x,
                self.rect.y + 4 * self.sprite_scale + self.pupil_size[0] + eye_offset_y + pupil_offset_y,
                *self.pupil_size)
        )
        surface.blit(
            self.pupil_image,
            pygame.Rect(
                self.rect.centerx + self.pupil_size[0] + eye_offset_x + pupil_offset_x,
                self.rect.y + 4 * self.sprite_scale + self.pupil_size[0] + eye_offset_y + pupil_offset_y,
                *self.pupil_size
            )
        )

    def move(self, deltatime):
        map_h, map_w = self.tilemap.map.shape
        current_tile_x, current_tile_y = self._get_tile_coordinates(self.rect.centerx, self.rect.centery)
        next_position = (
            self.rect.centerx + self.velocity[0] * deltatime,
            self.rect.centery + self.velocity[1] * deltatime
        )

        if self.next_tile is None or (current_tile_x, current_tile_y) == self.next_tile:
            min_x = min(next_position[0], self.rect.centerx)
            max_x = max(next_position[0], self.rect.centerx)
            min_y = min(next_position[1], self.rect.centery)
            max_y = max(next_position[1], self.rect.centery)

            if self.next_tile is None or \
                    min_x <= (0.5 + self.next_tile[0]) * self.tilemap.tile_size <= max_x or \
                    min_y <= (0.5 + self.next_tile[1]) * self.tilemap.tile_size <= max_y:
                self.velocity = self.next_velocity
                self.next_tile = (
                    int(current_tile_x + self.velocity[0] / self.speed) % map_w,
                    int(current_tile_y + self.velocity[1] / self.speed) % map_h
                )

                if self._is_in_ghost_house():
                    target_x, target_y = self.tilemap.find_tile(Tile.GHOST_GATE)
                else:
                    target_x, target_y = self._get_tile_coordinates(self.pacman.rect.centerx, self.pacman.rect.centery)

                if self._is_in_bounds(*self.next_tile):
                    tile_choices = [
                        (
                            self.next_tile[0],
                            self.next_tile[1] - 1
                        ),
                        (
                            self.next_tile[0] - 1,
                            self.next_tile[1]
                        ),
                        (
                            self.next_tile[0],
                            self.next_tile[1] + 1
                        ),
                        (
                            self.next_tile[0] + 1,
                            self.next_tile[1]
                        )
                    ]
                    min_distance = math.inf

                    for tile_coords in tile_choices:
                        tile = self.tilemap.get_tile(*tile_coords)

                        if (tile in self.transparent_tiles or self._is_in_ghost_house() and tile == Tile.GHOST_GATE) \
                                and tile_coords != (current_tile_x, current_tile_y):
                            distance = math.dist(tile_coords, (target_x, target_y))

                            if distance < min_distance:
                                min_distance = distance
                                self.next_velocity = ((tile_coords[0] - self.next_tile[0]) * self.speed,
                                                      (tile_coords[1] - self.next_tile[1]) * self.speed)

        self.rect.centerx = next_position[0]
        self.rect.centery = next_position[1]
        self._realign(
            self.velocity[0] == 0 and self.velocity[1] != 0,
            self.velocity[0] != 0 and self.velocity[1] == 0
        )

        # wrap when off the screen horizontally
        if self.rect.right < 0:
            self.rect.move_ip(SCREEN_WIDTH + self.rect.width, 0)

        if self.rect.left > SCREEN_WIDTH:
            self.rect.move_ip(-SCREEN_WIDTH - self.rect.width, 0)

    def _is_in_ghost_house(self):
        return self.tilemap.get_tile(
            *self._get_tile_coordinates(self.rect.centerx, self.rect.centery)
        ) == Tile.GHOST_HOUSE
