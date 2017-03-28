import random
from abc import ABCMeta, abstractmethod
from os import listdir
from os.path import isfile, join

import numpy as np
import pandas as pd

__author__ = "Anthony Rouneau"


class FileDecoder(metaclass=ABCMeta):
    def __init__(self, nb_files_per_step: int, path: str, prefix: str=""):
        self._nbFilesPerStep = nb_files_per_step
        self._path = path
        self._files = [f for f in listdir(self._path) if f.startswith(prefix) and isfile(join(self._path, f))]
        random.shuffle(self._files)

    @abstractmethod
    def _parseDataFrame(self, dataframe: pd.DataFrame) -> np.ndarray:
        """
        Must parse the given data frame into a ndarray which contains one data vector per row
        (or a sequence for a LSTM)
        
        Args:
            dataframe: The data frame that was read by  

        Returns: A numpy ndarray containing all the feature vectors that will be sent to the learning model
        """
        pass

    def getNextData(self) -> np.ndarray:
        dataframe = pd.DataFrame()
        for _ in range(self._nbFilesPerStep):
            # TODO: append every files into the dataframe
            pass
        return self._parseDataFrame(dataframe)

