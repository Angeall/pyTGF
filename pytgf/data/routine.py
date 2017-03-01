"""
Contains the definition of a routine to gather daata
"""
import os
import random
from typing import Iterable, Union, Callable, Optional, Tuple, List, Dict

import numpy as np
import pandas as pd

from pytgf.ai import SimultaneousAlphaBeta
from pytgf.ai.simultaneous_alphabeta import Value, EndState
from pytgf.characters.moves import MoveDescriptor
from pytgf.data.component import Data, Component
from pytgf.data.gatherer import Gatherer
from pytgf.game import API

__author__ = "Anthony Rouneau"
ObjID = int


MAX_TEMP_VECTORS = 1000
COLLECTED_DATA_PATH_NAME = "collected_data"


class Routine(SimultaneousAlphaBeta):
    def __init__(self, gatherer: Gatherer, possible_moves: Tuple[MoveDescriptor, ...],
                 eval_fct: Callable[[API], Tuple[Value, ...]], max_depth: int = -1):
        super().__init__(eval_fct, possible_moves, max_depth)
        self.TEMP_DATA_PATH_NAME = os.path.join(COLLECTED_DATA_PATH_NAME, "temp" + str(id(self)))
        self._gatherer = gatherer
        self._possibleMoves = tuple(possible_moves)
        self._aPrioriDataVectors = {}  # type: Dict[ObjID, np.ndarray]
        self._aPrioriTitles = [component.title for component in self._gatherer.aPrioriComponents]
        self._aPosterioriTitles = [component.title for component in self._gatherer.aPosterioriComponents]
        self._aPosterioriTitles.extend(["leads_to_win", "nb_turn_till_end"])
        self._nbAPosterioriComponent = len(self._gatherer.aPosterioriComponents) + 2
        self._aPrioriDescriptions = [component.description for component in self._gatherer.aPrioriComponents]
        self._aPosterioriDescriptions = [component.description for component in self._gatherer.aPosterioriComponents]
        self._aPosterioriDataVectors = {}  # type: Dict[ObjID, Dict[MoveDescriptor, List]]
        self._concludedStates = []  # type: List[ObjID]
        self._tempFileIDs = []  # type: List[str]
        self._test = {}

    def routine(self, player_number: int, state: API):
        self.alphaBetaSearching(player_number, state)
        self._writeToFinalFile()

    def _mustCutOff(self) -> bool:
        """
        Returns: False because our data gathering routine must consider all movements
        """
        return False

    def _maxValue(self, state: API, alpha: float, beta: float, depth: int) \
            -> Tuple[Value, Union[Dict[int, MoveDescriptor], None], EndState, API]:
        # STOCKING A PRIORI DATA AND INIT A POSTERIORI DATA STRUCTURE
        data = self._gatherer.getAPrioriData(state)
        self._test[id(state)] = state
        self._aPrioriDataVectors[id(state)] = data
        self._aPosterioriDataVectors[id(state)] = {action: [] for action in self._possibleMoves}
        # SEARCHING MAX VALUE
        retVal = super()._maxValue(state, alpha, beta, depth)
        # WE COMPLETE THE A POSTERIORI MOVES IF A MOVE WAS UNFEASIBLE
        for action, lst in self._aPosterioriDataVectors[id(state)].items():
            if len(lst) == 0:
                data = [np.nan for _ in range(self._nbAPosterioriComponent)]
                self._aPosterioriDataVectors[id(state)][action] = data
        # AS WE FINISHED TO SEARCH THE MAX, WE CAN MARK THIS STATE AS "CONCLUDED"
        self._concludedStates.append(id(state))
        # IF NEEDED, WE WRITE INTO A FILE THE CURRENT PROGRESSION
        if len(self._concludedStates) > MAX_TEMP_VECTORS:
            self._writeToTempFile()
        return retVal

    def _minValue(self, state: API, actions: List[Dict[int, MoveDescriptor]], alpha: float, beta: float, depth: int) \
            -> Tuple[Value, Union[Dict[int, MoveDescriptor], None], EndState, API]:
        player_move_descriptor = actions[0][self.playerNumber]
        # SEARCHING MIN VALUE
        value, best_actions, end_state, new_game_state = super()._minValue(state, actions,
                                                                           alpha, beta, depth)  # Simulate the actions
        # AS WE FINISHED SEARCHING, WE CAN STORE THE A POSTERIORI DATA
        a_posteriori_data = self._gatherer.getAPosterioriData(new_game_state)
        final_state = self._computeFinalStateScore(depth, end_state)  # Storing whether this move led to a winning state
        a_posteriori_data.extend(final_state)
        a_posteriori_dict = self._aPosterioriDataVectors[id(state)]
        a_posteriori_list = a_posteriori_dict[player_move_descriptor]
        a_posteriori_list.extend(a_posteriori_data)
        return value, best_actions, end_state, new_game_state

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
        if player_number == self.playerNumber:
            return moves
        safe_moves = []
        for move in moves:
            if not state.isMoveDeadly(player_number, move):
                safe_moves.append(move)
        if len(safe_moves) == 0:  # If all the moves are deadly
            safe_moves.append(random.choice(moves))
        return safe_moves

    def _writeToTempFile(self):
        """
        Writes the data stocked in the data structures in temporary files to save the current progress
        """
        a_priori_vectors = [self._aPrioriDataVectors[state_id] for state_id in self._concludedStates]
        if len(a_priori_vectors) > 0:
            a_posteriori_vectors_dicts = {action: [self._aPosterioriDataVectors[state_id][action]
                                                   for state_id in self._concludedStates]
                                          for action in self.possibleActions}
            a_priori_vectors = np.array(a_priori_vectors).reshape((len(a_priori_vectors), len(a_priori_vectors[0])))

            self._createDirectoryIfNeeded(COLLECTED_DATA_PATH_NAME)
            self._createDirectoryIfNeeded(self.TEMP_DATA_PATH_NAME)

            file_id = str(random.randint(0, 1000))
            self._tempFileIDs.append(file_id)
            self._writeToCsv(a_priori_vectors, self._aPrioriTitles, self._getDataFileName(file_id),
                             self.TEMP_DATA_PATH_NAME)
            for action, data_vectors in a_posteriori_vectors_dicts.items():
                data_vectors = np.array(data_vectors)
                data_vectors = data_vectors.reshape((len(data_vectors), len(data_vectors[0])))
                self._writeToCsv(data_vectors, self._aPosterioriTitles, self._getTargetFileName(file_id, action),
                                 self.TEMP_DATA_PATH_NAME)
        for state_id in self._concludedStates:
            del self._aPrioriDataVectors[state_id]
            del self._aPosterioriDataVectors[state_id]
        self._concludedStates = []

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

    def _writeToFinalFile(self):
        """
        Joins all the temporary files and the data that has not yet be written into one file
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
                os.remove(target_file_path) # The temporary file is no longer needed
            os.remove(data_file_path)  # The temporary file is no longer needed
        self._writeToCsv(a_priori, self._aPrioriTitles, self._getDataFileName(str(id(self))), COLLECTED_DATA_PATH_NAME)
        for action in a_posteriori:
            self._writeToCsv(a_posteriori[action], self._aPosterioriTitles,
                             self._getTargetFileName(str(id(self)), action), COLLECTED_DATA_PATH_NAME)

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
    def _writeToCsv(data: np.ndarray, column_titles: List[str], file_name: str, path: str):
        """
        Writes the given data into a CSV file

        Args:
            data: The data to write into a CSV file
            file_name: The name of the file that will contain the data (without extension !)
            path: The path in which the file will be written
        """
        file_name = os.path.join(path, file_name)
        addition = ""
        while True:
            try:
                file = open(file_name + addition + ".csv", "x")
                break
            except FileExistsError:
                addition += "_1"
        pd.DataFrame(data, columns=column_titles).to_csv(file, index=False)
        file.close()


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
                     title: str, description: str="",
                     reduce_function: Optional[Callable[[Tuple[Data, ...]], Data]]=None) -> None:
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
