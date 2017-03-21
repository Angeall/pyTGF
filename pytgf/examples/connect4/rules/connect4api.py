from pytgf.characters.moves import ListPath
from pytgf.characters.moves import MoveDescriptor
from pytgf.characters.moves import Path
from pytgf.characters.moves import ShortMove
from pytgf.characters.units import MovingUnit
from pytgf.controls.wrappers.wrapper import MAX_FPS
from pytgf.examples.connect4.units.bottom import Bottom
from pytgf.examples.connect4.units.disc import Disc
from pytgf.game import API
from pytgf.game import Core
from pytgf.game import UnfeasibleMoveException


class Connect4API(API):

    def __init__(self, game: Core):
        self.discNumber = 100
        super().__init__(game)

    def createMoveForDescriptor(self, unit: MovingUnit, move_descriptor: MoveDescriptor, max_moves: int = -1,
                                force: bool = False) -> Path:
        if isinstance(move_descriptor, int):
            occupants = self.game.getTileOccupants((0, move_descriptor))
            if len(occupants) == 0 or isinstance(occupants[0], Bottom):  # Column not full
                team_number = self.game.unitsTeam[unit]
                self.discNumber += 1
                disc = Disc(self.discNumber, self.game.unitsTeam[unit], speed=self.game.board.graphics.size[1]*2)
                self.game.addUnit(disc, team_number=team_number, origin_tile_id=(0, move_descriptor))
                y = 1
                if len(occupants) == 0 or not isinstance(occupants[0], Bottom):
                    path_list = []
                    for i in range(1, 6):
                        path_list.append((i, move_descriptor))
                        occupants = self.game.getTileOccupants((i, move_descriptor))
                        if len(occupants) > 0 and isinstance(occupants[0], Bottom):
                            break
                    path = ListPath(disc, [ShortMove(disc, self.game.board.getTileById((i-1, j)),
                                           self.game.board.getTileById((i, j)), MAX_FPS, self.game.unitsLocation)
                                           for i, j in path_list])
                else:
                    path = ListPath(disc, [ShortMove(disc, self.game.board.getTileById((0, move_descriptor)),
                                                     self.game.board.getTileById((0, move_descriptor)), MAX_FPS,
                                                     self.game.unitsLocation)])
                return path
        raise UnfeasibleMoveException("The move " + str(move_descriptor) + " is unfeasible...")
