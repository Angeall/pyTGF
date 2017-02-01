import itertools
import random
import time
import traceback

from pytgf.game import GameState

__author__ = 'Anthony Rouneau'

direction_str = ["RIGHT", "UP", "LEFT", "DOWN"]


class SimultaneousAlphaBeta:
    # TODO: generate combinations of moves... Tried itertools.product with functools.reduce
    """
    Implementation of a cutoff AlphaBeta algorithm that performs the moves of all the players simultaneously
    """
    def __init__(self, eval_fct, possible_actions: tuple, max_depth=6):
        """

        Args:
            eval_fct:
                objective function that computes a score tuple given a state.
                The evaluation function must take a GameState parameter as first parameter.
                It must return a tuple, giving the current score of each player for the given state.
                Example:
                    - (2, 5, 0, 1000) indicates that the state suits very well for the fourth player.
                    - (1, 1, 1, 1) indicates that the state suits equally to all the players.
                This tuple will then be reworked into team scores.
            possible_actions: The tuple of possible actions accepted in the game for all players
            max_depth: the maximum depth of the tree the algorithm can explore
        """
        self.eval = eval_fct
        self.max_depth = max_depth
        self.random = random.Random()
        self.possibleActions = possible_actions
        self.actions = {}  # Will retain the best action for a given state (will speed up the tree search)
        self.playerNumber = -1
        self.copyTime = 0

    def alphaBetaSearching(self, player_number: int, state: GameState):
        """
        :param player_number: The number of the player for which an action must be found
        :param state: The current state of the game (including the current player)
        :type state: GameState
        :return: the best action among the possible ones
        """
        try:
            self.playerNumber = player_number
            a = time.time()

            if self.actions.get(state) is not None:
                value, actions = self.actions[state]
            else:

                value, actions, _ = self.maxValue(state, -float('inf'), float('inf'), 0)
            print("GLOBAL", time.time() - a, "s")
            self.playerNumber = None
            if actions is not None:
                return actions[player_number]
            else:
                return self._randomChoice(self.possibleActions)
        except:
            traceback.print_exc()

    def maxValue(self, state: GameState, alpha: float, beta: float, depth: int):
        """
        :param state: the state of the current node
        :type state: GameState
        :param alpha: The alpha bound that allows to cutoff some branches
        :param beta: The beta bound that allows to cutoff some branches
        :param depth: the current depth in the tree
        :return: the best value and the best action among its children or
                 the value of the terminal state
                 True if the action has reached a end state

        Computes the best step possible for the "MAX" Player
        """
        # Check if we reached the end of the tree
        if depth > self.max_depth:
            score = self._getTeamScore(state, self.eval(state))
            return score, None, False
        # Check if the game state is final
        elif state.isFinished():
            return self._getTeamScore(state, self.eval(state)), None, True

        # Initializing the best values
        max_value = -float('inf')
        best_reached_end = False
        equally_good_choices = []

        # Explore every possible actions from this point
        actions_combinations = self._generateMovesCombinations(state)
        actions_combinations_scores = {}
        for actions in actions_combinations:  # type: tuple
            min_value, min_actions, min_reached_end = self.minValue(state, actions, alpha, beta, depth)
            actions_combinations_scores[min_value] = min_actions, min_reached_end
            if min_value >= beta:
                return min_value, min_actions, min_reached_end
            alpha = max(alpha, min_value)  # Confirmed
        for score in actions_combinations_scores:
            combination, reached_end = actions_combinations_scores[score]
            if score > max_value:
                max_value = score
                equally_good_choices = [combination]
                best_reached_end = reached_end
            elif score == max_value:
                equally_good_choices.append(combination)
        if len(equally_good_choices) == 0:  # No choice is good to take...
            return self._getTeamScore(state, self.eval(state)), None, True
        best_combination = self._randomChoice(equally_good_choices)

        return max_value, best_combination, best_reached_end

    def minValue(self, state, actions, alpha, beta, depth):
        min_reached_end = False
        min_value = float('inf')
        equal_min_choices = []
        for combination in actions:  # type: dict
            feasible_moves, new_game_state = state.simulateMoves(combination)
            if feasible_moves and new_game_state is not None:
                value, _, reached_end = self.maxValue(new_game_state, alpha, beta, depth + 1)
                if value < min_value:
                    min_value = value
                    equal_min_choices = [combination]
                    min_reached_end = reached_end
                elif value == min_value:
                    equal_min_choices.append(combination)
                if value <= alpha:  # Cutoff because we are in a min situation
                    return value, self._randomChoice(equal_min_choices), min_reached_end
                beta = min(beta, value)
        min_actions = self._randomChoice(equal_min_choices)
        return min_value, min_actions, min_reached_end

    def _getTeamScore(self, state: GameState, players_score: tuple) -> float:
        """
        Given a tuple of players individual score for the given state, computes the score for the team of the player
        for which this alpha beta is running.

        Args:
            state: the state for which the given score has been computed
            players_score: The tuple of score, computed by the evaluation function

        Returns: The score of the team of the player of this AlphaBeta
        """
        own_team_score = 0
        player_numbers = state.getPlayerNumbers()
        for player_index, player_score in enumerate(players_score):
            player_number = player_numbers[player_index]
            if player_number == self.playerNumber or state.belongsToSameTeam(player_number, self.playerNumber):
                own_team_score += player_score
        return own_team_score

    def _generateMovesCombinations(self, state: GameState) -> list:
        """
        Generates al the possible combinations of movements for the given state

        Args:
            state: The state for which the movements will be evaluated

        Returns:
            A list of tuples of dictionaries
            (e.g. {1: 2, 2: 3} indicates that the player 1 chose the action "2" and the player 2 chose the action "3")
            The list contains tuple, containing all the dictionaries containing the same actions for the player
            concerned in this alpha beta. (e.g. [({1: 2, 2: 3}, {1: 2, 2: 1}) , ({1: 3, 2: 3}, {1: 3, 2: 2})])
        """
        players = state.getPlayerNumbers()
        moves = []
        for player_number in [player for player in players if state.game.players[player].isAlive()]:
            possible_moves_for_player = state.checkFeasibleMoves(player_number, self.possibleActions)
            moves.append(itertools.product([player_number],
                                           possible_moves_for_player))
        temp = itertools.product(*moves)
        dicts = [dict(choices) for choices in temp]
        order_dicts = {}
        for dico in dicts:
            if self.playerNumber in dico:
                if dico[self.playerNumber] not in order_dicts:
                    order_dicts[dico[self.playerNumber]] = [dico]
                else:
                    order_dicts[dico[self.playerNumber]].append(dico)
        res = [order_dicts[key] for key in order_dicts]
        return res

    def _randomChoice(self, choices):
        multiplier = 10
        selector = self.random.randint(0, multiplier * (len(choices) - 1))
        return choices[selector//multiplier]



