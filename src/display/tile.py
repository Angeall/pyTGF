from pygame import gfxdraw
import pygame


class NotAPolygonError(BaseException):
    pass


class Tile(object):
    def __init__(self, center: tuple, points: list, external_color: tuple=(0, 0, 0), internal_color: tuple=None) -> None:
        """
        Args:
            center: The equidistant center of the tile
            points: The points that will be used to draw the polygon (not closed), it will be closed by connecting
                    the last and the first point
            external_color: RGB (or RGBA) tuple that defines the color of the tile's sides
            internal_color: RGB (or RGBA) tuple that defines the tile's internal color
        """
        self.nbrOfSides = len(points)
        if self.nbrOfSides < 3:
            raise NotAPolygonError("LOLOL")
        self.center = center
        self.points = points
        self.externalColor = external_color
        self.internalColor = internal_color

    def draw(self, surface: pygame.Surface):
        if self.internalColor is not None:
            gfxdraw.filled_polygon(surface, self.points, self.internalColor)
        gfxdraw.aapolygon(surface, self.points, self.externalColor)
        pygame.draw.aaline(surface, self.externalColor, self.points[-1], self.points[0])




