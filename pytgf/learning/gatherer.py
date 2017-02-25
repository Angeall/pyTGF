"""
Contains the definition of a data gatherer, which is a class that contains multiple components
"""

from typing import Iterable

import numpy as np

from pytgf.game import API
from pytgf.learning.component import Component

__author__ = "Anthony Rouneau"


class Gatherer:
    """
    Class containing multiple components and gathers their data into a data vector using its getData method
    """
    def __init__(self, a_priori_components: Iterable[Component], a_posteriori_components: Iterable[Component]=()):
        """
        Instantiates the data gatherer

        Args:
            a_priori_components: The component(s) destined to be gathered before the move is performed
            a_posteriori_components: The component(s) destined to be gathered just after the move was performed
            final_components: The component(s) destined to be gathered once the game ended
        """
        self._aPrioriComponents = a_priori_components
        self._aPosterioriComponents = a_posteriori_components

    def getAPrioriData(self, api: API) -> np.ndarray:
        """
        Args:
            api: The API that will be used to get the data in the components

        Returns: A list containing the a priori components' data for the given API
        """
        return self._getData(api, self._aPrioriComponents)

    def getAPosterioriData(self, api: API) -> np.ndarray:
        """
        Args:
            api: The API that will be used to get the data in the components

        Returns: A list containing the a posteriori components' data for the given API
        """
        return self._getData(api, self._aPosterioriComponents)

    @staticmethod
    def _getData(api: API, components: Iterable[Component]):
        """
        Args:
            api: The API that will be used to get the data in components
            components: The components from which we want to gather the data

        Returns: The data of the given components for the given api
        """
        data_vector = []
        for component in components:
            data_vector.append(component.getData(api))
        return np.array(data_vector)
