"""
File containing the Definition of Color (a 3-uple of int) and BoardGraphics that
represents the graphical part of a Board
"""

from typing import Tuple, List, Union

import numpy as np
import pygame
from pygame import gfxdraw
from scipy.spatial import KDTree

import pytgf.utils.geom
from pytgf.utils.geom import Coordinates


__author__ = 'Anthony Rouneau'


class NotAPolygonError(Exception):
    """
    Exception raised when a Tile is trying to be created without being a closed polygon
    """
    pass


Color = Tuple[int, int, int]
Width = int
Height = int


class BoardGraphics:
    """
    Class defining the graphical part of a Board.
    It contains the background color, the color of each tile, and the polygon formed by the tiles
    """

    _BORDER_COLOR = 0
    _INTERNAL_COLOR = 1

    _TILE_LENGTH_EPSILON = 0.1

    def __init__(self, size: Tuple[Width, Height], tiles_borders: list, background_color: Color,
                 border_line_color: Color, centers: List[List[Coordinates]],
                 borders: List[Tuple[Coordinates, Coordinates]], tiles_visible: bool):
        """
        Instantiates a BoardGraphics object, representing the graphical part of the board
        Args:
            tiles_borders: The points that will serve to draw the tiles
            background_color: The color of the background of the board
            border_line_color: The color of the border of the ground
            centers: The list containing the matrix of centers for the tiles. Used to associate a pixel to a tile.
            borders:
                A list of lines, represented by two points each, representing the borders of the board.
                 (e.g. [((1, 2), (3, 4)), ((0,1), (0,2)), ...])
            tiles_visible: If true, the borders of each tile will be drawn by the "draw" method.
        """
        self.size = size
        self.sideLength = pytgf.utils.geom.dist(tiles_borders[0][0][-1], tiles_borders[0][0][0])
        self.nbrOfSides = len(tiles_borders[0][0])
        self._tilesVisible = tiles_visible
        self._borders = borders
        self._backgroundColor = background_color
        self._borderLineColor = border_line_color
        self._colorMatrix = self._initColorMatrix(len(tiles_borders), len(tiles_borders[0]))
        self._drawMatrix = self._initDrawMatrix(tiles_borders)
        self._columns = len(centers[0])
        self._kdTree = KDTree(np.array(centers).reshape(1, len(centers) * len(centers[0]), 2)[0])  # type: KDTree

    # -------------------- PUBLIC METHODS -------------------- #

    def getBorderColor(self, i: int, j: int) -> Color:
        """
        Gets the border color of the tile located at the position (i, j)
        Args:
            i: The row index of the wanted tile
            j: The column index of the wanted tile

        Returns: A tuple containing the (R, G, B) components of the (i, j)th tile's border color
        """
        return self._colorMatrix[i][j][self._BORDER_COLOR]

    def setBorderColor(self, border_color: Color, i: int=None, j: int=None) -> None:
        """
        Sets the border color of the board. We can distinguish four cases:
            - i = j = None:      Sets the border color of the entire board
            - i = None, j = int: Sets the border color of the j column
            - i = int, j = None: Sets the border color of the i line
            - i = int, j = int:  Sets the border color of the (i, j) tile

        Args:
            border_color: The new border color to set
            i: (Optional) The row index of the wanted tile
            j: (Optional) The column index of the wanted tile
        """
        self._setTilesColor(border_color, i, j, internal=False)

    def getInternalColor(self, i: int, j: int) -> Color:
        """
        Gets the internal color of the tile located at the position (i, j)
        Args:
            i: The row index of the wanted tile
            j: The column index of the wanted tile

        Returns: A tuple containing the (R, G, B) components of the (i, j)th tile's internal color
        """
        return self._colorMatrix[i][j][self._INTERNAL_COLOR]

    def setInternalColor(self, internal_color: Color, i: int = None, j: int = None) -> None:
        """
        Sets the border color of the board. We can distinguish four cases:
            - i = j = None:      Sets the internal color of the entire board
            - i = None, j = int: Sets the internal color of the j column
            - i = int, j = None: Sets the internal color of the i line
            - i = int, j = int:  Sets the internal color of the (i, j) tile

        Args:
            internal_color: The new internal color to set
            i: (Optional) The row index of the wanted tile
            j: (Optional) The column index of the wanted tile
        """
        self._setTilesColor(internal_color, i, j, internal=True)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the board on the given surface
        Args:
            surface: The surface on which draw the board
        """
        # Using a temporary surface allows to paint only once on the displayed surface (avoid delay between components)
        surf = pygame.Surface(surface.get_size())
        self._drawBackground(surf)
        if self._tilesVisible:
            self._drawTiles(surf)
        self._drawBorders(surf)
        surface.blit(surf, (0, 0))

    def setBordersColor(self, borders_color: Color) -> None:
        """
        Change the color of the board's borders color
        Args:
            borders_color: RGB (or RGBA) tuple for the borders color
        """
        self._borderLineColor = borders_color

    def setBackgroundColor(self, background_color: Color) -> None:
        """
        Change the background color of the board (default: white)
        Args:
            background_color: RGB (or RGBA) tuple for the background color
        """
        self._backgroundColor = background_color

    def setTilesVisible(self, visible: bool) -> None:
        """
        If true, the tiles will be visible when the board is drawn
        Args:
            visible: True if the tiles must be visible. False otherwise.
        """
        self._tilesVisible = visible

    def containsPoint(self, point: Coordinates, i: int, j: int) -> bool:
        """
        Checks if a point lies inside the tile (i, j)

        Args:
            point: The point to check
            i: The row index of the tile to check
            j: The column index of the tile to check

        Returns: True if the point is inside and False otherwise
        """
        points = self._drawMatrix[i][j]
        convex_hull = pytgf.utils.geom.get_convex_hull(points)
        hull_path = pytgf.utils.geom.get_path(points, convex_hull)
        return hull_path.contains_point(point)

    # -------------------- PROTECTED METHODS -------------------- #

    def _setTilesColor(self, color: Color, i: int, j: int, internal: bool=True):
        """
        Sets the (i, j) tile's border color

        Args:
            color: The color to give to the border of the (i, j) tile
            i: The row index of the tile
            j: The column index of the tile
            internal: If true, sets the internal color of the tile, else, sets the border color
        """
        if i is None:
            if j is None:  # FILL THE ENTIRE BOARD
                for k in range(len(self._colorMatrix)):
                    for l in range(len(self._colorMatrix[0])):
                        self._setTileColor(color, k, l, internal)
            else:  # FILL A COLUMN
                for k in range(len(self._colorMatrix)):
                    self._setTileColor(color, k, j, internal)

        elif j is None:  # FILL A LINE
            for l in range(len(self._colorMatrix[i])):
                self._setTileColor(color, i, l, internal)
        else:
            self._setTileColor(color, i, j, internal)

    def _setTileColor(self, color: Color, i: int, j: int, internal: bool=True) -> None:
        """
        Sets the (i, j) tile's border color

        Args:
            color: The color to give to the border of the (i, j) tile
            i: The row index of the tile
            j: The column index of the tile
            internal: If true, sets the internal color of the tile, else, sets the border color
        """
        assert i is not None and j is not None
        internal_color = self._colorMatrix[i][j][self._INTERNAL_COLOR]
        border_color = self._colorMatrix[i][j][self._BORDER_COLOR]
        temp = [None, None]
        temp[self._INTERNAL_COLOR] = internal_color
        temp[self._BORDER_COLOR] = border_color
        if internal:
            temp[self._INTERNAL_COLOR] = color
        else:
            temp[self._BORDER_COLOR] = color
        temp = internal_color, color

        self._colorMatrix[i] = self._colorMatrix[i][:j] + (tuple(temp), ) + self._colorMatrix[i][j+1:]

    def _drawTiles(self, surface: pygame.Surface) -> None:
        """
        Draws the tiles on the given surface

        Args:
            surface: The surface on which the tiles will be drawn
        """
        for i in range(len(self._drawMatrix)):
            for j in range(len(self._drawMatrix[0])):
                points = self._drawMatrix[i][j]
                internal_color = self._colorMatrix[i][j][self._INTERNAL_COLOR]
                border_color = self._colorMatrix[i][j][self._BORDER_COLOR]
                if internal_color is not None:
                    gfxdraw.filled_polygon(surface, points, internal_color)
                gfxdraw.aapolygon(surface, points, border_color)

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
        surf.fill(self._backgroundColor)
        surface.blit(surf, (0, 0))

    def _drawBorders(self, surface: pygame.Surface) -> None:
        """
        Draws the borders of the board, without drawing any tile.

        Args:
            surface: The surface onto which draw the borders
        """
        for (p1, p2) in self._borders:
            pygame.draw.aaline(surface, self._borderLineColor, p1, p2)

    def _initDrawMatrix(self, points: List[List[List[Coordinates]]]) -> List[Tuple[List[Coordinates], ...]]:
        """
        Initializes the matrix that will be used to draw the board.

        Args:
            points: A matrix of polygon's borders for the tiles

        Returns: A matrix of tuples, containing a center for the tile, followed by the points of the tile's polygon
        """
        draw_matrix = []
        for i in range(len(points)):
            line = ()
            for j in range(len(points[0])):
                if len(points[i][j]) < 3:
                    raise NotAPolygonError("A polygon is made of minimum 3 points")
                assert self._isEquilateral(points[i][j])
                line += (tuple(points[i][j]), )
            draw_matrix.append(line)
        return draw_matrix

    def _initColorMatrix(self, lines: int, rows: int) -> list:
        """
        Initializes the color matrix with black borders and white internal

        Args:
            lines: The number of lines of this board
            rows: The number of rows of this board

        Returns: A matrix of tuples, containing a border color triplet (R,G,B) and an internal color triplet (R,G,B)
        """
        color_matrix = []
        for _ in range(lines):
            line = ()
            for _2 in range(rows):
                temp = [None, None]
                temp[self._BORDER_COLOR] = (0, 0, 0)
                temp[self._INTERNAL_COLOR] = (255, 255, 255)
                line += (tuple(temp), )
            color_matrix.append(line)
        return color_matrix

    def _isEquilateral(self, points: List[Coordinates]) -> bool:
        """
        Checks if the polygon formed by the given points is equilateral

        Returns: True if all the length are equal with a epsilon-accuracy.
        """
        length = pytgf.utils.geom.dist(points[0], points[1])
        if abs(length - self.sideLength) > self._TILE_LENGTH_EPSILON:
            return False
        i = 1
        while i < len(points) - 1:
            computed_length = pytgf.utils.geom.dist(points[i], points[i + 1])
            if abs(computed_length - length) > self._TILE_LENGTH_EPSILON:
                return False
            i += 1
        return abs(pytgf.utils.geom.dist(points[len(points) - 1], points[0]) - length) < self._TILE_LENGTH_EPSILON

    def getTileIdByPixel(self, pixel: Coordinates) -> Union[Tuple[int, int], None]:
        """
        Get the identifier of the tile located on the given pixel

        Args:
            pixel: The screen coordinates on which we want to get the tile

        Returns: The identifier of the tile located on the pixel, or None if there is no tile at this position
        """
        center_index = self._kdTree.query(pixel, 1)[1]
        i = center_index // self._columns
        j = center_index - (self._columns * i)
        if self.containsPoint(pixel, i, j):
            return i, j
