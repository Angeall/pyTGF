from display.boards.square_board import SquareBoardBuilder, SquareBoard
from pygame import Surface
from examples.lazerbike.exec.game import LazerBikeGame
from examples.lazerbike.sprites.bike import BikeSprite

if __name__=="__main__":
    surf = Surface((720, 480))
    builder = SquareBoardBuilder(surf, 50, 50)
    builder.setBackgroundColor((25, 25, 25))
    board = builder.create()
    sprite = BikeSprite()
    board.getTileById((25, 25)).addOccupant()
    game = LazerBikeGame(board)
    game.run()


