import random

import numpy as np

from game_state import GameState


__author__ = 'Anthony Rouneau'


class MaxN:
    """
    Simple implementation of a cutoff MaxN algorithm
    Assert that the player using this Alpha Beta is the "MAX" player.
    """
    def __init__(self, eval_fct, possible_actions: list, teams: dict, max_depth=6):
        """

        Args:
            eval_fct: objective function that computes a score tuple given a state for one player
            possible_actions: The list of possible actions accepted in the game for all players
            max_depth: the maximum depth of the tree the algorithm can explore
        """
        self.eval = eval_fct
        self.max_depth = max_depth
        self.random = random.Random()
        self.possibleActions = possible_actions
        self.teams = teams
        self.actions = {}  # Will retain the best action for a given state (will speed up the tree search)

    def alphaBetaSearching(self, state):
        """
        :param state: The current state of the game (including the current player)
        :type state: GameState
        :return: the best action among the possible ones
        """
        if self.actions.get(state) is not None:
            value, action = self.actions[state]
        else:
            value, action, _ = self.maxValue(state, -float('inf'), float('inf'), 0)
        return action

    def maxValue(self, state, alpha, beta, depth):
        """
        :param state: the state of the current node
        :type state: GameState
        :param alpha: the alpha bound
        :param beta: the beta bound
        :param depth: the current depth in the tree
        :return: the best value and the best action among its children or
                 the value of the terminal state
                 True if the action has reached a end state
        Computes the best step possible for the "MAX" Player
        """
        # Check if we reached the end of the tree
        if depth > self.max_depth:
            return self.eval(state, player_number=False), None, False
        # Check if the game state is final
        elif np.array(state.terminalTest()).any():
            return self.eval(state, player_number=False), None, True

        # Initializing the best values
        best_value = -float('inf')
        best_actions = []
        best_reached_end = False

        # If we already made the computations, no need to do more
        if self.actions.get(state) is not None:
            return self.actions.get(state), True

        # Explore every possible actions from this point
        for action in state.possibleActions():
            value, _, reached_end = self.minValue(state.simulateAction(action), alpha, beta, depth + 1)
            if value > best_value:
                best_value = value
                best_actions = [action]
                best_reached_end = reached_end
                if best_value >= beta:
                    best_action = best_actions[self.random.randint(0, len(best_actions)-1)]
                    if best_reached_end:  # If the reached state was final, we can stock the best action for this state
                        self.actions[state] = best_value, best_action
                    return best_value, best_action, best_reached_end
            elif value == best_value:
                best_actions.append(action)
            alpha = max(alpha, value)
        best_action = best_actions[self.random.randint(0, len(best_actions) - 1)]
        if best_reached_end:  # If the reached state was final, we can stock the best action for this state
            self.actions[state] = best_value, best_action
        return best_value, best_action, best_reached_end

    def minValue(self, state, alpha, beta, depth):
        """
        :param state: the state of the current node
        :type state: GameState
        :param alpha: the alpha bound
        :param beta: the beta bound
        :param depth: the current depth in the tree
        :return: the best value and the best action among its children or
                 the value of the terminal state
        Computes the best step possible for the "MAX" Player
        """
        # Check if we reached the end of the tree
        if depth > self.max_depth:
            return self.eval(state, player_number=True), None, False
        # Check if the game state is final
        if np.array(state.terminalTest()).any():
            return self.eval(state, player_number=True), None, True

        # Initializing the best values
        best_value = float('inf')
        best_actions = []
        best_reached_end = False

        # If we already made the computations, no need to do more
        if self.actions.get(state) is not None:
            return self.actions.get(state), True

        # Explore every possible actions from this point
        for action in state.possibleActions():
            value, _, reached_end = self.maxValue(state.simulateAction(action), alpha, beta, depth + 1)
            if value < best_value:
                best_value = value
                best_actions = [action]
                best_reached_end = reached_end
                if best_value <= alpha:
                    best_action = best_actions[self.random.randint(0, len(best_actions) - 1)]
                    if best_reached_end:  # If the reached state was final, we can stock the best action for this state
                        self.actions[state] = best_value, best_action
                    return best_value, best_action, best_reached_end
            elif value == best_value:
                best_actions.append(action)
            beta = min(beta, value)
        best_action = best_actions[self.random.randint(0, len(best_actions) - 1)]
        if best_reached_end:  # If the reached state was final, we can stock the best action for this state
            self.actions[state] = best_value, best_action
        return best_value, best_action, best_reached_end



