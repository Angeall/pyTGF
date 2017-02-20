"""
Contains the definition of a data gatherer, which is a class that contains multiple components
"""

from typing import Iterable

from pytgf.game import API
from pytgf.learning.component import Component

__author__ = "Anthony Rouneau"


class Gatherer:
    """
    Class containing multiple components and gathers their data into a data vector using its getData method
    """
    def __init__(self, components: Iterable[Component]):
        """
        Instantiates the data gatherer

        Args:
            components: The components that make this data gatherer
        """
        self.components = components

    def getData(self, api: API):
        """
        Args:
            api: The API that will be used to get the data in the components

        Returns: A list containing the components' data for the given API
        """
        data_vector = []
        for component in self.components:
            data_vector.append(component.getData(api))
        return data_vector
