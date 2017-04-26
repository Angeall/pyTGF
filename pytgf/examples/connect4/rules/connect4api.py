from .connect4 import Connect4Core
from ..units import Connect4Unit
from ..units.bottom import Bottom
from ..units.disc import Disc
from ....characters.moves import ListPath
from ....characters.moves import MoveDescriptor
from ....characters.moves import Path
from ....characters.moves import ShortMove
from ....controls.wrappers.wrapper import MAX_FPS
from ....game import UnfeasibleMoveException
from ....game.turnbased import TurnBasedAPI


class Connect4API(TurnBasedAPI):
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
        return self.game.getUnitForNumber(player_number).lastAction

    def updateMove(self, unit: Connect4Unit, column_played: int):
        self.numberOfDiscPlayed += 1
        unit.setLastAction(column_played)

    def _encodeMoveIntoPositiveNumber(self, player_number: int, move_descriptor: MoveDescriptor) -> int:
        return move_descriptor

    def _decodeMoveFromPositiveNumber(self, player_number: int, encoded_move: int) -> MoveDescriptor:
        return encoded_move

    def createMoveForDescriptor(self, unit: Connect4Unit, move_desc: MoveDescriptor, force: bool = False,
                                is_step: bool=False) -> Path:
        if isinstance(move_desc, int):
            occupants = self.game.getTileOccupants((0, move_desc))
            if len(occupants) == 0 or isinstance(occupants[0], Bottom):  # Column not full
                team_number = self.game.unitsTeam[unit]
                self.discNumber += 1
                speed = 50
                has_graphics = self.game.board.graphics is not None
                if has_graphics:
                    speed = self.game.board.graphics.size[1] * 2
                disc = Disc(self.discNumber, self.game.unitsTeam[unit], speed=speed, graphics=has_graphics)
                near_bottom = 0
                for i in range(6):
                    occupants = self.game.getTileOccupants((i, move_desc))
                    if len(occupants) > 0 and isinstance(occupants[0], Bottom):
                        near_bottom = i
                        break
                path = ListPath(disc, [ShortMove(disc, self.game.board.getTileById((near_bottom, move_desc)),
                                                 self.game.board.getTileById((near_bottom, move_desc)), MAX_FPS,
                                                 self.game.unitsLocation)],
                                pre_action=lambda: self.game.addUnit(disc, team_number=team_number,
                                                                     origin_tile_id=(near_bottom, move_desc),
                                                                     is_avatar=False, active=False,
                                                                     controlled_by=team_number),
                                post_action=lambda: self.updateMove(unit, move_desc))
                return path
        raise UnfeasibleMoveException("The move " + str(move_desc) + " is unfeasible...")

    def getTileByteCode(self, tile_id: tuple) -> int:
        occupants = self.game.getTileOccupants(tile_id)
        if len(occupants) == 0 or (len(occupants) > 0 and isinstance(occupants[0], Bottom)):
            return 0
        else:
            team_number = self.game.unitsTeam[self.game.getTileOccupants(tile_id)[0]]
            return team_number

    def getDirectWinningMove(self, player_number: int):
        for i in range(7):
            succeeded, new_api = self.simulateMove(player_number, i)
            if succeeded and new_api.hasWon(player_number):
                return i

    def getDirectLosingMove(self, player_number: int):
        other_player_number = (player_number % 2) + 1
        for i in range(7):
            succeeded, new_api = self.simulateMove(other_player_number, i, force=True)
            if succeeded and new_api.hasWon(other_player_number):
                return i
