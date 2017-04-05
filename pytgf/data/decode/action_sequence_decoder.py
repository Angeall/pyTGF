import numpy as np
import pandas as pd

from pytgf.data.decode.file_decoder import FileDecoder


class ActionSequenceDecoder(FileDecoder):
    """
    
    """

    def __init__(self, nb_files_per_step: int, path: str, player_number: int, nb_players: int, must_win: bool=True):
        """
        
        Args:
            nb_files_per_step: The number of files to take into account per step
            path: The path containing the files to parse
            player_number: The number representing the player (between 0 and nb_players-1) 
            nb_players: The total number of players
            must_win: True if the player must have won to save its action sequence
        """
        super().__init__(nb_files_per_step, path)
        self._playerNumber = player_number
        self._mustWin = must_win
        self._nbPlayers = nb_players

    def _parseDataFrame(self, data_frame: pd.DataFrame) -> list:
        actions = []
        for i in range(0, data_frame.shape[0], self._nbPlayers):
            player_has_won = data_frame.loc[i+self._playerNumber][0] == 1
            players_actions_sequences = [list(data_frame.loc[i+offset][1:]) for offset in range(self._nbPlayers)]
            if not self._mustWin or player_has_won:
                sequence = []
                for k in range(data_frame.shape[1]):
                    cur_actions = []
                    is_nan = False
                    for j in range(self._nbPlayers):
                        item = players_actions_sequences[j][k]
                        if np.isnan(item):
                            is_nan = True
                            break
                        cur_actions.append(item)
                    if not is_nan:
                        sequence.append(cur_actions)
                actions.append(sequence)
        return actions



