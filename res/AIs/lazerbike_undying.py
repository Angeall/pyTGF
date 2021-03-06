"""
File containing the definition of an undying AI, its goal is not to die.
"""
import random
import time
from typing import Dict

from pytgf.board.simulation import SimultaneousAlphaBeta
from pytgf.characters.moves import MoveDescriptor
from pytgf.examples.lazerbike.controllers import LazerBikeBotPlayer
from pytgf.game import API


class UndyingAI(LazerBikeBotPlayer):
    """
    Defines an AI that focus on not dying.
    """
    def __init__(self, player_number):
        """
        Instantiates a bot controller that choose its new move randomly for its unit.

        Args:
            player_number: The identifier of the unit controlled by this controller
        """
        super().__init__(player_number)
        self._playersMove = []
        self.alphabeta = SimultaneousAlphaBeta(self.eval_fct, self.possibleMoves, max_depth=3)

    def selectMoveFollowingTeammateMessage(self, teammate_number: int, message) -> None:
        """
        Does nothing special if it receives a message from a teammate

        Args:
            teammate_number: The number representing the teammate sending the message
            message: The message sent by the teammate
        """
        pass

    @staticmethod
    def eval_fct(state: API) -> Dict[int, float]:
        """
        Just give a score of 1 for a unit that is alive, and -1 for a player that is not alive

        Args:
            state:

        Returns:

        """
        scores = {}
        for player_number in state.getPlayerNumbers():
            score = 1
            if not state.game.units[player_number].isAlive():
                score = -1000
            for other_player_number in state.getPlayerNumbers():
                if other_player_number != player_number:
                    if not state.belongsToSameTeam(player_number, other_player_number):
                        if not state.game.units[other_player_number].isAlive():
                            score += 1
            score += random.random()
            scores[player_number] = score
        return scores

    def _selectNewMove(self, game_state: API) -> MoveDescriptor:
        """
        Selects a new move following a new game state

        Args:
            game_state: The new game state to react to

        Returns: a new MoveDescriptor to send to the game
        """
        start = time.time()
        game_state.game.copy()
        print("ONE COPY:", time.time() - start)
        action = self.alphabeta.alphaBetaSearching(self.playerNumber, game_state)
        return action
