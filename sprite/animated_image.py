import pygame
from pygame import Vector2, SurfaceType
from pygame.sprite import Sprite

from utils.direction import Direction


class AnimatedImage(Sprite):

    def __init__(self, path: str, sprite_size: Vector2, frame_time_ms: int = 1000, sprite_index: int = 0,
                 frame_index: int = 0, direction: Direction = Direction.LEFT) -> None:
        super().__init__()
        self.spritesheet = pygame.image.load(path).convert_alpha()
        self.sprite_size = sprite_size
        self._frame_index = frame_index
        self.frame_count = self.spritesheet.get_width() / self.sprite_size.x
        self.sprite_index = sprite_index
        self.image = None
        self.rect = pygame.Rect(0, 0, sprite_size.x, sprite_size.y)
        self.frame_time_ms = frame_time_ms
        self.last_frame_time_ms = 0
        self.direction = direction

    def draw(self, surface: SurfaceType):
        ticks = pygame.time.get_ticks()

        if ticks - self.last_frame_time_ms > self.frame_time_ms:
            self.last_frame_time_ms = ticks
            self.frame_index = (self.frame_index + 1) % self.frame_count

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

    @property
    def frame_index(self) -> int:
        return self._frame_index

    @frame_index.setter
    def frame_index(self, frame_index: int):
        self._frame_index = frame_index % self.frame_count
        self.last_frame_time_ms = pygame.time.get_ticks()
