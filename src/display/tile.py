from pygame import gfxdraw
import pygame


class NotAPolygonError(BaseException):
    pass


class Tile(object):
    def __init__(self, center: tuple, points: list, position: tuple,
                 external_color: tuple = (0, 0, 0), internal_color: tuple = None) -> None:
        """
        Args:
            center: The equidistant center of the tile
            points: The points that will be used to draw the polygon (not closed), it will be closed by connecting
                    the last and the first point
            position: The location of the tile in the grid
            external_color: RGB (or RGBA) tuple that defines the color of the tile's sides
            internal_color: RGB (or RGBA) tuple that defines the tile's internal color
        """
        self.nbrOfSides = len(points)
        if self.nbrOfSides < 3:
            raise NotAPolygonError("A polygon is made of a minimum of 3 points")
        self.position = position
        self.neighbours = []
        self.center = center
        self.points = points
        self.walkable = False
        self.externalColor = external_color
        self.internalColor = internal_color

    def addNeighbour(self, neighbour_position: tuple) -> None:
        """
        Adds a neighbours, accessible from this tile
        Args:
            neighbour_position: The position of the new neighbour of the tile
        """
        self.neighbours.append(neighbour_position)

    def addNeighbours(self, neighbours_position: list) -> None:
        """
        Add multiple neighbours, accessible from this tile
        Args:
            neighbours_position: A list of all the new accessible position to add to this tile
        """
        self.neighbours.extend(neighbours_position)

    def draw(self, surface: pygame.Surface):
        if self.internalColor is not None:
            gfxdraw.filled_polygon(surface, self.points, self.internalColor)
        gfxdraw.aapolygon(surface, self.points, self.externalColor)
        pygame.draw.aaline(surface, self.externalColor, self.points[-1], self.points[0])
