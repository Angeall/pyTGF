from src.display.board import Board, Builder
from src.display.tile import Tile
import pygame
from pygame.locals import *


class SquareTilesBoardBuilder(Builder):
    def __init__(self, surface: pygame.Surface, lines: int, columns: int):
        """

        Args:
            surface: The pygame surface on which draw
            lines: The number of lines wanted in the grid
            columns: The number of columns wanted in the grid
        """
        super().__init__(surface, lines, columns)
        self._borderLength = min(self._maxPixelsPerCol, self._maxPixelsPerLine)

    def _generateTile(self, center: tuple) -> Tile:
        borders = self._getTileBorders(center)
        return Tile(center, borders)

    def _getTileBorders(self, center: tuple) -> list:
        """
        Makes 4 points to make a square
        Args:
            center: The center of the future square

        Returns: A list containing the four points of the square
        """
        return [(center[0] - self._borderLength / 2, center[1] + self._borderLength / 2),
                (center[0] - self._borderLength / 2, center[1] - self._borderLength / 2),
                (center[0] + self._borderLength / 2, center[1] - self._borderLength / 2),
                (center[0] + self._borderLength / 2, center[1] + self._borderLength / 2)]

    def _getFirstCenter(self) -> tuple:

        return ((self._width - (self._borderLength * self._columns)) / 2) + self._borderLength / 2, \
               ((self._height - (self._borderLength * self._lines)) / 2) + self._borderLength / 2

    def _getNextCenter(self, current_center: tuple, column: int) -> tuple:
        if not column == self._columns - 1:
            return current_center[0] + self._borderLength, current_center[1]
        else:  # If the current center is the last of its line
            return self._getFirstCenter()[0], current_center[1] + self._borderLength

if __name__ == "__main__":
    default = 700
    pygame.init()
    clock = pygame.time.Clock()
    builder = SquareTilesBoardBuilder(pygame.Surface((1920, 1080)), 90, 160)

    screen = pygame.display.set_mode((1920, 1080), DOUBLEBUF + HWSURFACE)
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((255, 255, 255))
    screen.blit(background, (0, 0))
    surface = builder.create().surface
    screen.blit(surface, (0, 0))
    pygame.display.flip()
    exit = False
    while not exit:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit = True
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                exit = True
            elif event.type == MOUSEBUTTONDOWN:
                print(event.pos)
                print("ohohoh")
            elif event.type == MOUSEBUTTONUP:
                print("ahahah")
            clock.tick(60)