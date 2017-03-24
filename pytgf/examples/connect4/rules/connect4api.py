from pytgf.characters.moves import ListPath
from pytgf.characters.moves import MoveDescriptor
from pytgf.characters.moves import Path
from pytgf.characters.moves import ShortMove
from pytgf.controls.wrappers.wrapper import MAX_FPS
from pytgf.examples.connect4.rules import Connect4Core
from pytgf.examples.connect4.units import Connect4Unit
from pytgf.examples.connect4.units.bottom import Bottom
from pytgf.examples.connect4.units.disc import Disc
from pytgf.game import API
from pytgf.game import UnfeasibleMoveException


class Connect4API(API):
    def __init__(self, game: Connect4Core):
        self.discNumber = 100
        self.numberOfDiscPlayed = 0
        super().__init__(game)

    def getLastMove(self, player_number: int):
        """
        Get the last column number in which the given player has put a disc in.

        Args:
            player_number: The number representing the player for which we want the last move

        Returns:
            One of the values below:

            - -1 if the given player hasn't played yet
            - -2 if the given player has lost
            - The number of the last column played otherwise
        """
        if self.game.isFinished():
            if not self.hasWon(player_number):
                return -2
        return self.game.getUnitForNumber(player_number).lastColumnPlayed

    def updateMove(self, unit: Connect4Unit, column_played: int):
        self.numberOfDiscPlayed += 1
        unit.setLastAction(column_played)

    def _encodeMoveIntoPositiveNumber(self, player_number: int, move_descriptor: MoveDescriptor) -> int:
        return move_descriptor

    def _decodeMoveFromPositiveNumber(self, player_number: int, encoded_move: int) -> MoveDescriptor:
        return encoded_move

    def createMoveForDescriptor(self, unit: Connect4Unit, move_descriptor: MoveDescriptor, max_moves: int = -1,
                                force: bool = False) -> Path:
        if isinstance(move_descriptor, int):
            occupants = self.game.getTileOccupants((0, move_descriptor))
            if len(occupants) == 0 or isinstance(occupants[0], Bottom):  # Column not full
                team_number = self.game.unitsTeam[unit]
                self.discNumber += 1
                disc = Disc(self.discNumber, self.game.unitsTeam[unit], speed=self.game.board.graphics.size[1] * 2)
                self.game.addUnit(disc, team_number=team_number, origin_tile_id=(0, move_descriptor), controlled=False)
                if len(occupants) == 0 or not isinstance(occupants[0], Bottom):
                    path_list = []
                    for i in range(1, 6):
                        path_list.append((i, move_descriptor))
                        occupants = self.game.getTileOccupants((i, move_descriptor))
                        if len(occupants) > 0 and isinstance(occupants[0], Bottom):
                            break
                    path = ListPath(disc, [ShortMove(disc, self.game.board.getTileById((i - 1, j)),
                                                     self.game.board.getTileById((i, j)), MAX_FPS,
                                                     self.game.unitsLocation)
                                           for i, j in path_list],
                                    post_action=lambda: self.updateMove(unit, move_descriptor))
                else:
                    path = ListPath(disc, [ShortMove(disc, self.game.board.getTileById((0, move_descriptor)),
                                                     self.game.board.getTileById((0, move_descriptor)), MAX_FPS,
                                                     self.game.unitsLocation)],
                                    post_action=lambda: self.updateMove(unit, move_descriptor))
                return path
        raise UnfeasibleMoveException("The move " + str(move_descriptor) + " is unfeasible...")

    def getTileByteCode(self, tile_id: tuple) -> int:
        if len(self.game.getTileOccupants(tile_id)) == 0:
            return 0
        else:
            return self.game.unitsTeam[self.game.getTileOccupants(tile_id)[0]]
