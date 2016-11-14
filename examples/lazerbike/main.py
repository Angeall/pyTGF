from display.boards.square_board import SquareBoardBuilder, SquareBoard
import pygame

from examples.lazerbike.gameloop.game import LazerBikeGame
from examples.lazerbike.sprites.bike import BikeSprite
from units.unit import Unit

if __name__ == "__main__":
    pygame.init()
    surf = pygame.Surface((720, 480))
    builder = SquareBoardBuilder(surf, 50, 50)
    # builder.setBackgroundColor((25, 25, 25))
    board = builder.create()
    sprite = BikeSprite()
    board.getTileById((25, 25)).addOccupant(Unit(sprite))
    game = LazerBikeGame(board)
    game.run()
