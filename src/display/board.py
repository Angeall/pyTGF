from src.display.tile import Tile
from abc import ABCMeta, abstractmethod
import pygame


class Board(object):
    def __init__(self, surface: pygame.Surface, tiles: list, centers: list):
        self.tiles = tiles
        self._centers = centers
        self.surface = surface


class Builder(metaclass=ABCMeta):
    """
    Class used to instantiate a display board
    """

    BASE_MARGIN = 33

    def __init__(self, surface: pygame.Surface, lines: int, columns: int) -> None:
        self._surface = surface
        self._width, self._height = surface.get_size()
        self._lines = lines
        self._columns = columns
        self._margins = (self.BASE_MARGIN, self.BASE_MARGIN)
        self._maxPixelsPerLine = (self._height - self._margins[1]) / lines
        self._maxPixelsPerCol = (self._width - self._margins[0]) / columns
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

    def _changeBackgroundColor(self):
        surface = pygame.Surface(self._surface.get_size())

        surface.fill(self._backgroundColor)
        self._surface.blit(surface, (0, 0))

    def _buildGrid(self):
        current_center = self._getFirstCenter()
        tiles = []
        centers = []
        for i in range(self._lines):
            line = []
            line_centers = []
            for j in range(self._columns):
                tile = self._generateTile(current_center)
                if self._tilesVisible:
                    tile.draw(self._surface)
                line_centers.append(tile.center)
                line.append(tile)
                current_center = self._getNextCenter(current_center, i, j)
            tiles.append(line)
            centers.append(line_centers)
        return tiles, centers

    def create(self) -> Board:
        self._changeBackgroundColor()
        tiles, centers = self._buildGrid()
        return Board(self._surface, tiles, centers)

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
    def _generateTile(self, center: tuple, line: int, column: int) -> Tile:
        """
        Generates a tile for the grid
        Args:
            center: The equidistant center of the tile to build
            line: The line on which the tile is placed in the grid
            column: The column on which the tile is placed in the grid

        Returns: The tile built
        """
        pass

    @abstractmethod
    def _getFirstCenter(self) -> tuple:
        """
        Returns: The center of the first tile created
        """
        pass

