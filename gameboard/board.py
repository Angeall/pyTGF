from copy import deepcopy

from gameboard.graphics import BoardGraphics
from gameboard.tile import Tile
from scipy.spatial import KDTree
import numpy as np
import pygame


class Board:
    """
    TODO:
      - Make a transition between tiles, with a speed
      - Make a principle of inertia for the _units
    """

    def __init__(self, size: tuple, borders: list, points: list, centers: list):
        """
        Instantiates a game board using the given parameters
        Args:
            size: The size in pixels of the board : (width, height)
            borders: A list of lines, represented by two points each, representing the borders of the board.
                        (e.g. [((1, 2), (3, 4)), ((0,1), (0,2)), ...])
            points: The points that will serve to draw the tiles
            centers: A matrix containing the center of each tile that will be on the board
            centers_to_tile_ids: The dict that links the centers to the tile object (so the tiles can be center-indexed)
        """
        self.size = size
        self.graphics = BoardGraphics(tiles_borders=points, background_color=(255, 255, 255), border_line_color=(0, 0, 0),
                                      borders=borders, tiles_visible=False)
        self.tilesCenters = centers
        self.lines = len(centers)
        self.columns = len(centers[0])
        self.borders = borders
        self.backgroundColor = (255, 255, 255)
        self._bordersColor = (0, 0, 0)
        self._centers = centers
        np_centers = np.array(self._centers)

        self._kdTree = KDTree(np_centers.reshape(1, len(centers) * len(centers[0]), 2)[0])

    def getTileIdentifier(self, pixel: tuple):
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
            print(i, j)
            if self.graphics.containsPoint(pixel, i, j):
                return i, j
        return None

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
            if k == "tiles":
                value = []
                for line in v:
                    new_line = []
                    for tile in line:
                        tile_copy = tile.__deepcopy__(memo)
                        new_line.append(tile_copy)
                    value.append(new_line)
            elif k != "_kdTree" and k != "_centersToTileIds" and k != "_centers":
                value = deepcopy(v, memo)
            else:
                value = None
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
        centers_to_tile_ids = {}
        centers = []
        tiles_borders = []
        for i in range(self._lines):
            centers_line = []
            tiles_borders_line = []
            for j in range(self._columns):
                current_center = round(current_center[0], 1), round(current_center[1], 1)
                centers_line.append(current_center)
                tiles_borders_line.append(self._getTileBorders(current_center))
                centers_to_tile_ids[(round(current_center[0], 1), round(current_center[1], 1))] = (i, j)
                current_center = self._getNextCenter(current_center, j)
            centers.append(centers_line)
            tiles_borders.append(tiles_borders_line)
        return tiles_borders, centers, centers_to_tile_ids

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
        tiles_borders, centers, centers_to_tile_ids = self._buildGrid()
        borders = self._getBoardBorders(tiles_borders)
        board = Board((self._width, self._height), borders, tiles_borders, centers, centers_to_tile_ids)
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
        if x + 1 < self._lines:
            tile.addNeighbour((x + 1, y))
        if y + 1 < self._columns:
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
    identifier = None
    while not cancelled:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cancelled = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                cancelled = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    identifier = board.getTileIdentifier(event.pos)
                    if identifier is not None:
                        i, j = identifier
                        board.graphics.setInternalColor((255, 0, 0), i, j)
                else:
                    identifier = None
            elif event.type == pygame.MOUSEBUTTONUP:
                if identifier is not None:
                    board.graphics.setInternalColor(passed_int_color, identifier[0], identifier[1])
            board.draw(screen)
            pygame.display.flip()

            clock.tick(60)

