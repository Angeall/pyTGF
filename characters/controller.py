from abc import ABCMeta, abstractmethod
import pygame.locals
from queue import Queue


ARROWS_PLAYER1 = [pygame.locals.K_UP, pygame.locals.K_DOWN, pygame.locals.K_RIGHT, pygame.locals.K_LEFT]
ARROWS_PLAYER2 = [pygame.locals.K_z, pygame.locals.K_s, pygame.locals.K_d, pygame.locals.K_q]
ARROWS_PLAYER2_QWERTY = [pygame.locals.K_w, pygame.locals.K_s, pygame.locals.K_d, pygame.locals.K_a]
ARROWS_PLAYER3 = [pygame.locals.K_o, pygame.locals.K_l, pygame.locals.K_m, pygame.locals.K_k]


class Controller(metaclass=ABCMeta):
    def __init__(self):
        """
        Instantiates a controller for a unit.
        """
        self.moves = Queue()
