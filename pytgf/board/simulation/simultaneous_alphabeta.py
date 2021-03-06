"""
File containing the definition of an Alpha Beta in which the move simulations are performed simultaneously
for all the players
"""

import itertools
import random
from typing import List, Dict, Union, Callable, TypeVar, Tuple

import numpy as np

from ...characters.moves import MoveDescriptor
from ...game import API

__author__ = 'Anthony Rouneau'

Value = Union[int, float]
T = TypeVar('T')
EndState = Tuple[bool, int, bool]

_RetValue = Tuple[Value, Union[Dict[int, MoveDescriptor], None], EndState, Union[API, None], bool]


class SimultaneousAlphaBeta:
    """
    Implementation of a cutoff AlphaBeta algorithm that performs the moves of all the players simultaneously
    """

    def __init__(self, eval_fct: Callable[[API], Dict[int, Value]],
                 possible_actions: Union[Tuple[MoveDescriptor, ...], List[MoveDescriptor]],
                 max_depth: int = 6, turn_based: bool = False, must_hash_states: bool=True):
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
            must_hash_states: If True, will store states in order to cut off the already-made computations 
        """
        self.eval = eval_fct
        self.maxDepth = max_depth
        if self.maxDepth == -1:  # If there is no maximum depth...
            self.maxDepth = float('inf')
        self.random = random.Random()
        self.possibleActions = possible_actions
        self.actions = {}  # Will retain the best action for a given state (will speed up the tree search)
        self.playerNumber = -1
        self.copyTime = 0
        self.turnByTurn = turn_based
        self._currentMoveSequence = None  # type: np.ndarray
        self._playerMapping = {}
        self._prepared = False
        self._currentlyTestedAction = None
        self._mustHash = must_hash_states
        self._storedStates = {}  # type: Dict[Tuple[Tuple[int, ...], ...], _RetValue]

    # -------------------- PUBLIC METHODS -------------------- #

    def alphaBetaSearching(self, player_number: int, state: API) -> MoveDescriptor:
        """
        :param player_number: The number of the player for which an action must be found
        :param state: The current state of the game (including the current player)
        :type state: API
        :return: the best action among the possible ones
        """
        if not self._prepared:
            self._prepare(player_number, state)
        if self._storedStates.get(state.getBoardByteCodes()) is not None:
            val = self._storedStates[state.getBoardByteCodes()]
            actions = val[1]
        else:
            _, actions, _, _, _ = self._maxValue(state, -float('inf'), float('inf'), 0)
        self.playerNumber = None
        self._prepared = False
        if actions is not None:
            return actions[player_number]
        else:
            return random.choice(self.possibleActions)

    def _prepare(self, player_number: int, state: API):
        self._currentMoveSequence = np.ndarray((len(state.getAlivePlayersNumbers()), 0))
        ordered_list = state.getPlayerNumbers().copy()
        ordered_list.sort()
        self._playerMapping = {play_num: i for i, play_num in enumerate(ordered_list)}
        self.playerNumber = player_number
        self._prepared = True

    # -------------------- PROTECTED METHODS -------------------- #

    @property
    def _mustCutOff(self) -> bool:
        """
        Returns: True if this Alpha beta must cut off when it can, using the alpha and beta bounds.
        """
        return True

    def _maxValue(self, state: API, alpha: float, beta: float, depth: int) -> _RetValue:
        """
        Computes the best step possible for the Player asking this alpha beta

        Args:
            state: The state of the current node
            alpha: The alpha bound that allows to cutoff some branches
            beta: The beta bound that allows to cutoff some branches
            depth: The current depth in the tree
        Returns:
            A 4-uple

              - The best value
              - The best action combination
              - A 3-uple containing :
                    - A bool set to True if the action has reached a end state
                    - An int indicating the depth at which the game ended (0 if the game hasn't ended yet)
                    - A bool set to True if the player for which this AB is launched had won when the game ended
              - The API that represents the game after the best move

        """
        # Check if we reached the end of the tree
        if depth > self.maxDepth:
            score = self._getTeamScore(state, self.eval(state))
            return score, None, (False, depth - 1, False), state, False
        # Check if the game state is final
        elif state.isFinished():
            score = self._getTeamScore(state, self.eval(state))
            return score, None, (True, depth - 1, state.hasWon(self.playerNumber)), state, True
        hashable_state = state.getBoardByteCodes()
        # If we already made the computations, no need to do more
        if self._storedStates.get(hashable_state) is not None:
            return self._storedStates[hashable_state]
        # Initializing the best values
        max_value = -float('inf')
        equally_good_choices = []  # type: List[Tuple[Dict[int, MoveDescriptor], API, bool]]
        end_state = (False, 0, False)
        # Explore every possible actions from this point
        actions_combinations = self._generateMovesCombinations(state)
        random.shuffle(actions_combinations)
        actions_combinations_scores = {}  # type: Dict[float, Tuple[Dict[int, MoveDescriptor], API, bool]]
        for actions in actions_combinations:
            intermediate_state = state
            if depth == 0:
                self._currentlyTestedAction = actions[0][self.playerNumber]
            min_value, min_actions, new_end_state, min_game_state, best_reached_end = \
                self._minValue(intermediate_state, actions, alpha, beta, depth)
            end_state = self._evaluateEndState(end_state, new_end_state)
            actions_combinations_scores[min_value] = min_actions, min_game_state, best_reached_end
            if self._mustCutOff and min_value > beta:  # Cutoff
                ret_val = min_value, min_actions, end_state, min_game_state, best_reached_end
                if best_reached_end and self._mustHash:
                    self._storedStates[min_game_state.getBoardByteCodes()] = ret_val
                return ret_val
            alpha = max(alpha, min_value)
        for score in actions_combinations_scores:
            combination, new_game_state, best_reached_end = actions_combinations_scores[score]
            if score > max_value:
                max_value = score
                equally_good_choices = [(combination, new_game_state, best_reached_end)]
            elif score == max_value:
                equally_good_choices.append((combination, new_game_state, best_reached_end))
        if len(equally_good_choices) == 0:  # No choice is good to take...
            print("no choice is good to take")
            return self._getTeamScore(state, self.eval(state)), None, \
                (state.isFinished(), depth, state.hasWon(self.playerNumber)), None, False
        best_combination, best_game_state, best_reached_end = random.choice(equally_good_choices)
        ret_val = max_value, best_combination, end_state, best_game_state, best_reached_end
        if best_reached_end and self._mustHash:
            self._storedStates[best_game_state.getBoardByteCodes()] = ret_val
        return ret_val

    @staticmethod
    def _evaluateEndState(current_end_state: EndState, new_end_state: EndState) -> EndState:
        """
        Updates the end state if needed

        Args:
            current_end_state: The end state currently used
            new_end_state: The new end state coming from the depth further

        Returns: The end state that was updated if it was needed
        """
        if new_end_state[0]:
            if current_end_state[0]:  # If the current state finished the game
                if current_end_state[2]:
                    if new_end_state[2]:  # If both states ends in a win from the player
                        nb_turn = min(current_end_state[1], new_end_state[1])  # The less turn to win the better
                        return True, nb_turn, True
                    else:  # The new state ends in a loss while the initial ended in a win
                        return current_end_state
                elif new_end_state[2]:  # The new state finishes in a win
                    return new_end_state  # We save that chance to win
                else:  # Both states ends in an inevitable loss
                    nb_turn = max(current_end_state[1], new_end_state[1])
                    return True, nb_turn, False
            else:  # Only the new state finishes the game => no doubt, we need to update the current state
                return new_end_state
        else:  # The new state hasn't reached a final state => indeterminate... benefit of the doubt
            if not current_end_state[2]:
                return False, 0, False
        return current_end_state

    def _minValue(self, state: API, actions: List[Dict[int, MoveDescriptor]], alpha: float, beta: float, depth: int) \
            -> _RetValue:
        """
        Computes the possibilities of the other players, simulating the action of every players at the same time

        Args:
            state: The state of the current node
            actions:
            alpha: The alpha bound that allows to cutoff some branches
            beta: The beta bound that allows to cutoff some branches
            depth: The current depth in the tree

        Returns:
            A 4-uple

            - The best value
              - The best action combination
              - A 3-uple containing :
                    - A bool set to True if the action has reached a end state
                    - An int indicating the depth at which the game ended (0 if the game hasn't ended yet)
                    - A bool set to True if the player for which this AB is launched had won when the game ended
              - The API that represents the game after the best move
        """
        min_value = float('inf')
        equal_min_choices = []  # type: List[Tuple[Dict[int, MoveDescriptor], API, bool]]
        end_state = (False, 0, False)
        for combination in actions:
            simulation_combination = combination
            feasible_moves, new_game_state = self._simulateMoves(simulation_combination, state)
            if feasible_moves and new_game_state is not None:
                value, _, new_end_state, game_state, best_reached_end = \
                                        self._maxValue(new_game_state, alpha, beta, depth + 1)
                end_state = self._evaluateEndState(end_state, new_end_state)
                if value < min_value:
                    min_value = value
                    equal_min_choices = [(combination, new_game_state, best_reached_end)]
                elif value == min_value:
                    equal_min_choices.append((combination, new_game_state, best_reached_end))
                if self._mustCutOff and value < alpha:  # Cutoff because we are in a min situation
                    best_combination, new_game_state, best_reached_end = random.choice(equal_min_choices)
                    ret_val = value, best_combination, end_state, new_game_state, best_reached_end
                    if best_reached_end and self._mustHash:
                        self._storedStates[new_game_state.getBoardByteCodes()] = ret_val
                    return ret_val
                beta = min(beta, value)
        min_actions, new_game_state, best_reached_end = random.choice(equal_min_choices)
        ret_val = min_value, min_actions, end_state, new_game_state, best_reached_end
        if best_reached_end and self._mustHash:
            self._storedStates[new_game_state.getBoardByteCodes()] = ret_val
        return ret_val

    def _simulateMoves(self, simulation_combination, state):
        return state.simulateMoves(simulation_combination)

    def _getActionsList(self, actions: Dict[int, MoveDescriptor], state: API) -> np.ndarray:
        """

        Args:
            actions: The dict linking the actions with the players
            state: The state representing the game before the moves are performed

        Returns: A vertical vector of moves, which can be horizontally stacked with another matrix

        """
        actions_list = np.zeros((len(self._playerMapping), 1))
        actions_list -= 2  # -2 = player is dead => we first assume that every player is dead
        for player_number, move_descriptor in actions.items():
            actions_list[self._playerMapping[player_number]] = state.encodeMove(player_number, move_descriptor)
        return actions_list

    def _getTeamScore(self, state: API, players_score: Dict[int, Value]) -> float:
        """
        Given a tuple of players individual score for the given state, computes the score for the team of the player
        for which this alpha beta is running.

        Args:
            state: the state for which the given score has been computed
            players_score: The tuple of score, computed by the evaluation function

        Returns: The score of the team of the player of this AlphaBeta
        """
        own_team_score = 0
        for player_number, player_score in players_score.items():
            if player_number == self.playerNumber or state.belongsToSameTeam(player_number, self.playerNumber):
                own_team_score += player_score
        return own_team_score

    def _generateMovesList(self, state: API) -> List[Dict[int, MoveDescriptor]]:
        """
        Generates all the possible combinations of movements for the given state

        Args:
            state: The state for which the movements will be evaluated

        Returns:
            A list of dictionaries
            (e.g. {1: 2, 2: 3} indicates that the player 1 chose the action "2" and the player 2 chose the action "3")
        """
        players = state.getPlayerNumbers()
        moves = self._getPossibleMoves(players, state)
        temp = itertools.product(*moves)
        dicts = [dict(choices) for choices in temp]
        if self.turnByTurn:
            unfeasible = []
            for moves in dicts:
                succeeded, _ = state.simulateMoves(moves)
                if not succeeded:
                    unfeasible.append(moves)
            dicts = [dicts[i] for i in range(len(dicts)) if dicts[i] not in unfeasible]
        return dicts

    def _generateMovesCombinations(self, state: API) -> List[List[Dict[int, MoveDescriptor]]]:
        """
        Generates all the possible combinations of movements for the given state, and arrange them into a list of list 
        structure

        Args:
            state: The state for which the movements will be evaluated

        Returns:
            A list of lists of dictionaries
            (e.g. {1: 2, 2: 3} indicates that the player 1 chose the action "2" and the player 2 chose the action "3")
            The list contains lists, containing all the dictionaries containing the same actions for the player
            concerned in this alpha beta. (e.g. [[{1: 2, 2: 3}, {1: 2, 2: 1}] , [{1: 3, 2: 3}, {1: 3, 2: 2}]])
        """
        dicts = self._generateMovesList(state)
        order_dicts = {}
        for dico in dicts:
            if self.playerNumber in dico:
                if dico[self.playerNumber] not in order_dicts:
                    order_dicts[dico[self.playerNumber]] = [dico]
                else:
                    order_dicts[dico[self.playerNumber]].append(dico)
        res = [order_dicts[key] for key in order_dicts]
        return res

    def _getPossibleMoves(self, players: List[int], state: API) -> List[Tuple[int, MoveDescriptor]]:
        """
        Generate all the possible moves for the players

        Args:
            players: The list of player numbers for which generate the moves
            state: The API for which the move will be generated

        Returns: A list containing couples [player_number, move_descriptor]
        """
        moves = []
        for player_number in [player for player in players if state.game.avatars[player].isAlive()]:
            possible_moves_for_player = self._getPossibleMovesForPlayer(player_number, state)
            moves.append(itertools.product([player_number],
                                           possible_moves_for_player))
        return moves

    def _getPossibleMovesForPlayer(self, player_number: int, state: API) -> List[MoveDescriptor]:
        """
        Get the possible moves for the given player

        Args:
            player_number:  The number representing the player for which the moves must be generated
            state: The API for which the moves must be generated

        Returns: A list of move descriptors possible for the given player and API
        """
        possible_moves_for_player = state.checkFeasibleMoves(player_number, self.possibleActions)
        random.shuffle(possible_moves_for_player)
        return possible_moves_for_player
