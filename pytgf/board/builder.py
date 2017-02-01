from typing import List, Tuple, Dict

import pygame

from pytgf.board import Board, Tile
from pytgf.board import TileIdentifier
from pytgf.board.graphics import Color
from pytgf.utils.geom import Coordinates


__author__ = 'Anthony Rouneau'


class Builder:
    """
    Class used to instantiate a test_board board
    """

    _BASE_MARGIN = 33

    def __init__(self, width: int, height: int, lines: int, columns: int) -> None:
        self._width, self._height = width, height
        self._lines = lines
        self._columns = columns
        self._margins = (self._BASE_MARGIN, self._BASE_MARGIN)
        self._borderLength = None  # Init before computeMaxSizeUsingMargins
        self._computeMaxSizeUsingMargins()
        self._backgroundColor = (255, 255, 255)
        self._bordersColor = (0, 0, 0)
        self._tilesVisible = True

    # -------------------- PUBLIC METHODS -------------------- #

    def setTilesVisible(self, visible: bool) -> None:
        """
        If true, the tiles will be visible when the board is drawn

        Args:
            visible: True if the tiles must be visible. False otherwise.
        """
        self._tilesVisible = visible

    def setBordersColor(self, borders_color: Color) -> None:
        """
        Change the color of the board's borders color

        Args:
            borders_color: RGB (or RGBA) tuple for the borders color
        """
        self._bordersColor = borders_color

    def setBackgroundColor(self, background_color: Color) -> None:
        """
        Change the background color of the board

        Args:
            background_color: RGB (or RGBA) tuple for the background color
        """
        self._backgroundColor = background_color

    def setMargins(self, x_margin: float, y_margin: float) -> None:
        """
        Changes the margins of the grid.

        Args:
            x_margin: The new x margin in pixels (if None, keeps the current x margin)
            y_margin: The new y margin in pixels (if None, keeps the current y margin)

        """
        if x_margin is not None:
            self._margins = (x_margin, self._margins[1])
        if y_margin is not None:
            self._margins = (self._margins[0], y_margin)
        self._computeMaxSizeUsingMargins()

    def create(self) -> Board:
        """
        Creates the Board

        Returns: The created board
        """
        tiles_borders, centers, tiles = self._buildGrid()
        borders = self._getBoardBorders(tiles_borders)
        board = Board(len(centers), len(centers[0]),
                      tiles, centers, borders, tiles_borders)
        board.graphics.setBordersColor(self._bordersColor)
        board.graphics.setBackgroundColor(self._backgroundColor)
        board.graphics.setTilesVisible(self._tilesVisible)
        return board

    # -------------------- PROTECTED METHODS -------------------- #

    def _computeMaxSizeUsingMargins(self):
        """
        Computes the max size in pixels of the lines and columns of the grid and stores the result in
                self._maxPixelsPerLine and self._maxPixelsPerCol
        """
        self._maxPixelsPerLine = (self._height - 2 * self._margins[1]) / self._lines
        self._maxPixelsPerCol = (self._width - 2 * self._margins[0]) / self._columns
        self._borderLength = min(self._maxPixelsPerCol, self._maxPixelsPerLine)

    def _getTileBorders(self, center: Coordinates) -> List[Coordinates]:
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

    def _getNextCenter(self, current_center: Coordinates, column: int) -> Coordinates:
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

    def _buildGrid(self) -> Tuple[List[List[List[Coordinates]]], List[List[Coordinates]], List[List[Tile]]]:
        """
        Build and paint (if necessary) the grid on the surface

        Returns: A 3-uple containing:
            - A list of the created tiles, in a matrix [[column, columns, ...], [column, column, ...], more lines, ...]
            - A list of the centers of the tiles in the same format than the other list.
            - A dictionary linking a center to its tile
        """
        current_center = self._getFirstCenter()
        centers = []
        tiles = []
        tiles_borders = []
        for i in range(self._lines):
            tile_line = []
            centers_line = []
            tiles_borders_line = []
            for j in range(self._columns):
                current_center = round(current_center[0], 1), round(current_center[1], 1)
                centers_line.append(current_center)
                neighbours = self._getTileNeighbours(i, j)
                tile_line.append(Tile(identifier=(i, j), center=current_center, neighbours=neighbours, deadly=False,
                                      walkable=True))
                tiles_borders_line.append(self._getTileBorders(current_center))
                current_center = self._getNextCenter(current_center, j)
            tiles.append(tile_line)
            centers.append(centers_line)
            tiles_borders.append(tiles_borders_line)
        return tiles_borders, centers, tiles

    def _getTileNeighbours(self, i: int, j: int) -> Tuple[TileIdentifier]:
        """
        Args:
            i: the row index of the tile for which this method will give the neighbours
            j: the column index of the tile for which this method will give the neighbours

        Returns: The identifiers (x, y) of the neighbours that can be directly accessed through the given (i, j) tile.
        """
        neighbours = ()  # type: Tuple[TileIdentifier]
        if i - 1 >= 0:
            neighbours += ((i - 1, j), )
        if j - 1 >= 0:
            neighbours += ((i, j - 1), )
        if i + 1 < self._lines:
            neighbours += ((i + 1, j), )
        if j + 1 < self._columns:
            neighbours += ((i, j + 1), )
        return neighbours

    @staticmethod
    def _getBoardBorders(tiles_borders: List[List[List[Coordinates]]]) -> List[Tuple[Coordinates, Coordinates]]:
        """
        Computes and returns the borders of the board from the tiles of the board

        Args:
            tiles_borders: The points used to draw the polygon of each tile

        Returns: A list of lines, represented by two points, that defines the borders.
                    (e.g. [((1, 2), (3, 4)), ((0,1), (0,2)), ...])
        """
        top_left = None
        top_right = None
        bottom_left = None
        bottom_right = None
        for x, y in tiles_borders[0][0]:
            if top_left is None or (x <= top_left[0] and y <= top_left[1]):
                top_left = (x, y)
        for x, y in tiles_borders[-1][0]:
            if bottom_left is None or (x <= bottom_left[0] and y >= bottom_left[1]):
                bottom_left = (x, y)
        for x, y in tiles_borders[0][-1]:
            if top_right is None or (x >= top_right[0] and y <= top_right[1]):
                top_right = (x, y)
        for x, y in tiles_borders[-1][-1]:
            if bottom_right is None or (x >= bottom_right[0] and y >= bottom_right[1]):
                bottom_right = (x, y)

        return [(top_left, top_right), (top_right, bottom_right), (bottom_right, bottom_left), (bottom_left, top_left)]


if __name__ == "__main__":
    default = 700
    pygame.init()
    clock = pygame.time.Clock()
    builder = Builder(1920, 1080, 50, 100)
    builder.setBordersColor((255, 0, 0))
    builder.setTilesVisible(True)
    screen = pygame.display.set_mode((1920, 1080), pygame.DOUBLEBUF + pygame.HWSURFACE)
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((255, 255, 255))
    screen.blit(background, (0, 0))
    board = builder.create()
    board.draw(screen)
    pygame.display.flip()
    cancelled = False
    passed_int_color = (255, 255, 255)
    clicked_tile = None
    while not cancelled:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cancelled = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                cancelled = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    clicked_tile = board.getTileByPixel(event.pos)
                    if clicked_tile is not None:
                        i, j = clicked_tile.identifier
                        board.graphics.setInternalColor((255, 0, 0), i, j)
                else:
                    clicked_tile = None
            elif event.type == pygame.MOUSEBUTTONUP:
                if clicked_tile is not None:
                    i, j = clicked_tile.identifier
                    board.graphics.setInternalColor(passed_int_color, i, j)
            board.draw(screen)
            pygame.display.flip()

            clock.tick(60)
