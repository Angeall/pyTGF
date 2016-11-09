from display.board import Board, Builder
from display.tile import Tile
import pygame
from pygame.locals import *


class SquareBoard(Board):
    def getTileById(self, identifier: tuple) -> Tile:
        """

        Args:
            identifier: For the square board, the identifier is the position (line, column) of the wanted square tile

        Returns:

        """
        return self.tiles[identifier[0]][identifier[1]]


class SquareBoardBuilder(Builder):

    BOARD_TYPE = SquareBoard

    def __init__(self, surface: pygame.Surface, lines: int, columns: int):
        """

        Args:
            surface: The `pygame` surface on which draw
            lines: The number of lines wanted in the grid
            columns: The number of columns wanted in the grid
        """
        super().__init__(surface, lines, columns)

    def _generateTile(self, center: tuple, identifier: tuple) -> Tile:
        """
        Generates a black-outlined square tile with transparent body.
        Args:
            center: The center of the tile to generate
            identifier: A couple containing:
                            - The line on which the tile is placed
                            - The column on which the tile is placed

        Returns: The generated tile
        """
        borders = self._getTileBorders(center)
        tile = Tile(center, borders, identifier)
        (x, y) = identifier
        if x - 1 >= 0:
            tile.addNeighbour((x - 1, y))
        if y - 1 >= 0:
            tile.addNeighbour((x, y - 1))
        if x + 1 < self._columns:
            tile.addNeighbour((x + 1, y))
        if y + 1 < self._lines:
            tile.addNeighbour((x, y + 1))
        return tile

    def _getTileBorders(self, center: tuple) -> list:
        """
        Generates 4 points around the center to make a square
        Args:
            center: The center of the future square

        Returns: A list containing the four points of the square in this order:
            - Bottom left;
            - Top left;
            - Top right;
            - Bottom right
        """
        return [(center[0] - self._borderLength / 2, center[1] + self._borderLength / 2),
                (center[0] - self._borderLength / 2, center[1] - self._borderLength / 2),
                (center[0] + self._borderLength / 2, center[1] - self._borderLength / 2),
                (center[0] + self._borderLength / 2, center[1] + self._borderLength / 2)]

    def _getFirstCenter(self) -> tuple:
        """
        Computes the top-left-most tile center and centers the grid
        Returns: The position (x, y) of the first tile center
        """
        return ((self._width - (self._borderLength * self._columns)) / 2) + self._borderLength / 2, \
               ((self._height - (self._borderLength * self._lines)) / 2) + self._borderLength / 2

    def _getNextCenter(self, current_center: tuple, column: int) -> tuple:
        """
        Computes the next center from the current one
        Args:
            current_center: The center previously handled
            column: The column of the previously handled center
                    (used to determine if we should "line break" the next tile)

        Returns: The coordinates of the next center to handle

        """
        if not column == self._columns - 1:
            return current_center[0] + self._borderLength, current_center[1]
        else:  # If the current center is the last of its line
            return self._getFirstCenter()[0], current_center[1] + self._borderLength

    @property
    def boardType(self) -> type:
        """
        Returns: the type `SquareBoard`
        """
        return SquareBoard

if __name__ == "__main__":
    default = 700
    pygame.init()
    clock = pygame.time.Clock()
    builder = SquareBoardBuilder(pygame.Surface((720, 480)), 2, 5)

    screen = pygame.display.set_mode((720, 480), DOUBLEBUF + HWSURFACE)
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((255, 255, 255))
    screen.blit(background, (0, 0))
    board = builder.create()
    board.draw()
    surf = board.surface
    screen.blit(surf, (0, 0))
    pygame.display.flip()
    exit = False
    passed_int_color = (255, 255, 255)
    while not exit:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit = True
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                exit = True
            elif event.type == MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    tile = board.getTileByPixel(event.pos)
                    if tile is not None:
                        print(tile.identifier)
                        tile.setInternalColor((255, 0, 0))
                else:
                    tile = None
            elif event.type == MOUSEBUTTONUP:
                if tile is not None:
                    tile.setInternalColor(passed_int_color)
            board.draw(screen)
            pygame.display.flip()

            clock.tick(60)
