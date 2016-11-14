import math
import numpy as np
from scipy.spatial.distance import euclidean


def generate2DRotMatrix(angle: float, radians: bool=False) -> np.array:
    base = 2*math.pi if radians else 360
    while angle < 0:
        angle += base
    angle = angle if radians else angle*math.pi/180
    return np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])


def dist(a: tuple, b: tuple):
    return abs(euclidean(a, b))
