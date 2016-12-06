from abc import ABCMeta
from queue import Queue


class Controller(metaclass=ABCMeta):
    def __init__(self):
        """
        Instantiates a controller for a unit.
        """
        self.moves = Queue()  # Will contain constants that will be interpreted by the game
