"""
Contains the definition of a routine to gather daata
"""
from typing import Iterable, Union, Callable, Optional, Tuple

from pytgf.game import API
from pytgf.learning.component import Data, Component
from pytgf.learning.gatherer import Gatherer

__author__ = "Anthony Rouneau"




class Routine:
    def __init__(self, gatherer: Gatherer):
        self._gatherer = gatherer


class RoutineBuilder:
    """
    Class used to build a Routine
    """
    def __init__(self):
        """
        Instantiates a Routine builder
        """
        self._components = []

    def addComponent(self, methods: Union[Iterable[Callable[[API], Data]], Callable[[API], Data]],
                     reduce_function: Optional[Callable[[Tuple[Data, ...]], Data]]=None) -> None:
        """
        Adds a component to the routine being built

        Args:
            methods: An iterable of methods or just one method that takes an API as a parameter and returns a data
            reduce_function:
                A method that, given a tuple of data, returns a single data (e.g. functools.reduce)
                Unused if the "methods" parameter is a lone method, but necessary if there is more than one method.
        """
        self._components.append(Component(methods, reduce_function))

    def create(self) -> Routine:
        """
        Raises:
            ValueError: If no component was added to this builder, it cannot create a routine, and hence crash

        Returns: The Routine built using this builder
        """
        if len(self._components) == 0:
            raise ValueError("Cannot create a routine with 0 component")
        gatherer = Gatherer(self._components)
        return Routine(gatherer)
