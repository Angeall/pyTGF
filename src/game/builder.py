import os, sys
import pygame
from pygame.locals import *
from pygame import gfxdraw


class Builder(object):
    """
    Class used to instantiate a game board
    """

    def __init__(self, width: int, height: int) -> None:
        """
        Args:
            width:
            height:
        """
        pass

def _init() -> None:
    default = 700
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((700, 400), DOUBLEBUF + HWSURFACE)
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250))
    screen.blit(background, (0, 0))
    pygame.display.flip()
    pygame.gfxdraw.aapolygon(pygame.display.get_surface(), [(100, 100), (100, 150), (125, 180), (150, 150), (150, 100)], (0, 0, 0))
    pygame.display.flip()
    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            elif event.type == MOUSEBUTTONDOWN:
                print(event.pos)
                print("ohohoh")
            elif event.type == MOUSEBUTTONUP:
                print("ahahah")
            clock.tick(60)

_init()
