"""
File containing the definition of a Special Event, meant to be sent to ControllerWrappers to inform them on new game
information
"""

from .event import Event

__author__ = 'Anthony Rouneau'


class SpecialEvent(Event):
    """
    Defines a Special event, telling ControllerWrappers that the game ended, or that its unit has been killed or
    resurrected.
    """
    RESURRECT_UNIT = 2
    UNIT_KILLED = 1
    END = 0

    def __init__(self, flag: int):
        """
        Instantiates the Event with the given flag (see the class constants)

        Args:
            flag: The flag with which the event must be created.
        """
        self.flag = flag
