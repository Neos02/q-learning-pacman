import pygame

from pygame.locals import *

from vector import Vector

pygame.init()

FPS = 60

FONT_NUMBERS = pygame.font.Font("fonts/numbers.ttf", 8)
COLOR_FONT = (222, 222, 255)

SCREEN_WIDTH = 224
SCREEN_HEIGHT = 288
DRAW_SURFACE = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
DISPLAY_SURFACE = pygame.display.set_mode((SCREEN_WIDTH * 2, SCREEN_HEIGHT * 2), flags=DOUBLEBUF)
pygame.display.set_caption('Pac-Man')

pygame.event.set_allowed([QUIT, KEYDOWN])


def load_image(path):
    return pygame.image.load(path).convert_alpha()


if __name__ == '__main__':
    from game import Game

    game = Game()
    game.run()
