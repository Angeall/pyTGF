"""
Contains the definition of a routine to gather daata
"""
import os
import random
from typing import Any
from typing import Iterable, Union, Callable, Optional, Tuple, List, Dict

import numpy as np
import pandas as pd

from .abstractroutine import AbstractRoutine
from ..component import Data, Component
from ..gatherer import Gatherer
from ...board.simulation.simultaneous_alphabeta import SimultaneousAlphaBeta, Value, EndState, _RetValue
from ...characters.moves import MoveDescriptor
from ...game import API

__author__ = "Anthony Rouneau"
ObjID = int

MAX_TEMP_VECTORS = 10000
COLLECTED_DATA_PATH_NAME = "collected_data"
ACTIONS_SEQUENCES_PATH_NAME = "actions_sequences"


class ThoroughRoutine(AbstractRoutine, SimultaneousAlphaBeta):
    def __init__(self, gatherer: Gatherer, possible_moves: Tuple[MoveDescriptor, ...],
                 eval_fct: Callable[[API], Dict[int, Value]], max_depth: int = -1, must_write_files: bool = True,
                 must_keep_temp_files: bool = False, max_end_states: int = -1):
        super().__init__(eval_fct, possible_moves, max_depth)
        self.TEMP_DATA_PATH_NAME = os.path.join(COLLECTED_DATA_PATH_NAME, "temp" + str(id(self)))
        self.fileID = 0
        self._gatherer = gatherer
        self._mustKeepTempFiles = must_keep_temp_files
        self._mustWriteFiles = must_write_files
        self._possibleMoves = tuple(possible_moves)
        self._aPrioriTitles = [component.title for component in self._gatherer.aPrioriComponents]
        self._aPosterioriTitles = [component.title for component in self._gatherer.aPosterioriComponents]
        self._aPosterioriTitles.extend(["leads_to_win", "nb_turn_till_end"])
        self._nbAPosterioriComponent = len(self._gatherer.aPosterioriComponents) + 2
        self._aPrioriDescriptions = [component.description for component in self._gatherer.aPrioriComponents]
        self._aPosterioriDescriptions = [component.description for component in self._gatherer.aPosterioriComponents]
        self._aPrioriDataVectors = {}  # type: Dict[ObjID, np.ndarray]
        self._aPosterioriDataVectors = {}  # type: Dict[ObjID, Dict[MoveDescriptor, List]]
        self._concludedStates = {}  # type: Dict[ObjID, Any]
        self._tempFileIDs = []  # type: List[str]
        self._actionsSequences = pd.DataFrame()  # type: pd.DataFrame
        self._nbStates = 0
        self._totalNbStates = 0
        self._writtenFiles = 0
        self._maxEndStates = max_end_states
        if max_end_states == -1:
            self._maxEndStates = float('inf')

    def _resetValues(self):
        self._aPrioriDataVectors = {}  # type: Dict[ObjID, np.ndarray]
        self._aPosterioriDataVectors = {}  # type: Dict[ObjID, Dict[MoveDescriptor, List]]
        self._concludedStates = {}  # type: Dict[ObjID, Any]
        self._tempFileIDs = []  # type: List[str]
        self._nbStates = 0
        self._totalNbStates = 0
        self._writtenFiles = 0

    def routine(self, player_number: int, state: API) -> Tuple[pd.DataFrame, Dict[MoveDescriptor, pd.DataFrame]]:
        """
        Launches the data gathering routine and saves into file(s) the results

        Args:
            player_number: The number of the play er for which the data is gathered
            state: The initial state from which the data will be gathered

        Returns:
            The DataFrames containing the gathered data as a tuple
                (A Priori Data, A Posteriori data indexed by actions)
        """

        self.alphaBetaSearching(player_number, state)
        return self._writeToFinalFile()

    def alphaBetaSearching(self, player_number: int, state: API):
        res = super().alphaBetaSearching(player_number, state)
        self._nbStates = 0
        return res

    @staticmethod
    def updateTargetVectors(current_target: np.ndarray, new_target: np.ndarray) -> np.ndarray:
        """
        Compares two target vectors and returns the one to keep from the two.
        Pessimistic comparison => keeps the least advantageous vector

        Args:
            current_target: The first vector to compare
            new_target: The second vector to compare

        Returns: The vector to keep between the two given vectors
        """
        assert len(current_target.shape) == 0 and len(new_target.shape) == 0  # We can only compare flat vectors
        current_has_won, current_nb_turns = current_target[-2:]
        new_has_won, new_nb_turns = new_target[-2:]  # type: Tuple[float, float]
        if new_has_won < current_has_won:  # pessimistic
            return new_target
        if current_has_won < new_has_won:  # pessimistic
            return current_target
        else:  # If winning, the pessimistic option is the maximum number of turn 'til we win.
            # Else, it is the minimum number of turn till we lose.
            return new_target if new_nb_turns > current_nb_turns else current_target

    @property
    def _mustCutOff(self) -> bool:
        """
        Returns: False because our data gathering routine must consider all movements
        """
        return False

    def _maxValue(self, state: API, alpha: float, beta: float, depth: int) \
            -> _RetValue:
        finished = state.isFinished()

        # STOCKING A PRIORI DATA AND INIT A POSTERIORI DATA STRUCTURE
        if self._nbStates >= self._maxEndStates:  # We reached the limit
            return self._getTeamScore(state, self.eval(state)), None, \
                   (state.isFinished(), depth, state.hasWon(self.playerNumber)), None, False
        if not finished:
            while state.id in self._concludedStates or state.id in self._aPrioriDataVectors:
                state.id += 1
            data = self._gatherer.getAPrioriData(state)
            self._aPrioriDataVectors[state.id] = data
            self._aPosterioriDataVectors[state.id] = {action: [] for action in self._possibleMoves}
            data = None
        else:
            self._registerActionsSequence(state)
            self._nbStates += 1
            self._totalNbStates += 1
        # SEARCHING MAX VALUE
        ret_val = super()._maxValue(state, alpha, beta, depth)
        id_state = state.id
        state = []
        del state

        # WE COMPLETE THE A POSTERIORI MOVES IF A MOVE WAS UNFEASIBLE
        if not finished:
            for action, lst in self._aPosterioriDataVectors[id_state].items():
                if len(lst) == 0:
                    data = [np.nan for _ in range(self._nbAPosterioriComponent)]
                    self._aPosterioriDataVectors[id_state][action] = data
            data = None
            # AS WE FINISHED TO SEARCH THE MAX, WE CAN MARK THIS STATE AS "CONCLUDED"
            self._concludedStates[id_state] = True
            # IF NEEDED, WE WRITE INTO A FILE THE CURRENT PROGRESSION
            if len(self._concludedStates) > MAX_TEMP_VECTORS:
                self._writeToTempFile()
        return ret_val

    def _registerActionsSequence(self, state):
        actions_histories = state.getAllActionsHistories()
        has_won = np.ndarray((0, 1))
        for pl_num in state.getPlayerNumbers():
            won = 0
            if state.hasWon(pl_num):
                won = 1
            has_won = np.vstack((has_won, won))
        actions_histories = np.hstack((has_won, actions_histories))
        self._actionsSequences = self._actionsSequences.append(pd.DataFrame(actions_histories), ignore_index=True)

    def _minValue(self, state: API, actions: List[Dict[int, MoveDescriptor]], alpha: float, beta: float, depth: int) \
            -> _RetValue:
        player_move_descriptor = actions[0][self.playerNumber]
        new_actions = np.zeros((len(self._playerMapping), 1))
        new_actions -= 1

        # SEARCHING MIN VALUE
        value, best_actions, end_state, new_game_state, best_reached_end = super()._minValue(state, actions,
                                                                                             alpha, beta,
                                                                                             depth)  # Simulate actions

        id_state = state.id
        state = []
        del state

        # AS WE FINISHED SEARCHING, WE CAN STORE THE A POSTERIORI DATA
        final_state = self._computeFinalStateScore(depth, end_state)  # Storing whether this move led to a winning state
        a_posteriori_data = self._gatherer.getAPosterioriData(new_game_state)
        a_posteriori_data.extend(final_state)
        self._aPosterioriDataVectors[id_state][player_move_descriptor].extend(a_posteriori_data)
        return value, best_actions, end_state, new_game_state, best_reached_end

    @staticmethod
    def _computeFinalStateScore(depth: int, end_state: EndState) -> Tuple[int, int]:
        final_state = (0, 0)  # We suppose that the game has not ended
        if end_state[0]:
            nb_turn = end_state[1] - depth  # The number of turn in which the game ended
            if not end_state[2]:  # If the game ended but the player lost
                final_state = (-1, nb_turn)
            else:
                final_state = (1, nb_turn)
        return final_state

    def _getPossibleMovesForPlayer(self, player_number: int, state: API) -> List[MoveDescriptor]:
        moves = super()._getPossibleMovesForPlayer(player_number, state)
        if self.turnByTurn or player_number == self.playerNumber:
            return moves
        safe_moves = []
        for move in moves:
            deadly = state.isMoveSuicidal(player_number, move)
            if not deadly:
                safe_moves.append(move)
        if len(safe_moves) == 0:  # If all the moves are deadly
            safe_moves.append(random.choice(moves))  #
        return safe_moves

    def _generateMovesList(self, state: API):
        combinations = super()._generateMovesList(state)
        if not self.turnByTurn:
            return combinations
        safe_moves = []
        winning_moves = {}
        for moves in combinations:
            suicidal, winning = state.areMovesSuicidalOrWinning(moves)
            if not np.array(list(suicidal.values())).any():
                safe_moves.append(moves)
                for player_number, player_won in winning.items():
                    if player_won:
                        if player_number not in winning_moves:
                            winning_moves[player_number] = []
                        winning_moves[player_number].append(moves)
        if len(winning_moves) > 0:
            safe_moves = self._filterNonWinningSimilarMoves(state, winning_moves, safe_moves)
        # if len(safe_moves) == 0:

        return safe_moves

    @staticmethod
    def _filterNonWinningSimilarMoves(state: API, winning_moves: Dict[int, List[Dict[int, MoveDescriptor]]],
                                      other_moves: List[Dict[int, MoveDescriptor]]) -> List[Dict[int, MoveDescriptor]]:
        to_remove = []
        other_sequences = state.convertIntoMoveSequence(other_moves)
        for winning_player_number, moves in winning_moves.items():
            order_of_player = state.getOrderOfPlayer(winning_player_number)
            winning_sequences = {}
            sequences = state.convertIntoMoveSequence(moves)
            for winning_move in sequences:
                pre_seq = tuple(winning_move[:order_of_player])
                if pre_seq not in winning_sequences:
                    winning_sequences[pre_seq] = []
                winning_sequences[pre_seq].append(winning_move[order_of_player])
            avoid_doubles = {key: None for key in winning_sequences}
            for i, other_sequence in enumerate(other_sequences):
                pre_seq = tuple(other_sequence[:order_of_player])
                if pre_seq in winning_sequences:
                    if other_sequence[order_of_player] not in winning_sequences[pre_seq]:
                        to_remove.append(other_moves[i])
                    else:
                        if avoid_doubles[pre_seq] is None:
                            avoid_doubles[pre_seq] = other_moves[i]
                        else:
                            to_remove.append(other_moves[i])
        to_keep = []
        for move in other_moves:
            if move not in to_remove:
                to_keep.append(move)
        return to_keep

    def _writeToTempFile(self):
        """
        Writes the data stocked in the data structures in temporary files to save the current progress
        """
        self._writtenFiles += MAX_TEMP_VECTORS
        print(self._writtenFiles)
        a_priori_vectors = [self._aPrioriDataVectors[state_id] for state_id in self._concludedStates
                            if state_id in self._aPosterioriDataVectors]

        if len(a_priori_vectors) > 0:
            a_posteriori_vectors_dicts = {action: [self._aPosterioriDataVectors[state_id][action]
                                                   for state_id in self._concludedStates]
                                          for action in self.possibleActions}
            a_priori_vectors = np.array(a_priori_vectors).reshape((len(a_priori_vectors), len(a_priori_vectors[0])))

            self._createDirectoryIfNeeded(COLLECTED_DATA_PATH_NAME)
            self._createDirectoryIfNeeded(self.TEMP_DATA_PATH_NAME)

            file_id = str(self.fileID)
            self._tempFileIDs.append(file_id)
            self._writeToCsv(a_priori_vectors, self._getDataFileName(file_id),
                             self.TEMP_DATA_PATH_NAME, self._aPrioriTitles)
            data_vectors = None
            for action, data_vectors in a_posteriori_vectors_dicts.items():
                data_vectors = np.array(data_vectors)
                data_vectors = data_vectors.reshape((len(data_vectors), len(data_vectors[0])))
                self._writeToCsv(data_vectors, self._getTargetFileName(file_id, action),
                                 self.TEMP_DATA_PATH_NAME, self._aPosterioriTitles)

            self._createDirectoryIfNeeded(ACTIONS_SEQUENCES_PATH_NAME)
            if self._mustWriteFiles:
                self._writeToCsv(self._actionsSequences, "seq" + file_id,
                                 ACTIONS_SEQUENCES_PATH_NAME)
                self._actionsSequences = pd.DataFrame()
            self.fileID += 1

            del a_priori_vectors
            del a_posteriori_vectors_dicts
            del data_vectors
        for state_id in self._concludedStates:
            del self._aPrioriDataVectors[state_id]
            del self._aPosterioriDataVectors[state_id]
        self._concludedStates = {}

    @staticmethod
    def _getDataFileName(file_id: str) -> str:
        """
        Get the name of the data file linked to the given ID

        Args:
            file_id: The ID of the file for which the name will be given

        Returns: The file name of the data file linked to the given ID
        """
        return "data" + file_id

    @staticmethod
    def _getTargetFileName(file_id: str, move_descriptor: MoveDescriptor):
        """
        Get the name of the target file linked with the given ID

        Args:
            file_id: The ID of the file for which the name will be given
            move_descriptor: The move descriptor that was used to create the target file

        Returns: The file name of the target file linked to the given ID
        """
        return "target(" + str(move_descriptor) + ")" + file_id

    def _writeToFinalFile(self) -> Tuple[pd.DataFrame, Dict[MoveDescriptor, pd.DataFrame]]:
        """
        Joins all the temporary files and the data that has not yet be written into one file

        Returns:
            The DataFrames containing the data of all temp files as a tuple
                (A Priori Data, A Posteriori data indexed by actions)

        """
        self._writeToTempFile()  # WRITES WHAT HAS NOT ALREADY BEEN WRITTEN
        a_priori = None
        a_posteriori = {}
        for file_id in self._tempFileIDs:
            data_file_name = self._getDataFileName(file_id)
            data_file_path = os.path.join(self.TEMP_DATA_PATH_NAME, data_file_name + ".csv")
            data = pd.read_csv(data_file_path)
            if a_priori is None:
                a_priori = data
            else:
                a_priori = a_priori.append(data, ignore_index=True)

            for action in self._possibleMoves:
                target_file_name = self._getTargetFileName(file_id, action)
                target_file_path = os.path.join(self.TEMP_DATA_PATH_NAME, target_file_name + ".csv")
                target_data = pd.read_csv(target_file_path)
                if action not in a_posteriori:
                    a_posteriori[action] = target_data
                else:
                    a_posteriori[action] = a_posteriori[action].append(target_data, ignore_index=True)
                self._removeTempFileIfNeeded(target_file_path)  # The temporary file is no longer needed
            self._removeTempFileIfNeeded(data_file_path)  # The temporary file is no longer needed
        if self._mustWriteFiles:
            self._writeToCsv(a_priori, self._getDataFileName(str(id(self))), COLLECTED_DATA_PATH_NAME,
                             self._aPrioriTitles)
            for action in a_posteriori:
                self._writeToCsv(a_posteriori[action], self._getTargetFileName(str(id(self)), action),
                                 COLLECTED_DATA_PATH_NAME, self._aPosterioriTitles)
        self._removeTempFileIfNeeded(self.TEMP_DATA_PATH_NAME, is_folder=True)
        return a_priori, a_posteriori

    @staticmethod
    def _createDirectoryIfNeeded(path_name: str):
        """
        Creates a directory if it doesn't exist.

        Args:
            path_name: The path of the directory to create
        """
        try:
            path = os.path.join(os.path.curdir, path_name)
            os.mkdir(path)
        except FileExistsError:
            pass

    @staticmethod
    def _writeToCsv(data: Union[np.ndarray, pd.DataFrame], file_name: str, path: str, column_titles: List[str] = None):
        """
        Writes the given data into a CSV file

        Args:
            data: The data to write into a CSV file
            file_name: The name of the file that will contain the data (without extension !)
            path: The path in which the file will be written
        """
        file_name = os.path.join(path, file_name)
        addition = ""
        file = None
        finished = False
        while not finished:
            try:
                file = open(file_name + addition + ".csv", "a")
                if column_titles is not None:
                    pd.DataFrame(data, columns=column_titles).to_csv(file, index=False)
                else:
                    pd.DataFrame(data).to_csv(file, index=False)
                finished = True
            except FileExistsError:
                addition += "1"
            finally:
                if file is not None:
                    file.close()

    def _removeTempFileIfNeeded(self, file_path: str, is_folder: bool = False):
        if self._mustWriteFiles and not self._mustKeepTempFiles:
            if not is_folder:
                os.remove(file_path)
            else:
                os.rmdir(file_path)


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
                     title: str, description: str = "",
                     reduce_function: Optional[Callable[[Tuple[Data, ...]], Data]] = None) -> None:
        """
        Adds a component to the routine being built

        Args:
            methods: An iterable of methods or just one method that takes an API as a parameter and returns a data
            title: The title to give to this component
            description: A short description of this component
            reduce_function:
                A method that, given a tuple of data, returns a single data (e.g. functools.reduce)
                Unused if the "methods" parameter is a lone method, but necessary if there is more than one method.
        """
        self._components.append(Component(methods, title, description, reduce_function))

    def create(self, possible_moves: Tuple[MoveDescriptor, ...],
               eval_fct: Callable[[API], Tuple[Union[int, float], ...]]) -> ThoroughRoutine:
        """
        Raises:
            ValueError: If no component was added to this builder, it cannot create a routine, and hence crash

        Returns: The Routine built using this builder
        """
        if len(self._components) == 0:
            raise ValueError("Cannot create a routine with 0 component")
        gatherer = Gatherer(self._components)
        return ThoroughRoutine(gatherer, possible_moves, eval_fct)
