import sys
import pygame

from pygame.locals import *


class Game:

    def __init__(self):
        pass

    def run(self):
        while 1:
            Game.handle_events()

            pygame.display.update()

    @staticmethod
    def handle_events():
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
