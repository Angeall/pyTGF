import traceback
from collections import namedtuple
from copy import deepcopy, copy
from typing import Union, Dict, Tuple

from gameboard.graphics import BoardGraphics
from scipy.spatial import KDTree
import numpy as np
import pygame

Tile = namedtuple("Tile", "identifier center deadly walkable neighbours")


class Board:
    OUT_OF_BOARD_TILE = Tile(identifier=(-1, -1), center=(-500, -500), deadly=True, walkable=True, neighbours=())

    def __init__(self, size: tuple, lines: int, columns: int, tiles: dict, centers: list, borders: list, points: list):
        """
        Instantiates a game board using the given parameters

        Args:
            size: The size in pixels of the board : (width, height)
            lines: The number of lines in the board
            columns: The number of columns in the board
            tiles:
                A dict containing all the Tile structs, representing the tiles in the board,
                accessible through their identifier (i, j), i being the row index and j being the column index.
            centers: The list containing the matrix of centers for the tiles. Used to associate a pixel to a tile.
            borders: A list of lines, represented by two points each, representing the borders of the board.
                        (e.g. [((1, 2), (3, 4)), ((0,1), (0,2)), ...])
            points: The points that will serve to draw the tiles
        """
        self.size = size
        self.graphics = BoardGraphics(tiles_borders=points, background_color=(255, 255, 255),
                                      border_line_color=(0, 0, 0), borders=borders, tiles_visible=False)
        self.lines = lines
        self.columns = columns
        self._tiles = tiles  # type: Dict[tuple, Tile]
        self._kdTree = KDTree(np.array(centers).reshape(1, len(centers) * len(centers[0]), 2)[0])

    def getTileByPixel(self, pixel: tuple) -> Union[Tile, None]:
        """
        Get the tile located on the given pixel

        Args:
            pixel: The _screen coordinates on which we want to get the tile

        Returns: The tile located on the pixel, or None if there is no tile at this position

        """
        if self.graphics is not None:
            center_index = self._kdTree.query(pixel, 1)[1]
            i = center_index // self.columns
            j = center_index - (self.columns * i)
            if self.graphics.containsPoint(pixel, i, j):
                return self._tiles[(i, j)]
        return None

    def getTileById(self, identifier: tuple) -> Tile:
        """

        Args:
            identifier: A tuple containing the row and the column index of the wanted tile

        Returns: The Tile struct located at the given identifier
        """
        try:
            return self._tiles[identifier]
        except KeyError:
            return self.OUT_OF_BOARD_TILE

    def isAccessible(self, source_identifier: tuple, destination_identifier: tuple) -> bool:
        """

        Args:
            source_identifier:
                The identifier (i, j) that identifies the tile from which we want to access the destination tile
            destination_identifier:
                The identifier (i, j) that identifies the tile that we want to access from the source tile.

        Returns: True if the identifier is in the neighbourhood of the given source tile.
        """
        tile = self._tiles[source_identifier]
        return (tile.neighbours is not None and self.getTileById(destination_identifier).walkable) and (
               destination_identifier in tile.neighbours)

    def getNeighboursIdentifier(self, tile_identifier: tuple) -> Tuple[tuple]:
        """

        Args:
            tile_identifier: The identifier of the tile from which we want the neighbours

        Returns: A tuple containing the identifiers of the neighbours of the tile for which the identifier was given.
        """
        return self._tiles[tile_identifier].neighbours

    def setTileDeadly(self, tile_identifier: tuple, deadly: bool=True) -> None:
        """
        Modifies the "deadly" property of a tile

        Args:
            tile_identifier: The identifier of the tile from which we want the neighbours
            deadly: If True, the tile will be set as "deadly", else, set the tile as "non-deadly"
        """
        tile = self._tiles[tile_identifier]
        self._tiles[tile_identifier] = Tile(identifier=tile.identifier, center=tile.center, neighbours=tile.neighbours,
                                            deadly=deadly, walkable=tile.walkable)

    def setTileNonWalkable(self, tile_identifier: tuple, walkable: bool=False) -> None:
        """
        Modifies the "deadly" property of a tile

        Args:
            tile_identifier: The identifier of the tile from which we want the neighbours
            walkable: If False, the tile will be set as "non-walkable", else, sets the the tile as "walkable"
        """
        tile = self._tiles[tile_identifier]
        self._tiles[tile_identifier] = Tile(identifier=tile.identifier, center=tile.center, neighbours=tile.neighbours,
                                            deadly=tile.deadly, walkable=walkable)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the board on the given surface

        Args:
            surface: The surface on which draw the board
        """
        if self.graphics is not None:
            self.graphics.draw(surface)

    def __deepcopy__(self, memo={}):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k == "_tiles":
                value = {a: b for a, b in v.items()}
            elif k == "_kdTree" or k == "graphics":
                value = None
            else:
                value = v
            setattr(result, k, value)
        return result


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

    def setTilesVisible(self, visible: bool) -> None:
        """
        If true, the tiles will be visible when the board is drawn

        Args:
            visible: True if the tiles must be visible. False otherwise.
        """
        self._tilesVisible = visible

    def setBordersColor(self, borders_color: tuple) -> None:
        """
        Change the color of the board's borders color

        Args:
            borders_color: RGB (or RGBA) tuple for the borders color
        """
        self._bordersColor = borders_color

    def setBackgroundColor(self, background_color: tuple) -> None:
        """
        Change the background color of the board

        Args:
            background_color: RGB (or RGBA) tuple for the background color
        """
        self._backgroundColor = background_color

    def _buildGrid(self) -> tuple:
        """
        Build and paint (if necessary) the grid on the surface

        Returns: A 3-uple containing:
            - A list of the created tiles, in a matrix [[column, columns, ...], [column, column, ...], more lines, ...]
            - A list of the centers of the tiles in the same format than the other list.
            - A dictionary linking a center to its tile
        """
        current_center = self._getFirstCenter()
        centers = []
        tiles = {}
        tiles_borders = []
        for i in range(self._lines):
            centers_line = []
            tiles_borders_line = []
            for j in range(self._columns):
                current_center = round(current_center[0], 1), round(current_center[1], 1)
                centers_line.append(current_center)
                neighbours = self._getTileNeighbours(i, j)
                tiles[(i, j)] = Tile(identifier=(i, j), center=current_center, neighbours=neighbours, deadly=False,
                                     walkable=True)
                tiles_borders_line.append(self._getTileBorders(current_center))
                current_center = self._getNextCenter(current_center, j)
            centers.append(centers_line)
            tiles_borders.append(tiles_borders_line)
        return tiles_borders, centers, tiles

    def _getTileNeighbours(self, i, j):
        """
        Args:
            i: the row index of the tile for which this method will give the neighbours
            j: the column index of the tile for which this method will give the neighbours

        Returns: The identifiers (x, y) of the neighbours that can be directly accessed through the given (i, j) tile.
        """
        neighbours = []
        if i - 1 >= 0:
            neighbours.append((i - 1, j))
        if j - 1 >= 0:
            neighbours.append((i, j - 1))
        if i + 1 < self._lines:
            neighbours.append((i + 1, j))
        if j + 1 < self._columns:
            neighbours.append((i, j + 1))
        return tuple(neighbours)

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
        board = Board((self._width, self._height), len(centers), len(centers[0]),
                      tiles, centers, borders, tiles_borders)
        board.graphics.setBordersColor(self._bordersColor)
        board.graphics.setBackgroundColor(self._backgroundColor)
        board.graphics.setTilesVisible(self._tilesVisible)
        return board

    def _computeMaxSizeUsingMargins(self):
        """
        Computes the max size in pixels of the lines and columns of the grid and stores the result in
                self._maxPixelsPerLine and self._maxPixelsPerCol
        """
        self._maxPixelsPerLine = (self._height - 2 * self._margins[1]) / self._lines
        self._maxPixelsPerCol = (self._width - 2 * self._margins[0]) / self._columns
        self._borderLength = min(self._maxPixelsPerCol, self._maxPixelsPerLine)

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

    @staticmethod
    def _getBoardBorders(tiles_borders: list) -> list:
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
                    i, j = clicked_tile.identifier
                    if clicked_tile is not None:
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
