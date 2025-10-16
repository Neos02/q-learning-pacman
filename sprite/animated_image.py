import pygame
from pygame import Vector2, SurfaceType
from pygame.sprite import Sprite

from utils.direction import Direction


class AnimatedImage(Sprite):

    def __init__(self, path: str, position: Vector2, sprite_size: Vector2, frame_time_ms: int = 1000,
                 sprite_index: int = 0,
                 frame_index: int = 0, direction: Direction = Direction.LEFT) -> None:
        super().__init__()
        self._position = position
        self.spritesheet = pygame.image.load(path).convert_alpha()
        self.sprite_size = sprite_size
        self._frame_index = frame_index
        self.frame_count = self.spritesheet.get_width() / self.sprite_size.x
        self.sprite_index = sprite_index
        self.image = None
        self.rect = pygame.Rect(
            position.x - sprite_size.x / 2,
            position.y - sprite_size.y / 2,
            sprite_size.x,
            sprite_size.y
        )
        self.frame_time_ms = frame_time_ms
        self.time_since_last_frame = 0
        self.direction = direction

    def draw(self, surface: SurfaceType):
        image_rect = pygame.Rect(
            self.frame_index * self.sprite_size.x,
            self.sprite_index * self.sprite_size.y,
            self.sprite_size.x,
            self.sprite_size.y
        )

        match self.direction:
            case Direction.LEFT | Direction.NONE:
                self.image = self.spritesheet.subsurface(image_rect)
            case Direction.UP:
                self.image = pygame.transform.rotate(self.spritesheet.subsurface(image_rect), -90)
            case Direction.DOWN:
                self.image = pygame.transform.rotate(self.spritesheet.subsurface(image_rect), 90)
            case Direction.RIGHT:
                self.image = pygame.transform.rotate(self.spritesheet.subsurface(image_rect), 180)

        surface.blit(self.image, self.rect)

    def move(self, deltatime: float) -> None:
        self.time_since_last_frame += deltatime * 1000

        if self.time_since_last_frame >= self.frame_time_ms:
            self.time_since_last_frame -= self.frame_time_ms
            self.frame_index = (self.frame_index + 1) % self.frame_count

    @property
    def position(self) -> Vector2:
        return self._position

    @position.setter
    def position(self, position: Vector2):
        self._position = position
        self.rect.centerx = int(position.x)
        self.rect.centery = int(position.y)

    @property
    def frame_index(self) -> int:
        return self._frame_index

    @frame_index.setter
    def frame_index(self, frame_index: int):
        self._frame_index = frame_index % self.frame_count
        self.time_since_last_frame = 0
