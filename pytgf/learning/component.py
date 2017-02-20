"""
Contains the definition of the "Component" class, which is used in a data gathering routine
"""

from typing import Callable, Any, Union, Iterable, Tuple, Optional

from pytgf.game import API

__author__ = "Anthony Rouneau"


Data = Any


class Component:
    def __init__(self, methods: Union[Iterable[Callable[[API], Data]], Callable[[API], Data]],
                 reduce_function: Optional[Callable[[Tuple[Data, ...]], Data]]=None):
        """
        Creates a component of a data gather routine

        Args:
            methods: An iterable of methods or just one method that takes an API as a parameter and returns a data
            reduce_function:
                A method that, given a tuple of data, returns a single data (e.g. functools.reduce)
                Unused if the "methods" parameter is a lone method, but necessary if there is more than one method.

        Raises:
            AttributeError: When the reduce_function is None while the methods is an iterable;
        """
        self.methods = None  # type: Iterable[Callable[[API], Any]]
        if isinstance(methods, list) or isinstance(methods, tuple):
            if reduce_function is None:
                msg = "Got an iterable of methods, but no reduce_function."
                msg2 = "The component would be unable to process the data"
                raise AttributeError(msg + " " + msg2)
            self.methods = methods
        else:
            self.methods = [methods]

    def getData(self, api: API) -> Any:
        """
        Get the data of this component for the given API

        Args:
            api: The API with which the data will be retrieved

        Returns: The data of this component for the given API
        """
        if len(self.methods) == 1:
            return self.methods[0](api)
        else:
            data = []
            for method in self.methods:
                data.append(method(api))
            return self.combineData(*data)

    def combineData(self, *data: Iterable[Any]) -> Any:
        """
        Combine multiple data into one

        Args:
            *data: The data to combine

        Raises:
            NotImplementedError: When this method is not explicitly implemented

        Returns: The result of the combination of data (e.g. data = [2, 5] -> (2 + 5)/2)
        """
        explanation = "This component must combine multiple values, but it does not know how to do this..."
        solution = "Please implement its \"combineData\" method returning the right combination of data"
        raise NotImplementedError(explanation + " " + solution)


