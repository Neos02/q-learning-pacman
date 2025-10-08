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

    transparent_tiles = [Tile.AIR, Tile.SMALL_DOT, Tile.BIG_DOT, Tile.GHOST_GATE]

    def __init__(self, start_pos=(0, 0), tilemap=None):
        super().__init__()
        self.start_pos = (start_pos[0] + 2 * Ghost.sprite_scale, start_pos[1] - 2 * Ghost.sprite_scale)
        self.rect = pygame.Rect(0, 0, Ghost.sprite_size, Ghost.sprite_size)
        self.image_rect = self.rect.copy()
        self.image = Ghost.spritesheet.subsurface(self.image_rect)
        self.velocity = (0, 0)
        self.last_frame_update_time = 0
        self.rect.move_ip(*self.start_pos)
        self.tilemap = tilemap
        self.queued_velocity = (0, 0)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

        # draw eyes
        surface.blit(
            Ghost.eye_image,
            pygame.Rect(
                self.rect.centerx - Ghost.eye_size[0] - Ghost.sprite_scale,
                self.rect.y + 3 * Ghost.sprite_scale,
                *Ghost.eye_size)
        )
        surface.blit(
            Ghost.eye_image,
            pygame.Rect(
                self.rect.centerx + Ghost.sprite_scale,
                self.rect.y + 3 * Ghost.sprite_scale,
                *Ghost.eye_size
            )
        )

        # draw pupils
        surface.blit(
            Ghost.pupil_image,
            pygame.Rect(
                self.rect.centerx - Ghost.eye_size[0] - Ghost.sprite_scale + Ghost.pupil_size[0],
                self.rect.y + 3 * Ghost.sprite_scale + Ghost.pupil_size[0],
                *Ghost.pupil_size)
        )
        surface.blit(
            Ghost.pupil_image,
            pygame.Rect(
                self.rect.centerx + Ghost.sprite_scale + Ghost.pupil_size[0],
                self.rect.y + 3 * Ghost.sprite_scale + Ghost.pupil_size[0],
                *Ghost.pupil_size
            )
        )

    def move(self, deltatime):
        current_tile_x, current_tile_y = self._get_tile_coordinates(self.rect.centerx, self.rect.centery)

        # only allow input when player is on screen
        if self._is_in_bounds(current_tile_x, current_tile_y):
            queued_tile_x = int(current_tile_x + self.queued_velocity[0] / self.speed)
            queued_tile_y = int(current_tile_y + self.queued_velocity[1] / self.speed)

            if not self._has_collision(queued_tile_x, queued_tile_y):
                self.velocity = self.queued_velocity
                self._realign(
                    self.velocity[0] == 0 and self.velocity[1] != 0,
                    self.velocity[0] != 0 and self.velocity[1] == 0
                )

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
        current_tile_x, current_tile_y = self._get_tile_coordinates(self.rect.centerx, self.rect.centery)
        next_tile_x = int(current_tile_x + self.velocity[0] / self.speed)
        next_tile_y = int(current_tile_y + self.velocity[1] / self.speed)

        if not self._has_collision(current_tile_x, current_tile_y) \
                and not self._has_collision(next_tile_x, next_tile_y):
            self.rect.centerx = position[0]
            self.rect.centery = position[1]

            if self.tilemap.get_tile(current_tile_x, current_tile_y) == Tile.SMALL_DOT:
                self.tilemap.set_tile(current_tile_x, current_tile_y, Tile.AIR)
            elif self.tilemap.get_tile(current_tile_x, current_tile_y) == Tile.BIG_DOT:
                self.tilemap.set_tile(current_tile_x, current_tile_y, Tile.AIR)
        else:
            self._realign()
            self.velocity = (0, 0)
            self.queued_velocity = (0, 0)

    def _has_collision(self, tile_x, tile_y):
        if self.tilemap is None:
            return False

        if self._is_in_bounds(tile_x, tile_y):
            return self.tilemap.get_tile(tile_x, tile_y) not in Ghost.transparent_tiles

        return False

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
