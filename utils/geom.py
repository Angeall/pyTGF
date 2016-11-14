import numpy as np
from matplotlib.path import Path
from scipy.spatial.distance import euclidean
from scipy.spatial import ConvexHull


# def generate2DRotMatrix(angle: float, radians: bool=False) -> np.array:
#     base = 2*math.pi if radians else 360
#     while angle < 0:
#         angle += base
#     angle = angle if radians else angle*math.pi/180
#     return np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])


def dist(a: tuple, b: tuple):
    return abs(euclidean(a, b))


def vectorize(p1: tuple, p2: tuple, signed: bool=True) -> tuple:
    """
    Computes the vector made by the two input points, p1 to p2
    Args:
        p1: point 1
        p2: point 2
        signed: False will make the vector positive in x and y

    Returns: The vector made by p1 and p2

    """
    (x0, y0) = p1
    (x1, y1) = p2
    if not signed:
        return np.array([abs(float(x1) - float(x0)), abs(float(y1) - float(y0))])
    return float(x1) - float(x0), float(y1) - float(y0)


def get_convex_hull(points: list) -> ConvexHull:
    """
    Get the convex hull of a polygon, represented by the given points
    Args:
        points: The points representing the polygon

    Returns: The convex hull of the polygon
    """
    return ConvexHull(points)


def get_path(points: list, convex_hull: ConvexHull) -> Path:
    """
    Returns the hull path of the given convex hull
    Args:
        points: The points of the polygon
        convex_hull: The convex hul of the polygon

    Returns: The hull path of the polygon

    """
    if type(points) != np.array:
        points = np.array(points)
    return Path(points[convex_hull.vertices])
