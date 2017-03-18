from pytgf.characters.moves import MoveDescriptor
from pytgf.characters.moves import Path
from pytgf.characters.units import MovingUnit
from pytgf.examples.connect4.units.bottom import Bottom
from pytgf.examples.connect4.units.disc import Disc
from pytgf.game import API
from pytgf.game import UnfeasibleMoveException


class Connect4API(API):
    def createMoveForDescriptor(self, unit: MovingUnit, move_descriptor: MoveDescriptor, max_moves: int = -1,
                                force: bool = False) -> Path:
        if type(move_descriptor) == int:
            occupants = self.game.getTileOccupants((1, move_descriptor))
            if len(occupants) == 0 or isinstance(occupants[0], Bottom):  # Column not full
                team_number = self.game.unitsTeam[unit]
                disc = Disc(unit.playerNumber)
                self.game.addUnit(disc, graphics=self.game.board.graphics is not None,
                                  team_number=team_number, origin_tile_id=(0, move_descriptor))
                y = 1
                path_list = []
                for i in range(1, 7):
                    if isinstance(# TODO occupant, Bottom)
        raise UnfeasibleMoveException("The move " + str(move_descriptor + " is unfeasible..."))