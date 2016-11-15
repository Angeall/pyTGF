from display.boards.square_board import SquareBoardBuilder, SquareBoard
import pygame

from examples.lazerbike.gameloop.game import LazerBikeGame
from examples.lazerbike.sprites.bike import BikeSprite
from characters.unit import Unit

if __name__ == "__main__":
    pygame.init()
    surf = pygame.Surface((1920, 1080))
    builder = SquareBoardBuilder(surf, 50, 75)
    # builder.setBackgroundColor((25, 25, 25))
    board = builder.create()
    sprite = BikeSprite()

    tile = board.getTileById((25, 25))
    tile.addOccupant(Unit(sprite))
    tile.setInternalColor((255, 0, 0))
    game = LazerBikeGame(board)
    game.run()
