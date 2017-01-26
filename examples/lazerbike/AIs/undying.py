import time

from characters.ai.simultaneous_alphabeta import SimultaneousAlphaBeta
from controls.controllers.bot import Bot
from examples.lazerbike.control.player import LazerBikePlayer
from examples.lazerbike.rules.lazerbike import GO_RIGHT, GO_DOWN, GO_UP, GO_LEFT
from game.gamestate import GameState


class UndyingAI(LazerBikePlayer, Bot):
    def __init__(self, player_number):
        """
        Instantiates a bot controller that choose its new move randomly for its unit.

        Args:
            player_number: The identifier of the unit controlled by this controller
        """
        super().__init__(player_number)
        self.availableMoves = [self.goDown, self.goLeft, self.goRight, self.goUp]
        self._playersMove = []
        self.alphabeta = SimultaneousAlphaBeta(self.eval_fct, (GO_RIGHT, GO_DOWN, GO_UP, GO_LEFT), max_depth=3)

    def _selectNewMove(self, game_state: GameState) -> None:
        start = time.time()
        game_state.game.copy()
        print("ONE COPY:", time.time() - start)
        action = self.alphabeta.alphaBetaSearching(self.playerNumber, game_state)
        if action is GO_RIGHT:
            self.goRight()
        elif action is GO_LEFT:
            self.goLeft()
        elif action is GO_UP:
            self.goUp()
        elif action is GO_DOWN:
            self.goDown()

    def _isMoveInteresting(self, player_number: int, new_move_event) -> bool:
        self._playersMove.append(player_number)
        if len(self._playersMove) >= self.gameState.getNumberOfAlivePlayers():
            self._playersMove = []
            return True
        else:
            return False

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
