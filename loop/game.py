import pygame
from pygame.locals import *
from abc import ABCMeta, abstractmethod
from display.board import Board
import display.board
from display.tile import Tile


class Game(metaclass=ABCMeta):

    def __init__(self, board: Board):
        self.board = board

    def run(self, max_fps: int=display.board.MAX_FPS):
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode(self.board.surface.get_size(), DOUBLEBUF + HWSURFACE)
        previously_clicked_tile = None
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        return
                    else:
                        self._onKeyPressed(event.key)
                elif event.type == MOUSEBUTTONDOWN:
                    tile = self.board.getTileByPixel(event.pos)
                    self._onTileClickedDown(tile, pygame.mouse.get_pressed())
                    previously_clicked_tile = tile
                elif event.type == MOUSEBUTTONUP:
                    self._onTileClickedUp(previously_clicked_tile)
                self.board.draw(screen)
                screen.blit(self.board.surface, (0, 0))
                pygame.display.flip()

                clock.tick(max_fps)

    def pressOnKey(self, key_id: int):
        """
        Performs a virtual keyboard interaction
        Args:
            key_id: The ID representing the key pressed on (see the constants of pygame.locals "K_...")
        """
        self._onKeyPressed(key_id)

    def performClickOnTileId(self, tile_id, mouse1: bool, mouse2: bool, mouse3: bool) -> None:
        """
        Performs a virtual click on the tile represented by the given ID (see the game's board tile identifier)
        Args:
            tile_id: The identifier of the tile on which perform the click
            mouse1: True if the left mouse button (i.e. mouse1 button) must be clicked on
            mouse2: True if the right mouse button (i.e. mouse2 button) must be clicked on
            mouse3: True if the middle mouse button (i.e. mouse3 button) must be clicked on
        """
        tile = self.board.getTileById(tile_id)
        self.performClickOnTile(tile, mouse1, mouse2, mouse3)

    def performClickOnTile(self, tile: Tile, mouse1: bool, mouse2: bool, mouse3: bool) -> None:
        """
        Performs a virtual click on the given tile
        Args:
            tile: The tile on which perform the click
            mouse1: True if the left mouse button (i.e. mouse1 button) must be clicked on
            mouse2: True if the right mouse button (i.e. mouse2 button) must be clicked on
            mouse3: True if the middle mouse button (i.e. mouse3 button) must be clicked on
        """
        self._onTileClickedDown(tile, (mouse1, mouse2, mouse3))
        self._onTileClickedUp(tile)

    @abstractmethod
    def _onKeyPressed(self, key_id: int) -> None:
        """
        Method called when a key of the keyboard is pressed
        Args:
            key_id: The int constant representing the key pressed (see pygame.locals constants "K_...")
        """
        pass

    @abstractmethod
    def _onTileClickedDown(self, tile: Tile, mouse_buttons_state: tuple) -> None:
        """
        Method called when a tile is clicked down (i.e. the click has just been pressed)
        Args:
            tile: The tile clicked on
            mouse_buttons_state: A 3-uple of booleans containing the state of the mouse buttons
                                    => (mouse1_pressed, mouse2_pressed, mouse3_pressed)
        """
        pass

    @abstractmethod
    def _onTileClickedUp(self, tile: Tile) -> None:
        """
        Method called when a tile is clicked up (i.e. the click has just been released)
        Args:
            tile: The tile that was clicked down on
        """
        pass

