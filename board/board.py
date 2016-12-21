from board.tile import Tile
from abc import ABCMeta, abstractmethod
from scipy.spatial import KDTree
import numpy as np
import pygame


class Board(metaclass=ABCMeta):
    """
    TODO:
      - Make a transition between tiles, with a speed
      - Make a principle of inertia for the _units
    """

    def __init__(self, size: tuple, borders: list, tiles: list, centers: list, centers_to_tile_ids: dict):
        """
        Instantiates a game board using the given parameters
        Args:
            size: The size in pixels of the board : (width, height)
            borders: A list of lines, represented by two points each, representing the borders of the board.
                        (e.g. [((1, 2), (3, 4)), ((0,1), (0,2)), ...])
            tiles: A list of tiles that will be on the board
            centers: The list of the tiles centers
            centers_to_tile_ids: The dict that links the centers to the tile object (so the tiles can be center-indexed)
        """
        self.size = size
        self._tilesVisible = True
        self.tiles = tiles
        self.borders = borders
        self.backgroundColor = (255, 255, 255)
        self._bordersColor = (0, 0, 0)
        self._centers = centers
        self._centersToTileIds = centers_to_tile_ids
        self._kdTree = KDTree(np.array(self._centers))

    def setBordersColor(self, borders_color: tuple) -> None:
        """
        Change the color of the board's borders color
        Args:
            borders_color: RGB (or RGBA) tuple for the borders color
        """
        self._bordersColor = borders_color

    def setBackgroundColor(self, background_color: tuple) -> None:
        """
        Change the background color of the board (default: white)
        Args:
            background_color: RGB (or RGBA) tuple for the background color
        """
        self.backgroundColor = background_color

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
            pixel: The _screen coordinates on which we want to get the tile

        Returns: The tile located on the pixel, or None if there is no tile at this position

        """
        center_index = self._kdTree.query(pixel, 1)[1]
        center = self._centers[center_index]
        center = round(center[0], 1), round(center[1], 1)
        tile = self.getTileById(self._centersToTileIds[center])
        if tile.containsPoint(pixel):
            return tile
        return None

    def _drawBackground(self, surface: pygame.Surface) -> None:
        """
        Paints the surface into the colors saved in "self.backgroundColor"
            that can be changed using "self.setBackgroundColor"
        The background is painted above everything else on the surface,
            hence erasing what's below
        Args:
            surface: The surface onto which draw the background
        """
        surf = pygame.Surface(surface.get_size())
        surf.fill(self.backgroundColor)
        surface.blit(surf, (0, 0))

    def _drawBorders(self, surface: pygame.Surface) -> None:
        """
        Draws the borders of the board, without drawing any tile.
        Args:
            surface: The surface onto which draw the borders
        """
        for (p1, p2) in self.borders:
            pygame.draw.aaline(surface, self._bordersColor, p1, p2)

    def _drawTiles(self, surface: pygame.Surface) -> None:
        """
        Draw the tiles onto the board
        Args:
            surface: The surface onto which draw the tiles
        """
        for line in self.tiles:
            for tile in line:
                if self._tilesVisible:
                    tile.draw(surface)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the board on the given surface
        Args:
            surface: The surface on which draw the board
        """
        # Using a temporary surface allows to paint only once on the displayed surface (avoid delay between components)
        surf = pygame.Surface(surface.get_size())
        self._drawBackground(surf)
        self._drawTiles(surf)
        self._drawBorders(surf)
        surface.blit(surf, (0, 0))

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
        borders = self._getBoardBorders(tiles)
        board = self.boardType((self._width, self._height), borders, tiles, centers, centers_to_tile_ids)  # type: Board
        board.setBordersColor(self._bordersColor)
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
        self._borderLength = min(self._maxPixelsPerCol, self._maxPixelsPerLine)

    @property
    @abstractmethod
    def boardType(self) -> type:
        """
        Gets the type of board that this builder creates
        Returns: the type of the board being created
        """
        pass

    @abstractmethod
    def _getBoardBorders(self, tiles: list) -> list:
        """
        Computes and returns the borders of the board from the tiles of the board
        Args:
            tiles: The tiles created for the board

        Returns: A list of lines, represented by two points, that defines the borders.
                    (e.g. [((1, 2), (3, 4)), ((0,1), (0,2)), ...])
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
