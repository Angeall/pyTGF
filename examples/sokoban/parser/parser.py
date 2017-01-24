from gameboard.parsers.board_parser import BoardParser
from gameboard.tile import Tile
from examples.sokoban.tiles.hole import Hole
from examples.sokoban.tiles.wall import Wall
from examples.sokoban.tiles.winning import Winning
from examples.sokoban.units.box import Box
from examples.sokoban.units.sokobandrawstick import SokobanDrawstick


class SokobanBoardParser(BoardParser):
    def characterToTileProperties(self, character: str):
        character = character.lower()
        if character == "h":
            return Hole
        elif character == "b":
            return Box
        elif character == "p":
            return SokobanDrawstick
        elif character == " ":
            return Tile
        elif character == "w":
            return Wall
        elif character == "e":
            return Winning
