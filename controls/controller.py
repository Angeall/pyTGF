from abc import ABCMeta, abstractmethod
from queue import Queue

from controls.event import Event


class Controller(metaclass=ABCMeta):
    def __init__(self, player_number: int):
        """
        Instantiates a controller for a unit.
        Args:
            player_number: The identifier of the unit controlled by this controller
        """
        self.moves = Queue()  # Will contain constants that will be interpreted by the game
        self.playerNumber = player_number

    @abstractmethod
    def reactToEvent(self, event: Event):
        pass
