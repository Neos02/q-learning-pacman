import pygame

from pygame.locals import *

pygame.init()

FPS = 60

SCREEN_WIDTH = 448
SCREEN_HEIGHT = 576
DISPLAY_SURFACE = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags=DOUBLEBUF)
pygame.display.set_caption('Pac-Man')

pygame.event.set_allowed([QUIT, KEYDOWN])


def load_image(path, scale=2):
    return pygame.transform.scale_by(pygame.image.load(path).convert_alpha(), scale)


if __name__ == '__main__':
    from game import Game

    game = Game()
    game.run()
