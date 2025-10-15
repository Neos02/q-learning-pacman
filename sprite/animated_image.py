import pygame
from pygame import Vector2, SurfaceType
from pygame.sprite import Sprite


class AnimatedImage(Sprite):

    def __init__(self, path: str, sprite_size: Vector2, frame_time_ms: int = 1000, sprite_index: int = 0,
                 frame_index: int = 0) -> None:
        super().__init__()
        self.spritesheet = pygame.image.load(path).convert_alpha()
        self.sprite_size = sprite_size
        self.image_rect = pygame.Rect(
            frame_index * sprite_size.x,
            sprite_index * sprite_size.y,
            sprite_size.x,
            sprite_size.y
        )
        self.image = self.spritesheet.subsurface(self.image_rect)
        self.rect = self.image.get_rect()
        self.frame_time_ms = frame_time_ms
        self.last_frame_time_ms = 0

    def draw(self, surface: SurfaceType):
        ticks = pygame.time.get_ticks()

        if ticks - self.last_frame_time_ms > self.frame_time_ms:
            self.last_frame_time_ms = ticks
            self.image_rect.left = (self.image_rect.left + self.image_rect.width) % self.spritesheet.get_width()
            self.image = self.spritesheet.subsurface(self.image_rect)

        surface.blit(self.image, self.rect)
