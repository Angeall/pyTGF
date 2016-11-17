import pygame
from characters.controllers.human import Human
from pygame.locals import *
from abc import ABCMeta, abstractmethod
from display.board import Board
import display.board
from display.tile import Tile


class Game(metaclass=ABCMeta):

    def __init__(self, board: Board):
        self.board = board
        self._controllers = []
        self._screen = None
        self._previouslyClickedTile = None

    def run(self, max_fps: int=display.board.MAX_FPS):
        clock = pygame.time.Clock()
        self._screen = pygame.display.set_mode(self.board.surface.get_size(), DOUBLEBUF + HWSURFACE)
        while True:
            self._handleInputs()
            self._refreshScreen()
            clock.tick(max_fps)

    def _refreshScreen(self):
        self.board.draw(self._screen)
        self._screen.blit(self.board.surface, (0, 0))
        pygame.display.flip()

    def _handleInputs(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return
                else:
                    self.dispatchInputToHumanControllers(event.key)
            elif event.type == MOUSEBUTTONDOWN:
                self.dispatchMouseEventToHumanControllers(event.pos)
            elif event.type == MOUSEBUTTONUP:
                self.dispatchMouseEventToHumanControllers(None, click_up=True)

    def dispatchInputToHumanControllers(self, input_key):
        for controller in self._controllers:  # type: Human
            if type(controller) == Human:
                controller.reactToInput(input_key=input_key)

    def dispatchMouseEventToHumanControllers(self, pixel, click_up=False):
        tile = None
        if pixel is not None:
            tile = self.board.getTileByPixel(pixel)
        self._previouslyClickedTile = tile
        mouse_state = pygame.mouse.get_pressed()
        for controller in self._controllers:  # type: Human
            if type(controller) == Human:
                controller.reactToTileClicked(tile, mouse_state, click_up=click_up)
