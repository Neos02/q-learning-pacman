import pygame

from pygame.locals import *

from entity import Entity
from main import SCREEN_WIDTH, load_image
from tile import Tile


class Pacman(Entity):
    spritesheet = load_image("./images/pacman.png")
    sprite_size = 13
    regular_speed_multiplier = 1
    pellet_speed_multiplier = 1.125
    transparent_tiles = [Tile.AIR, Tile.SMALL_DOT, Tile.BIG_DOT, Tile.GHOST_SLOW, Tile.GHOST_NO_UPWARD_TURN,
                         Tile.GHOST_NO_UPWARD_TURN_DOT]

    def __init__(self, game, start_pos=(0, 0)):
        super().__init__(game, start_pos)
        self.queued_velocity = (0, 0)
        self.freeze_frames = 0

    def draw(self, surface):
        ticks = pygame.time.get_ticks()

        # make pacman be closed when not moving
        if self.velocity == (0, 0):
            self.image_rect.left = 0
            self.image = self.spritesheet.subsurface(self.image_rect)
            self.last_frame_update_time = ticks

        if (ticks - self.last_frame_update_time) >= self.animation_frame_length_ms:
            self.image_rect.left = (self.image_rect.left + self.sprite_size) % self.spritesheet.get_width()
            self.image = self.spritesheet.subsurface(self.image_rect)
            self.last_frame_update_time = ticks

            if self._get_direction(self.velocity[1]) == -1:
                self.image = pygame.transform.rotate(self.image, -90)
            elif self._get_direction(self.velocity[1]) == 1:
                self.image = pygame.transform.rotate(self.image, 90)
            elif self._get_direction(self.velocity[0]) == 1:
                self.image = pygame.transform.rotate(self.image, 180)

        surface.blit(self.image, self.rect)

    def move(self, deltatime):
        current_tile_x, current_tile_y = self.get_tile_coordinates(self.rect.centerx, self.rect.centery)

        # only allow input when player is on screen
        if self._is_in_bounds(current_tile_x, current_tile_y):
            self._handle_input()

            queued_tile_x = int(current_tile_x + self._get_direction(self.queued_velocity[0]))
            queued_tile_y = int(current_tile_y + self._get_direction(self.queued_velocity[1]))

            if not self._has_collision(queued_tile_x, queued_tile_y):
                self.velocity = (
                    self.queued_velocity[0] * self._get_speed(),
                    self.queued_velocity[1] * self._get_speed()
                )
                self._realign(
                    self.velocity[0] == 0 and self.velocity[1] != 0,
                    self.velocity[0] != 0 and self.velocity[1] == 0
                )
        if self.freeze_frames > 0:
            self.freeze_frames -= 1
        else:
            self._handle_collisions_and_update_position((
                self.rect.centerx + self.velocity[0] * deltatime,
                self.rect.centery + self.velocity[1] * deltatime
            ))

        # wrap when off the screen horizontally
        if self.rect.right < 0:
            self.rect.move_ip(SCREEN_WIDTH + self.rect.width, 0)

        if self.rect.left > SCREEN_WIDTH:
            self.rect.move_ip(-SCREEN_WIDTH - self.rect.width, 0)

    def _handle_collisions_and_update_position(self, position):
        current_tile_x, current_tile_y = self.get_tile_coordinates(self.rect.centerx, self.rect.centery)
        next_tile_x, next_tile_y = self._get_next_tile()

        if not self._has_collision(current_tile_x, current_tile_y) \
                and not self._has_collision(next_tile_x, next_tile_y):
            self.rect.centerx = position[0]
            self.rect.centery = position[1]
            tile = self.game.tilemap.get_tile(current_tile_x, current_tile_y)

            if self.velocity != (0, 0):
                if tile == Tile.SMALL_DOT or tile == Tile.GHOST_NO_UPWARD_TURN_DOT:
                    self.freeze_frames = 1
                    self.game.eat_small_dot(current_tile_x, current_tile_y)
                elif tile == Tile.BIG_DOT:
                    self.freeze_frames = 3
                    self.game.eat_big_dot(current_tile_x, current_tile_y)
        else:
            self._realign()
            self.velocity = (0, 0)
            self.queued_velocity = (0, 0)

    def _has_collision(self, tile_x, tile_y):
        if self.game.tilemap is None:
            return False

        if self._is_in_bounds(tile_x, tile_y):
            return self.game.tilemap.get_tile(tile_x, tile_y) not in self.transparent_tiles

        return False

    def _handle_input(self):
        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_w]:
            self.queued_velocity = (0, -self.speed)

        if pressed_keys[K_a]:
            self.queued_velocity = (-self.speed, 0)

        if pressed_keys[K_s]:
            self.queued_velocity = (0, self.speed)

        if pressed_keys[K_d]:
            self.queued_velocity = (self.speed, 0)

    def _get_speed(self):
        if self.game.pellet_time_seconds > 0:
            return self.pellet_speed_multiplier

        return self.regular_speed_multiplier
