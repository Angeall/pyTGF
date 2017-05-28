from typing import List, Any, Iterable

import numpy as np
import pandas as pd

from .file_decoder import FileDecoder


class ActionSequenceDecoder(FileDecoder):
    """
    
    """

    def __init__(self, nb_files_per_step: int, path: str, player_number: int, nb_players: int, must_win: bool=True,
                 prefix: str="", verbose: bool=True):
        """
        
        Args:
            nb_files_per_step: The number of files to take into account per step
            path: The path containing the files to parse
            player_number: The number representing the player (between 0 and nb_players-1) 
            nb_players: The total number of players
            must_win: True if the player must have won to save its action sequence
            verbose: If True, the code will print when it finished parsing a file
        """
        super().__init__(nb_files_per_step, path, prefix, verbose)
        self._playerNumber = player_number
        self._mustWin = must_win
        self._nbPlayers = nb_players

    def _parseDataFrame(self, data_frame: pd.DataFrame) -> list:
        actions = []
        nb_sequences = int(data_frame.shape[0] / self._nbPlayers)
        for i in range(0, data_frame.shape[0], self._nbPlayers):
            player_has_won = data_frame.loc[i+self._playerNumber][0] == 1
            players_actions_sequences = [list(data_frame.loc[i+offset][1:]) for offset in range(self._nbPlayers)]
            if not self._mustWin or player_has_won:
                actions.append(self.getPlayersActionsSequence(players_actions_sequences))
            if self.verbose:
                print("parsing file", str(int(i/self._nbPlayers)), "/", str(nb_sequences))
        return actions

    @staticmethod
    def getPlayersActionsSequence(players_actions_sequences: Iterable) -> List[List[Any]]:
        """
        Transforms multiple lists, each containing one player's actions into a list of actions.
        e.g. transforms [[1, 2, 3], [4, 5, 6]] into [[1, 4], [2, 5], [3, 6]]
         
        Args:
            nb_players: The number of players in the sequence
            seq_length: The length of the wanted sequence 
            players_actions_sequences: 
                List containing multiple lists, each containing one player's actions into a list of actions.

        Returns: 
            A list containing List of actions performed by each player.
        """
        sequence = []
        for k in range(len(players_actions_sequences[0])):  # Sequence
            cur_actions = []
            is_nan = False
            for j in range(len(players_actions_sequences)):  # Nb of players
                item = players_actions_sequences[j][k]
                if np.isnan(item):
                    is_nan = True  # Once we reached a "NaN", the sequence is considered as finished
                    break
                cur_actions.append(item)
            if not is_nan:
                sequence.append(cur_actions)
        return sequence



