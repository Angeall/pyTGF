from game.game import Game


class GameState:

    def __init__(self, game: Game):
        self.game = game

    def simulateMove(self, player_number: int, wanted_move):
        """
        Simulates the move by creating a new GameState

        Args:
            player_number: The number of the player moving
            wanted_move: The event triggering the move

        Returns:
            A copy of this GameState in which the move have been applied (if it is possible)
        """
        new_game_state = GameState(self.game)
        new_game_state.performMove(player_number, wanted_move)
        return new_game_state

    def simulateMoves(self, player_moves: dict):
        """
        Simulates the given moves for the key players

        Args:
            player_moves: a dictionary with player_numbers as keys and a list of moves for the key player

        Returns:
            A copy of this GameState in which the moves have been applied (if they are possible)
        """
        new_game_state = GameState(self.game)
        for player_number, wanted_move in player_moves.items():
            new_game_state.performMove(player_number, wanted_move)
        return new_game_state

    def performMove(self, player_number: int, wanted_move):
        """
        Performs the move inside this GameState

        Args:
            player_number: The number of the player moving
            wanted_move: The event triggering the move
        """
        unit = self.game.players[player_number]
        move = self.game.createMoveForEvent(unit, wanted_move, max_moves=1)
        move.complete()
