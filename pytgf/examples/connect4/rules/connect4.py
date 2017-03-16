from typing import Optional

import numpy as np

from pytgf.board import Board
from pytgf.board import TileIdentifier
from pytgf.characters.units import MovingUnit
from pytgf.characters.units import Particle
from pytgf.examples.connect4.units.bottom import Bottom
from pytgf.examples.connect4.units.disc import Disc
from pytgf.game import Core
from pytgf.game.core import InconsistentGameStateException


class Connect4(Core):

    def __init__(self, board: Board):
        super().__init__(board)
        self._simplifiedBoard = np.zeros((6, 7))  # Init with an empty board

    @property
    def _teamKillAllowed(self) -> bool:
        return False

    @property
    def _suicideAllowed(self) -> bool:
        return False

    def _collidePlayers(self, player1: MovingUnit, player2: MovingUnit, tile_id: TileIdentifier, frontal: bool = False,
                        particle: Optional[Particle]=None):
        assert particle is not None
        if isinstance(player2, Bottom) and isinstance(player1, Disc):
            # TODO: need to find the location of the collision... Problem : player and not particle...
            self.unitsLocation[tile_id] = player1
            if self._checkWin():
                for player_number, player_unit in self.players.items():
                    if player_number is not player1.playerNumber:
                        player_unit.kill()

    def _checkWin(self) -> True:
        # TODO: Use _computeTerminalStateLocally
        return False

    def _computeTerminalStateLocally(self, line, column, player_number: int):
        """
        :param line: The line of the last played disc
        :param column: The column of the last played disc
        :param color: The color of the last disc played
        :return: a tuple containing three booleans : (red_won, green_won, draw).
                 red_won, green_won is True if there is 4 discs of that color in a row
                 and draw is True if there is a draw
        :rtype: tuple

        Assume that the game was not terminal before the disc at (line, column) was placed.
        Check if the game is terminated due to the (line, column) disc.
        """
        rows = self._enumerateLocalRows(line, column)
        finished = False
        for row in rows:
            i = 0
            j = 4
            while j <= len(row) and not finished:
                slack = row[i:j]
                if (slack == player_number).all():
                    finished = True
                    break
                i += 1
                j += 1
            if finished:
                break
        return finished

    def _enumerateLocalRows(self, line, column):
        """
        :param line: the line of the last disc placed
        :param column: the column of the last disc placed
        :return: a list of rows in which the disc in (line, column) could have changed
        """
        # TODO: self.board is to transform into "self.simplifiedBoard" which is a np.ndarray of 1 and 2s (player nums)
        rows = []
        board = np.zeros((6, 7), np.uint8)
        for i in range(self.board.lines):
            for j in range(self.board.columns):
                occupants = self.getTileOccupants((i, j))
                if len(occupants) > 0:
                    if len(occupants) > 1:
                        raise InconsistentGameStateException("Tile (%d, %d) has more than one occupant" % (i, j))
                    board[i][j] = occupants[0].playerNumber
        # Diagonals
        inverted_board = np.fliplr(board)
        rows.append(self.board.diagonal(column - line))
        rows.append(inverted_board.diagonal(6 - column - line))

        # Line
        rows.append(self.board[line])

        # Column
        rows.append(self.board[:, column][line:])

        return rows