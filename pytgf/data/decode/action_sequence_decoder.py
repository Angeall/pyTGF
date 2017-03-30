import numpy as np
import pandas as pd

from pytgf.data.decode.file_decoder import FileDecoder


class ActionSequenceDecoder(FileDecoder):
    """
    
    """

    def __init__(self, nb_files_per_step: int, path: str, player_number: int, nb_players: int, must_win: bool = True):
        super().__init__(nb_files_per_step, path)
        self._playerNumber = player_number
        self._mustWin = must_win
        self._nbPlayers = nb_players

    def _parseDataFrame(self, data_frame: pd.DataFrame) -> np.ndarray:
        actions = np.ndarray((0, len(data_frame)))
        for i in range(self._playerNumber, len(data_frame.loc[0]), self._nbPlayers):
            cur_seq = data_frame.loc[i]
            if not self._mustWin or cur_seq[0] == 1:
                actions = np.vstack((actions, cur_seq))
        return actions



