from abc import ABCMeta, abstractmethod
from queue import Queue
from typing import List

from ..events import Event

__author__ = 'Anthony Rouneau'


class Controller(metaclass=ABCMeta):
    """
    Abstract Controller.
    """
    def __init__(self, player_number: int):
        """
        Instantiates a controller for a unit.

        Args:
            player_number: The identifier of the unit controlled by this controller
        """
        self.moves = Queue()  # Will contain constants that will be interpreted by the game
        self.playerNumber = player_number

    @abstractmethod
    def reactToEvents(self, events: List[Event]) -> None:
        """
        New events have been received for this controller. It must thus react if needed

        Args:
            events: The new event to which this controller must react if needed
        """
        pass
