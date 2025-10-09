import math

import pygame

from main import SCREEN_WIDTH, load_image
from tile import Tile


class Ghost(pygame.sprite.Sprite):
    speed = 200
    sprite_scale = 2
    spritesheet = load_image("./images/ghosts.png", sprite_scale)
    sprite_size = sprite_scale * 14

    eye_size = (sprite_scale * 4, sprite_scale * 5)
    eye_image = spritesheet.subsurface(pygame.Rect(sprite_size * 4, 0, *eye_size))

    pupil_size = (sprite_scale * 2, sprite_scale * 2)
    pupil_image = spritesheet.subsurface(pygame.Rect(sprite_size * 4, eye_size[1], *pupil_size))

    transparent_tiles = [Tile.AIR, Tile.SMALL_DOT, Tile.BIG_DOT]

    def __init__(self, pacman, tilemap, start_pos=(0, 0)):
        super().__init__()
        self.start_pos = (start_pos[0] + 2 * Ghost.sprite_scale, start_pos[1] - 2 * Ghost.sprite_scale)
        self.rect = pygame.Rect(0, 0, Ghost.sprite_size, Ghost.sprite_size)
        self.image_rect = self.rect.copy()
        self.image = Ghost.spritesheet.subsurface(self.image_rect)
        self.velocity = (0, 0)
        self.rect.move_ip(*self.start_pos)
        self.tilemap = tilemap
        self.queued_velocity = (0, 0)
        self.pacman = pacman
        self.next_tile = None
        self.next_velocity = (-Ghost.speed, 0)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

        eye_offset_x = 0
        eye_offset_y = 0
        pupil_offset_x = 0
        pupil_offset_y = 0

        if self.velocity[0] < 0:
            eye_offset_x = -Ghost.sprite_scale
            pupil_offset_x = -Ghost.sprite_scale
            pupil_offset_y = -Ghost.sprite_scale
        elif self.velocity[0] > 0:
            eye_offset_x = Ghost.sprite_scale
            pupil_offset_x = Ghost.sprite_scale
            pupil_offset_y = -Ghost.sprite_scale
        elif self.velocity[1] < 0:
            eye_offset_y = -2 * Ghost.sprite_scale
            pupil_offset_y = -3 * Ghost.sprite_scale

        # draw eyes
        surface.blit(
            Ghost.eye_image,
            pygame.Rect(
                self.rect.centerx - Ghost.eye_size[0] - Ghost.sprite_scale + eye_offset_x,
                self.rect.y + 3 * Ghost.sprite_scale + eye_offset_y,
                *Ghost.eye_size)
        )
        surface.blit(
            Ghost.eye_image,
            pygame.Rect(
                self.rect.centerx + Ghost.sprite_scale + eye_offset_x,
                self.rect.y + 3 * Ghost.sprite_scale + eye_offset_y,
                *Ghost.eye_size
            )
        )

        # draw pupils
        surface.blit(
            Ghost.pupil_image,
            pygame.Rect(
                self.rect.centerx - Ghost.eye_size[0] - 2 * Ghost.sprite_scale + Ghost.pupil_size[
                    0] + eye_offset_x + pupil_offset_x,
                self.rect.y + 4 * Ghost.sprite_scale + Ghost.pupil_size[0] + eye_offset_y + pupil_offset_y,
                *Ghost.pupil_size)
        )
        surface.blit(
            Ghost.pupil_image,
            pygame.Rect(
                self.rect.centerx + Ghost.pupil_size[0] + eye_offset_x + pupil_offset_x,
                self.rect.y + 4 * Ghost.sprite_scale + Ghost.pupil_size[0] + eye_offset_y + pupil_offset_y,
                *Ghost.pupil_size
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
                    int(current_tile_x + self.velocity[0] / Ghost.speed) % map_w,
                    int(current_tile_y + self.velocity[1] / Ghost.speed) % map_h
                )
                target_x, target_y = self._get_tile_coordinates(self.pacman.rect.centerx, self.pacman.rect.centery)

                # TODO: replace with is_in_bounds
                if 0 <= self.next_tile[0] < map_w and 0 <= self.next_tile[1] < map_h:
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

                    for tile in tile_choices:
                        if self.tilemap.get_tile(tile[0], tile[1]) not in self.transparent_tiles \
                                or tile == (current_tile_x, current_tile_y):
                            continue

                        distance = math.dist(tile, (target_x, target_y))

                        if distance < min_distance:
                            min_distance = distance
                            self.next_velocity = ((tile[0] - self.next_tile[0]) * Ghost.speed,
                                                  (tile[1] - self.next_tile[1]) * Ghost.speed)

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

    def _get_tile_coordinates(self, center_x, center_y):
        return int(center_x // self.tilemap.tile_size), int(center_y // self.tilemap.tile_size)

    def _realign(self, realign_x=True, realign_y=True):
        current_tile_x, current_tile_y = self._get_tile_coordinates(self.rect.centerx, self.rect.centery)

        if realign_x:
            self.rect.centerx = current_tile_x * self.tilemap.tile_size + self.tilemap.tile_size / 2

        if realign_y:
            self.rect.centery = current_tile_y * self.tilemap.tile_size + self.tilemap.tile_size / 2
