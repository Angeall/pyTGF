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

    def _getBoardBorders(self, tiles: list) -> list:
        """
        Computes and returns the borders of the board from the tiles of the board
        Args:
            tiles: The tiles created for the board

        Returns: A list of lines, represented by two points, that defines the borders.
                    (e.g. [((1, 2), (3, 4)), ((0,1), (0,2)), ...])
        """
        top_left_tile = tiles[0][0]        # type: Tile
        top_right_tile = tiles[0][-1]      # type: Tile
        bottom_left_tile = tiles[-1][0]    # type: Tile
        bottom_right_tile = tiles[-1][-1]  # type: Tile
        top_left = None
        top_right = None
        bottom_left = None
        bottom_right = None
        for x, y in top_left_tile.points:
            if top_left is None or (x <= top_left[0] and y <= top_left[1]):
                top_left = (x, y)
        for x, y in bottom_left_tile.points:
            if bottom_left is None or (x <= bottom_left[0] and y >= bottom_left[1]):
                bottom_left = (x, y)
        for x, y in top_right_tile.points:
            if top_right is None or (x >= top_right[0] and y <= top_right[1]):
                top_right = (x, y)
        for x, y in bottom_right_tile.points:
            if bottom_right is None or (x >= bottom_right[0] and y >= bottom_right[1]):
                bottom_right = (x, y)

        return [(top_left, top_right), (top_right, bottom_right), (bottom_right, bottom_left), (bottom_left, top_left)]

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
    builder = SquareBoardBuilder(pygame.Surface((1920, 1080)), 50, 100)
    builder.setBordersColor((255, 0, 0))
    builder.setTilesVisible(False)
    screen = pygame.display.set_mode((1920, 1080), DOUBLEBUF + HWSURFACE)
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((255, 255, 255))
    screen.blit(background, (0, 0))
    board = builder.create()
    board.draw(screen)
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
