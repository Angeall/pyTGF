from typing import Optional, List

import numpy as np

from pytgf.board import Board
from pytgf.board import TileIdentifier
from pytgf.characters.units import MovingUnit
from pytgf.characters.units import Particle
from pytgf.examples.connect4.units.bottom import Bottom
from pytgf.examples.connect4.units.disc import Disc
from pytgf.game import Core


class Connect4Core(Core):

    def __init__(self, board: Board):
        super().__init__(board)
        # Init with an empty board
        self._simplifiedBoard = np.zeros((6, 7))  # type: np.ndarray

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
            team_number = self.unitsTeam[player1]
            self.tilesOccupants[tile_id] = [player1]
            i, j = tile_id
            self._simplifiedBoard[i][j] = team_number  # Updating the simplified board
            self.tilesOccupants[(i, j-1)] = [particle]  # We put the bottom of the line on the upper case
            particle.kill()

            if self._checkWin(i, j, team_number):
                team = self.teams[team_number]
                for _, player_unit in self.players.items():
                    if player_unit not in team:
                        player_unit.kill()

    def _checkWin(self, line: int, column: int, team_number: int) -> bool:
        """
        :param line: The line of the last played disc
        :param column: The column of the last played disc
        :param team_number: The number representing the team of the player that played the last disc
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
                if (slack == team_number).all():
                    finished = True
                    break
                i += 1
                j += 1
            if finished:
                break
        return finished

    def _enumerateLocalRows(self, line: int, column: int) -> List[np.ndarray]:
        """
        :param line: the line of the last disc placed
        :param column: the column of the last disc placed
        :return: a list of rows in which the disc in (line, column) could have changed
        """
        rows = []

        # Diagonals
        inverted_board = np.fliplr(self._simplifiedBoard)
        rows.append(self._simplifiedBoard.diagonal(column - line))
        rows.append(inverted_board.diagonal(6 - column - line))

        # Line
        rows.append(self._simplifiedBoard[line])

        # Column
        rows.append(self._simplifiedBoard[:, column][line:])

        return rows
