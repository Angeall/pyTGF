from src.display.tile import Tile
from abc import ABCMeta, abstractmethod, abstractproperty
import pygame


class Board(metaclass=ABCMeta):
    def __init__(self, surface: pygame.Surface, tiles: list, centers: list):
        self.tiles = tiles
        self._centers = centers
        self.surface = surface

    @abstractmethod
    def getTileById(self, identifier) -> Tile:
        """

        Args:
            identifier:

        Returns:

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

    def _changeBackgroundColor(self) -> None:
        """
        Paints the surface into the colors saved in "self._backgroundColor"
            that can be changed using "self.setBackgroundColor"
        The background is painted above everything else on the surface,
            hence erasing what's below
        """
        surface = pygame.Surface(self._surface.get_size())

        surface.fill(self._backgroundColor)
        self._surface.blit(surface, (0, 0))

    def _buildGrid(self) -> tuple:
        """
        Build and paint (if necessary) the grid on the surface
        Returns: A couple containing:
            - A list of the created tiles, in a matrix [[column, columns, ...], [column, column, ...], more lines, ...]
            - A list of the centers of the tiles in the same format than the other list.
        """
        current_center = self._getFirstCenter()
        tiles = []
        centers = []
        for i in range(self._lines):
            line = []
            line_centers = []
            for j in range(self._columns):
                tile = self._generateTile(current_center, i, j)
                if self._tilesVisible:
                    tile.draw(self._surface)
                line_centers.append(tile.center)
                line.append(tile)
                current_center = self._getNextCenter(current_center, j)
            tiles.append(line)
            centers.append(line_centers)
        return tiles, centers

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
        self._changeBackgroundColor()
        tiles, centers = self._buildGrid()
        return self.boardType(self._surface, tiles, centers)

    def _computeMaxSizeUsingMargins(self):
        """
        Computes the max size in pixels of the lines and columns of the grid and stores the result in
                self._maxPixelsPerLine and self._maxPixelsPerCol
        """
        self._maxPixelsPerLine = (self._height - self._margins[1]) / self._lines
        self._maxPixelsPerCol = (self._width - self._margins[0]) / self._columns

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



