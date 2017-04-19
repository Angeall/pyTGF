import random
from abc import ABCMeta, abstractmethod
from os import listdir, remove
from os.path import isfile, join

import numpy as np
import pandas as pd

__author__ = "Anthony Rouneau"


class FileDecoder(metaclass=ABCMeta):
    def __init__(self, nb_files_per_step: int, path: str, prefix: str=""):
        self._nbFilesPerStep = nb_files_per_step
        self._path = path
        self._fileNames = [join(self._path, f) for f in listdir(self._path)
                           if f.startswith(prefix) and isfile(join(self._path, f))]
        self._usedFiles = []
        random.shuffle(self._fileNames)

    @abstractmethod
    def _parseDataFrame(self, data_frame: pd.DataFrame) -> np.ndarray:
        """
        Must parse the given data frame into a ndarray which contains one data vector per row
        (or a sequence for a LSTM)
        
        Args:
            data_frame: The data frame that was read by  

        Returns: A numpy ndarray containing all the feature vectors that will be sent to the learning model
        """
        pass

    def hasData(self) -> bool:
        """
        Returns: True if there remain files to be read
        """
        return len(self._fileNames) > 0

    def getNextData(self) -> np.ndarray:
        """
        Returns: The ndarray representing the data contained in the "nb_file_per_step" next random files.
        """
        data_frame = pd.DataFrame()
        for _ in range(min(self._nbFilesPerStep, len(self._fileNames))):
            file_name = self._fileNames.pop()
            df = pd.read_csv(file_name)
            self._usedFiles.append(file_name)
            data_frame = data_frame.append(df, ignore_index=True)
        return self._parseDataFrame(data_frame)

    def deleteUsedFiles(self):
        """
        Deletes the files that were used (and not already deleted) 
        """
        for file_name in self._usedFiles:
            remove(file_name)
        self._usedFiles = []
