import time

from characters.ai.simultaneous_alphabeta import SimultaneousAlphaBeta
from examples.lazerbike.control.api import GO_RIGHT, GO_DOWN, GO_UP, GO_LEFT
from examples.lazerbike.control.player import LazerBikeBotPlayer
from game.gamestate import GameState


class UndyingAI(LazerBikeBotPlayer):
    def selectMoveFollowingTeammateMessage(self, teammate_number: int, message):
        pass

    def __init__(self, player_number):
        """
        Instantiates a bot controller that choose its new move randomly for its unit.

        Args:
            player_number: The identifier of the unit controlled by this controller
        """
        super().__init__(player_number)
        self._playersMove = []
        self.alphabeta = SimultaneousAlphaBeta(self.eval_fct, (GO_RIGHT, GO_DOWN, GO_UP, GO_LEFT), max_depth=4)

    def _selectNewMove(self, game_state: GameState) -> None:
        start = time.time()
        game_state.game.copy()
        print("ONE COPY:", time.time() - start)
        action = self.alphabeta.alphaBetaSearching(self.playerNumber, game_state)
        return action

    def eval_fct(self, state: GameState):
        """
        Just give a score of 1 for a unit that is alive, and -1 for a player that is not alive

        Args:
            state:

        Returns:

        """
        scores = []
        for player_number in state.getPlayerNumbers():
            score = 1
            if not state.game.players[player_number].isAlive():
                score = -1000
            for other_player_number in state.getPlayerNumbers():
                if other_player_number != player_number:
                    if not state.belongsToSameTeam(player_number, other_player_number):
                        if not state.game.players[other_player_number].isAlive():
                            score += 1
            scores.append(score)
        return scores
