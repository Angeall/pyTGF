import random

import itertools
import functools
import numpy as np

from game.gamestate import GameState

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

    def alphaBetaSearching(self, player_number: int, state: GameState):
        """
        :param player_number: The number of the player for which an action must be found
        :param state: The current state of the game (including the current player)
        :type state: GameState
        :return: the best action among the possible ones
        """
        self.playerNumber = player_number
        if self.actions.get(state) is not None:
            value, actions = self.actions[state]
        else:
            value, actions, _ = self.depthSearch(state, (-float('inf'), float('inf')), 0)
        self.playerNumber = None
        if actions is not None:
            return actions[player_number]
        else:
            return random.choice(self.possibleActions)

    def depthSearch(self, state: GameState, bounds: tuple, depth: int):
        """
        :param state: the state of the current node
        :type state: GameState
        :param bounds: the previous bounds (alpha, beta)
        :param depth: the current depth in the tree
        :return: the best value and the best action among its children or
                 the value of the terminal state
                 True if the action has reached a end state

        Computes the best step possible for the "MAX" Player
        """
        alpha, beta = bounds
        # Check if we reached the end of the tree
        if depth > self.max_depth:
            score = self._getTeamScore(state, self.eval(state))
            return score, None, False
        # Check if the game state is final
        elif state.isFinished():
            return self._getTeamScore(state, self.eval(state)), None, True

        # Initializing the best values
        best_pessimistic_value = -float('inf')
        best_optimistic_value = float('inf')
        best_mean_value = -float('inf')
        equally_good_choices = []
        best_reached_end = False

        # # If we already made the computations, no need to do more
        # if self.actions.get(state) is not None:
        #     return self.actions.get(state), True

        # Explore every possible actions from this point
        combinations = self._generateMovesCombinations(state)
        for actions in combinations:
            feasible_moves, new_game_state = state.simulateMoves(actions)
            if feasible_moves and new_game_state is not None:
                (pessimistic_value, optimistic_value), _, reached_end = self.depthSearch(new_game_state,
                                                                                         (alpha, beta), depth + 1)
                if pessimistic_value > best_pessimistic_value:
                    best_pessimistic_value = pessimistic_value
                if optimistic_value < best_optimistic_value:
                    best_optimistic_value = optimistic_value
                if pessimistic_value - optimistic_value > best_mean_value:  # Trying to maximize the mean value
                    best_mean_value = pessimistic_value - optimistic_value
                    equally_good_choices = [actions]
                    best_reached_end = reached_end
                elif pessimistic_value - optimistic_value == best_mean_value:
                    equally_good_choices.append(actions)
                if best_pessimistic_value >= beta or best_optimistic_value <= alpha:  # Cutoff
                    choices = self.random.choice(equally_good_choices)
                    # if best_reached_end:  # If the reached state was final, stock the best action for this state
                    #     self.actions[state] = best_pessimistic_value, best_optimistic_value, best_action
                    return (best_pessimistic_value, best_optimistic_value), choices, best_reached_end
                alpha = max(alpha, pessimistic_value)
                beta = min(beta, optimistic_value)
        if len(equally_good_choices) == 0:
            return (-1000, 1000), None, True
        choices = self.random.choice(equally_good_choices)
        # if best_reached_end:  # If the reached state was final, we can stock the best action for this state
        #     self.actions[state] = best_pessimistic_value, best_optimistic_value, best_action
        return (best_pessimistic_value, best_optimistic_value), choices, best_reached_end

    def _getTeamScore(self, state: GameState, players_score: tuple) -> tuple:
        """
        Given a tuple of players individual score for the given state, computes the score for the team of the player
        for which this alpha beta is running and the mean score of every other teams

        Args:
            state: the state for which the given score has been computed
            players_score: The tuple of score, computed by the evaluation function

        Returns:
            A tuple containing the score of the team of the player of this AlphaBeta, followed by the sum of the
            score of every other teams, divided by the number of other team.
        """
        own_team_score = 0
        other_teams_score = 0
        player_numbers = state.getPlayerNumbers()
        for player_index, player_score in enumerate(players_score):
            player_number = player_numbers[player_index]
            if player_number == self.playerNumber or state.belongsToSameTeam(player_number, self.playerNumber):
                own_team_score += player_score
            else:
                other_teams_score += player_score
        return own_team_score, other_teams_score/(state.getNumberOfTeams() - 1)

    def _generateMovesCombinations(self, state: GameState) -> list:
        """
        Generates al the possible combinations of movements for the given state

        Args:
            state: The state for which the movements will be evaluated

        Returns:
            A list of dictionary
            - {1: 2, 2: 3} indicates that the player 1 chose the action "2" and the player 2 chose the action "3".
        """
        players = state.getPlayerNumbers()
        moves = []
        for player_number in players:
            possible_moves_for_player = state.checkFeasibleMoves(player_number, self.possibleActions)
            moves.append(tuple(itertools.product([player_number],
                                                 possible_moves_for_player)))
        temp = tuple(itertools.product(*moves))
        dicts = []
        for choices in temp:
            temp_dict = dict(choices)
            dicts.append(temp_dict)
        return dicts



