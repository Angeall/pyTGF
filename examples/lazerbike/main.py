from examples.lazerbike.controllers.player import LazerBikePlayer
from display.boards.square_board import SquareBoardBuilder, SquareBoard
import pygame
from pygame.locals import *

from examples.lazerbike.controllers.allowed_moves import *
from examples.lazerbike.gameloop.game import LazerBikeGame
from examples.lazerbike.sprites.bike import BikeSprite, Bike

if __name__ == "__main__":
    pygame.init()
    surf = pygame.Surface((1920, 1080))
    builder = SquareBoardBuilder(1920, 1080, 50, 75)
    builder.setBackgroundColor((25, 25, 25))
    builder.setTilesVisible(False)
    board = builder.create()
    tile = board.getTileById((25, 25))
    game = LazerBikeGame(board)
    player1 = LazerBikePlayer(1, K_RIGHT, K_LEFT, K_UP, K_DOWN)
    player2 = LazerBikePlayer(2, K_d, K_a, K_w, K_s)
    player3 = LazerBikePlayer(2, K_COMMA, K_k, K_o, K_l)
    player4 = LazerBikePlayer(2, K_h, K_f, K_t, K_g)

    game.addUnit(Bike(1, max_trace=15), player1, (12, 25), GO_RIGHT, team=1)
    # game.addUnit(Bike(3, max_trace=15), player3, (4, 37), GO_DOWN, team=3)
    # game.addUnit(Bike(4, max_trace=15), player4, (45, 37), GO_UP, team=4)
    game.addUnit(Bike(2, max_trace=15), player2, (37, 50), GO_LEFT, team=2)
    game.run()
