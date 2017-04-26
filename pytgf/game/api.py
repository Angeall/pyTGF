"""
File containing the definition of a basic API to interact with a game from a controller
"""
import copy
from abc import ABCMeta, abstractmethod
from typing import Tuple, Dict, Union, List

import pandas as pd

from .core import Core, UnfeasibleMoveException
from ..board import TileIdentifier
from ..characters.moves import IllegalMove, MoveDescriptor, Path
from ..characters.units import Unit

__author__ = 'Anthony Rouneau'


class DeadPlayerException(Exception):
    pass


class NoMovementException(Exception):
    pass


class API(metaclass=ABCMeta):
    """
    A class defining a basic API so a controller can get information on the current state of the game,
    and simulate new moves in it.
    """

    def __init__(self, game: Core):
        """
        Instantiates the API

        Args:
            game: The game that will be used in this API
        """
        self.game = game
        self.id = id(self)
        self._actionsHistory = {pl_num: [] for pl_num in self.getPlayerNumbers()}

    # -------------------- PUBLIC METHODS -------------------- #

    def simulateMove(self, player_number: int, wanted_move: MoveDescriptor, force: bool=False) \
            -> Tuple[bool, Union['API', None]]:
        """
        Simulates the move by creating a new GameState

        Args:
            force: Force the move, even if the game is turn-based and it is not the turn of the given player
            player_number: The number of the player moving
            wanted_move: The event triggering the move

        Returns:
            A copy of this GameState in which the move have been applied (if it is possible)
        """
        new_game_state = self.copy()
        feasible_move = new_game_state.performMove(player_number, wanted_move, force=force)
        return feasible_move, new_game_state if feasible_move else None

    def simulateMoves(self, player_moves: Dict[int, MoveDescriptor]) -> Tuple[bool, Union['API', None]]:
        """
        Simulates the given moves for the key players

        Args:
            player_moves: a dictionary with player_number as key and a move as value for the key player

        Returns:
            - A boolean -- True if all the moves succeeded, False otherwise
            - A copy of this GameState in which the moves have been applied (if a move is unfeasible, returns None).
        """
        moves = []
        for pl_num in self.game.playerNumbers:
            if pl_num in player_moves:
                moves.append((pl_num, player_moves[pl_num]))
        new_game_state = self.copy()
        for player_number, wanted_move in moves:
            feasible_move = new_game_state.performMove(player_number, wanted_move)

            if not feasible_move:
                return False, None
        if self._mustCheckIfFinishedAfterSimulations():
            new_game_state.game.checkIfFinished()
        return True, new_game_state

    def performMove(self, player_number: int, move_descriptor: MoveDescriptor, force: bool = False) -> bool:
        """
        Performs the move inside this GameState

        Args:
            player_number: The number of the player moving
            move_descriptor: The move to perform (either a Path or a move descriptor)
            force: Boolean that indicates if the move must be forced into the game (is optional in the game def...)
        """
        if self.game.isFinished():
            return True
        unit = self.game.getUnitForNumber(player_number)  # type: Unit
        try:
            move = self.createMoveForDescriptor(unit, move_descriptor, force=force, is_step=True)
            new_tile_id = move.complete()
            unit.currentAction = move_descriptor
            self._addActionToHistory(move_descriptor, player_number)
            self.game.updateGameState(move.unit, new_tile_id, move_descriptor)
            self._reactToMovePerformed(player_number, move)

        except UnfeasibleMoveException:
            return False
        except IllegalMove:
            self._addActionToHistory(move_descriptor, player_number)
            unit.kill()
        return True

    def _addActionToHistory(self, move_descriptor, player_number):
        if player_number not in self._actionsHistory:
            self._actionsHistory[player_number] = []
        encoded_move = self.encodeMove(player_number, move_descriptor)
        self._actionsHistory[player_number].append(encoded_move)

    def getActionsHistory(self, player_number: int) -> List[MoveDescriptor]:
        """
        Args:
            player_number: The number representing the player for which we want the actions history 

        Returns: The history of the given player
        """
        if player_number not in self._actionsHistory:
            return []
        return self._actionsHistory[player_number]

    def getAllActionsHistories(self) -> pd.DataFrame:
        """
        Returns: The history of all players, in vertical order (if there is an order between players)
        """
        df = pd.DataFrame()
        for player_number in self.game.playerNumbers:
            df = df.append([self.getActionsHistory(player_number)], ignore_index=True)
        return df

    def belongsToSameTeam(self, player_1_number: int, player_2_number: int) -> bool:
        """
        Checks if two players are in the same team

        Args:
            player_1_number: The number representing the first player to check
            player_2_number: The number representing the second player to check

        Returns: True if the two players belongs to the same team, False otherwise.
        """
        return self.game.belongsToSameTeam(self.game.units[player_1_number], self.game.units[player_2_number])

    def getPlayerNumbers(self):
        """
        Returns: The list of the number of each player, sorted !
        """
        players = list(self.game.avatars.keys())
        players.sort()
        return players

    def getNumberOfTeams(self) -> int:
        """
        Returns: The number of teams playing the game
        """
        return len(self.game.teams)

    def getAlivePlayersNumbers(self) -> List[int]:
        """
        Returns: The numbers representing the alive players in the game
        """
        alive_players = []
        for player_number in self.game.playerNumbers:
            unit = self.game.getUnitForNumber(player_number)
            if unit.isAlive():
                alive_players.append(player_number)
        return alive_players

    def checkFeasibleMoves(self, player_number: int, possible_moves: Tuple[MoveDescriptor, ...]) -> \
            List[MoveDescriptor]:
        """
        Keeps only the feasible moves in the given list of possible moves

        Args:
            player_number: The number of the player that wants to know its possible moves
            possible_moves: The total list of possible moves, that will be filtered to keep only the feasible ones

        Returns: The list of all the feasible moves among the possible ones
        """
        if not self.isPlayerAlive(player_number):  # If the unit is dead, no move is feasible for it
            return []
        feasible_moves = []
        for move in possible_moves:
            if self._generateMove(player_number, move)[0]:
                feasible_moves.append(move)

        return feasible_moves

    def isFinished(self) -> bool:
        """
        Returns: True if the game is in a final state
        """
        finished = self.game.checkIfFinished()
        return self.game.isFinished()

    def isPlayerAlive(self, player_number: int) -> bool:
        """

        Args:
            player_number: The number of the player for which we want to know the state.

        Returns: True if the player is alive, False otherwise
        """
        return self.game.units[player_number].isAlive()

    def hasWon(self, player_number: int) -> bool:
        """

        Args:
            player_number: The number representing the player.

        Returns: True if the player represented by the given number has won.
        """
        unit = self.game.getUnitForNumber(player_number)
        return self.isFinished() and unit in self.game.winningPlayers

    def getPlayerLocation(self, player_number: int) -> TileIdentifier:
        """

        Args:
            player_number: The number of the player for which we want to know the state.

        Returns: The (i, j) coordinates of the player, i being the row index and j being the column index.
        """
        return self.game.unitsLocation[self.game.units[player_number]]

    def getAdjacent(self, tile_id: TileIdentifier) -> Tuple[TileIdentifier, ...]:
        """

        Args:
            tile_id:
                The (i, j) coordinates of the tile for which we want the adjacent tiles,
                i being the row index and j being the column index.

        Returns: A tuple containing each identifier of the tiles adjacent to the tile for which the id was given
        """
        return self.game.board.getNeighboursIdentifier(tile_id)

    def areMovesSuicidalOrWinning(self, move_descriptors: Dict[int, MoveDescriptor]) \
            -> Tuple[Dict[int, bool], Dict[int, bool]]:
        """

        Args:
            move_descriptors: The descriptors of the moves to perform along with the number of the player performing it

        Returns: 
            A couple of dict, the first linking player numbers to a boolean indicating if the move is a suicidal move 
             for that player, and the second linking player number to a boolean indicating if the move makes that
             player win the game.
        """
        suicidal = {}
        winning = {}
        api = self.copy()
        for player_number in self.game.playerNumbers:
            player_deadly = False
            player_winning = False
            had_won = api.hasWon(player_number)
            if api.isPlayerAlive(player_number):
                succeeded, new_api = api.simulateMove(player_number, move_descriptors[player_number], force=True)
                if succeeded:
                    api = new_api
                    player_deadly = not api.isPlayerAlive(player_number)
                    player_winning = not had_won and api.hasWon(player_number)
                else:
                    player_deadly = True
            suicidal[player_number] = player_deadly
            winning[player_number] = player_winning
        return suicidal, winning

    def isMoveSuicidalOrWinning(self, player_number: int, move_descriptor: MoveDescriptor) \
            -> Tuple[bool, bool]:
        """
        
        Args:
            player_number: The player that will perform the move
            move_descriptor: The descriptor of the move to perform

        Returns: A couple of booleans containing: (is_move_suicidal, is_move_winning)
        """
        if self.isPlayerAlive(player_number):
            succeeded, new_api = self.simulateMove(player_number, move_descriptor, force=True)
            if succeeded:
                return not new_api.isPlayerAlive(player_number), new_api.hasWon(player_number)
        return False, False

    def isMoveSuicidal(self, player_number: int, move_descriptor: MoveDescriptor) -> bool:
        """

        Args:
            player_number: The player that will perform the move
            move_descriptor: The descriptor of the move to perform

        Returns: True if the move kills the unit in the simulation
        """
        return self.isMoveSuicidalOrWinning(player_number, move_descriptor)[0]

    def isMoveWinning(self, player_number: int, move_descriptor: MoveDescriptor) -> bool:
        """

        Args:
            player_number: The player that will perform the move
            move_descriptor: The descriptor of the move to perform

        Returns: True if the move makes the given player win the game
        """
        return self.isMoveSuicidalOrWinning(player_number, move_descriptor)[1]

    def getTileByteCode(self, tile_id: tuple) -> int:
        """
        Get the byte code of a tile

        Args:
            tile_id: The row and column-index of the tile (e.g. (x, y))

        Returns:
            The code representing the tile (i, j) in the board

                - 0 = walkable non-deadly
                - 1 = walkable deadly
                - 2 = non-walkable, non-deadly
                - 3 = non-walkable, deadly
        """
        i, j = tile_id
        tile = self.game.board.getTileById((i, j))
        byte_code = 0
        if tile.deadly:
            byte_code += 1
        if not tile.walkable:
            byte_code += 2
        return byte_code

    def copy(self):
        new_api = type(self)(self.game.copy())
        new_api._actionsHistory = copy.deepcopy(self._actionsHistory)
        return new_api

    def encodeMove(self, player_number: int, move_descriptor: MoveDescriptor) -> int:
        """
        Encode a move to be performed (hence, this API must be in a state where the move represented by the descriptor
        has not yet been performed !)

        Args:
            player_number: The number representing the player that could perform the move
            move_descriptor: The descriptor of the move to be performed by the given player

        Returns:
            -1 if the player hasn't played yet, -2 if the player is dead,
            or a positive integer that represents the given move descriptor
        """
        # if not self.isPlayerAlive(player_number):
        #     return -2
        if self.game.getUnitForNumber(player_number).lastAction is None:
            return -1000
        return self._encodeMoveIntoPositiveNumber(player_number, move_descriptor)

    def decodeMove(self, player_number: int, encoded_move: int) -> MoveDescriptor:
        """
        Decode the given encoded move into a correct move descriptor.

        Args:
            player_number: The number representing the player that could perform the move.
            encoded_move: The integer representing an encoded move (to be decoded..)

        Returns:
            The decoded move, hence a correct move descriptor for the given player
            (does not check if the move is feasible).

        Raises:
            DeadPlayerException:
                If the encoded move is -2, it means that the player was dead when trying to encode the move.
            NoMoveException:
                If the encoded move is -1, it means that the player had't played yet when encoding the last move
        """
        if encoded_move == -2000:
            raise DeadPlayerException()
        if encoded_move == -1000:
            raise NoMovementException()
        return self._decodeMoveFromPositiveNumber(player_number, encoded_move)

    def getBoardByteCodes(self):
        """
        Returns: A tab containing the byte code of each tile of the board
        """
        tab = []
        for i in range(self.game.board.lines):
            tab_line = []
            for j in range(self.game.board.columns):
                tab_line.append(self.getTileByteCode((i, j)))
            tab.append(tab_line)
        return tab

    def convertIntoMoveSequence(self, move_combination: Union[Dict[int, MoveDescriptor],
                                                              List[Dict[int, MoveDescriptor]]]
                                ) -> List[MoveDescriptor]:
        """
        Convert a move combination into a move sequence

        Args:
            move_combination: The moves that are performed by the players

        Returns: A sequence of moves
        """
        if isinstance(move_combination, dict):
            return [move_combination[player_number] for player_number in self.game.playerNumbers
                    if self.isPlayerAlive(player_number) and player_number in move_combination]
        if isinstance(move_combination, list):
            sequences = []
            for move in move_combination:
                sequences.append(self.convertIntoMoveSequence(move))
            return sequences

    def getOrderOfPlayer(self, player_number: int) -> int:
        """
        Gets the index of the given player in the list of the alive players

        Args:<
            player_number: The number representing the player 

        Returns: The number of order amongst all alive players
        
        Raises: 
            ValueError: if the given player is dead or not in the list of alive players.
        """
        return self.getAlivePlayersNumbers().index(player_number)

    @abstractmethod
    def createMoveForDescriptor(self, unit: Unit, move_descriptor: MoveDescriptor, force: bool = False,
                                is_step: bool=False) -> Path:
        """
        Creates a move following the given event coming from the given unit

        Args:
            unit: The unit that triggered the event
            move_descriptor: The descriptor of the move triggered by the given unit
            force: Optional, a bot controller will force the move as it does not need to check if the move is possible
            is_step: 
                Optional, True indicates that the move will serve to perform a step in an API.
                It can be ignored if the moves do not differ from a step or from a complete move

        Returns: A Path of move(s) triggered by the given event for the given unit

        Raises:
            UnfeasibleMoveException: If the move is not possible.
        """
        pass

    # -------------------- PROTECTED METHODS -------------------- #

    def _generateMove(self, player_number: int, wanted_move: MoveDescriptor) -> Tuple[bool, Union[Path, None]]:
        """
        Generates a move for a given event

        Args:
            player_number: The player that must perform the move
            wanted_move: The descriptor of the move to perform

        Returns:
            A tuple containing

             - A bool set to True if the move was successfully created, set to False otherwise
             - The Path created from the given move descriptor, or None if the move was not successfully created

        """
        unit = self.game.units[player_number]
        try:
            move = self.createMoveForDescriptor(unit, wanted_move, is_step=True)
            return True, move
        except UnfeasibleMoveException:
            return False, None

    @abstractmethod
    def _decodeMoveFromPositiveNumber(self, player_number: int, encoded_move: int) -> MoveDescriptor:
        """
        Decode the given encoded move into a correct move descriptor.

        Args:
            player_number: The number representing the player that could perform the move.
            encoded_move: The positive integer representing an encoded move (to be decoded..)

        Returns:
            The decoded move, hence a correct move descriptor for the given player
            (does not check if the move is feasible).
        """
        pass

    @abstractmethod
    def _encodeMoveIntoPositiveNumber(self, player_number: int, move_descriptor: MoveDescriptor) -> int:
        """
        Encode a move to be performed (hence, this API must be in a state where the move represented by the descriptor
        has not yet been performed !)

        Args:
            player_number: The number representing the player that could perform the move
            move_descriptor: The descriptor of the move to be performed by the given player

        Returns: A positive integer that represents the move descriptor
        """
        pass

    def _mustCheckIfFinishedAfterSimulations(self) -> bool:
        return True

    def _reactToMovePerformed(self, player_number: int, move: Path):
        pass
