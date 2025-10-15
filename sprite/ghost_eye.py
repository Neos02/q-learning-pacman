import pygame
from pygame import Vector2, SurfaceType
from pygame.sprite import Sprite
from main import load_image
from utils.direction import Direction


class GhostEye(Sprite):
    eye_image = load_image("images/ghost-eye.png")
    eye_white_image = eye_image.subsurface(pygame.Rect(0, 0, 4, 5))
    pupil_image = eye_image.subsurface(pygame.Rect(0, 5, 2, 2))

    def __init__(self, position: Vector2, offset: Vector2 = Vector2(0, 0)) -> None:
        super().__init__()
        image_size = (2 + self.eye_white_image.get_width(), 2 + self.eye_white_image.get_height())
        self.image = pygame.Surface(image_size, pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.offset = offset
        self.direction = Direction.DOWN
        self.move(position, self.direction)

    def draw(self, surface: SurfaceType) -> None:
        self.image.fill((0, 0, 0, 0))

        match self.direction:
            case Direction.LEFT:
                self.image.blit(self.eye_white_image, (0, 2))
                self.image.blit(self.pupil_image, (0, 4))
            case Direction.UP:
                self.image.blit(self.eye_white_image, (1, 0))
                self.image.blit(self.pupil_image, (2, 0))
            case Direction.RIGHT:
                self.image.blit(self.eye_white_image, (2, 2))
                self.image.blit(self.pupil_image, (4, 4))
            case Direction.DOWN | Direction.NONE:
                self.image.blit(self.eye_white_image, (1, 2))
                self.image.blit(self.pupil_image, (2, 5))

        surface.blit(self.image, self.rect)

    def move(self, position: Vector2, direction: Vector2) -> None:
        self.rect.centerx = int(position.x + self.offset.x)
        self.rect.centery = int(position.y + self.offset.y)
        self.direction = direction
