from abc import ABCMeta
from queue import Queue


class Controller(metaclass=ABCMeta):
    def __init__(self, player_number: int):
        """
        Instantiates a controller for a unit.
        Args:
            player_number: The identifier of the unit controlled by this controller
        """
        self.moves = Queue()  # Will contain constants that will be interpreted by the rules
        self.playerNumber = player_number

