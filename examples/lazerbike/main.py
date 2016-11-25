from examples.lazerbike.controllers.player1 import Player1
from display.boards.square_board import SquareBoardBuilder, SquareBoard
import pygame

from examples.lazerbike.controllers.allowed_moves import *
from examples.lazerbike.gameloop.game import LazerBikeGame
from examples.lazerbike.sprites.bike import BikeSprite, Bike

if __name__ == "__main__":
    pygame.init()
    surf = pygame.Surface((1920, 1080))
    builder = SquareBoardBuilder(1920, 1080, 50, 75)
    # builder.setBackgroundColor((25, 25, 25))
    board = builder.create()
    sprite = BikeSprite()
    tile = board.getTileById((25, 25))
    game = LazerBikeGame(board)
    # TODO : add a turn method to a Bike class so the bike can easily turn from any position to any other
    game.addUnit(Bike(sprite, GO_RIGHT), Player1(), (25, 25), GO_RIGHT)
    del sprite
    game.run()
