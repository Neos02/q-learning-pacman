import pygame

from pygame.locals import *

pygame.init()

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags=DOUBLEBUF)
pygame.display.set_caption('Pac-Man')

pygame.event.set_allowed([QUIT, KEYDOWN])

if __name__ == '__main__':
    from game import Game
    game = Game()
    game.run()
