from display.tile import Tile
from abc import ABCMeta, abstractmethod
from scipy.spatial import KDTree
import numpy as np
import pygame


class Board(metaclass=ABCMeta):
    def __init__(self, surface: pygame.Surface, tiles: list, centers: list, centers_to_tile_ids: dict):
        self._tilesVisible = True
        self.tiles = tiles
        self._backgroundColor = (255, 255, 255)
        self._centers = centers
        self._centersToTileIds = centers_to_tile_ids
        self._kdTree = KDTree(np.array(self._centers))
        self.surface = surface

    def setBackgroundColor(self, background_color: tuple) -> None:
        """
        Change the background color of the board (default: white)
        Args:
            background_color: RGB (or RGBA) tuple for the background color
        """
        self._backgroundColor = background_color

    def _changeBackgroundColor(self) -> None:
        """
        Paints the surface into the colors saved in "self._backgroundColor"
            that can be changed using "self.setBackgroundColor"
        The background is painted above everything else on the surface,
            hence erasing what's below
        """
        surface = pygame.Surface(self.surface.get_size())

        surface.fill(self._backgroundColor)
        self.surface.blit(surface, (0, 0))

    def setTilesVisible(self, visible: bool) -> None:
        """
        If true, the tiles will be visible when the board is drawn
        Args:
            visible: True if the tiles must be visible. False otherwise.
        """
        self._tilesVisible = visible

    def getTileByPixel(self, pixel: tuple) -> Tile:
        """
        Get the tile located on the given pixel
        Args:
            pixel: The screen coordinates on which we want to get the tile

        Returns: The tile located on the pixel, or None if there is no tile at this position

        """
        center_index = self._kdTree.query(pixel, 1)[1]
        center = self._centers[center_index]
        center = round(center[0], 1), round(center[1], 1)
        tile = self.getTileById(self._centersToTileIds[center])
        #TODO

    def draw(self, surface: pygame.Surface):
        self._changeBackgroundColor()
        for line in self.tiles:
            for tile in line:
                if self._tilesVisible:
                    tile.draw(self.surface)
        surface.blit(self.surface, (0, 0))

    @abstractmethod
    def getTileById(self, identifier) -> Tile:
        """
        Gets the tile with the corresponding identifier in the board
        Args:
            identifier: the identifier of the wanted tile in the board

        Returns: The tile corresponding to the identifier

        """
        pass


class Builder(metaclass=ABCMeta):
    """
    Class used to instantiate a display board
    """

    _BASE_MARGIN = 33

    def __init__(self, surface: pygame.Surface, lines: int, columns: int) -> None:
        self._surface = surface
        self._width, self._height = surface.get_size()
        self._lines = lines
        self._columns = columns
        self._margins = (self._BASE_MARGIN, self._BASE_MARGIN)
        self._borderLength = None  # Init before computeMaxSizeUsingMargins
        self._computeMaxSizeUsingMargins()
        self._backgroundColor = (255, 255, 255)
        self._tilesVisible = True

    def setTilesVisible(self, visible: bool) -> None:
        """
        If true, the tiles will be visible when the board is drawn
        Args:
            visible: True if the tiles must be visible. False otherwise.
        """
        self._tilesVisible = visible

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
        self._borderLength = min(self._maxPixelsPerCol, self._maxPixelsPerLine)
        current_center = self._getFirstCenter()
        centers_to_tile_ids = {}
        tiles = []
        centers = []
        for i in range(self._lines):
            line = []
            for j in range(self._columns):
                current_center = round(current_center[0], 1), round(current_center[1], 1)
                tile = self._generateTile(current_center, (i, j))
                centers.append(tile.center)
                line.append(tile)
                centers_to_tile_ids[(round(current_center[0], 1), round(current_center[1], 1))] = tile.identifier
                current_center = self._getNextCenter(current_center, j)
            tiles.append(line)
        return tiles, centers, centers_to_tile_ids

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
        tiles, centers, centers_to_tile_ids = self._buildGrid()
        board = self.boardType(self._surface, tiles, centers, centers_to_tile_ids)  # type: Board
        board.setBackgroundColor(self._backgroundColor)
        board.setTilesVisible(self._tilesVisible)
        return board

    def _computeMaxSizeUsingMargins(self):
        """
        Computes the max size in pixels of the lines and columns of the grid and stores the result in
                self._maxPixelsPerLine and self._maxPixelsPerCol
        """
        self._maxPixelsPerLine = (self._height - 2 * self._margins[1]) / self._lines
        self._maxPixelsPerCol = (self._width - 2 * self._margins[0]) / self._columns

    @property
    @abstractmethod
    def boardType(self) -> type:
        """
        Gets the type of board that this builder creates
        Returns: the type of the board being created
        """
        pass

    @abstractmethod
    def _getTileBorders(self, center: tuple) -> list:
        """
        Generates the borders (non-closed) of a polygon using the given center
        Args:
            center: The center of the polygon to build

        Returns: A list containing the borders of the polygon.
        """
        pass

    @abstractmethod
    def _getNextCenter(self, current_center: tuple, column: int) -> tuple:
        """
        From the center of the current tile, get the center of the next tile
        Args:
            current_center: The center of the current tile
            column: The column on which is placed the current center
        """
        pass

    @abstractmethod
    def _generateTile(self, center: tuple, identifier) -> Tile:
        """
        Generates a tile for the grid
        Args:
            center: The equidistant center of the tile to build
            identifier: The tile identifier in the board

        Returns: The tile built
        """
        pass

    @abstractmethod
    def _getFirstCenter(self) -> tuple:
        """
        Returns: The center of the first tile created
        """
        pass



