from collections import namedtuple

from gameboard.parsers.board_parser import BoardParser


TileProperty = namedtuple("TileProperty", "deadly walkable internal_color border_color has_box winning has_player")
hole = TileProperty(deadly=True, walkable=True, internal_color=(0, 0, 0), border_color=None, has_box=False,
                    winning=False, has_player=False)
wall = TileProperty(deadly=False, walkable=False, internal_color=(125, 85, 7), border_color=None, has_box=False,
                    winning=False, has_player=False)
box = TileProperty(deadly=False, walkable=True, internal_color=None, border_color=None, has_box=True, winning=False,
                   has_player=False)
player_tile = TileProperty(deadly=False, walkable=True, internal_color=None, border_color=None, has_box=False,
                           winning=False, has_player=True)
classical_tile = TileProperty(deadly=False, walkable=True, internal_color=None, border_color=None, has_box=False,
                              winning=False, has_player=False)
winning = TileProperty(deadly=False, walkable=True, internal_color=(0, 255, 0), border_color=None, has_box=False,
                       winning=True, has_player=False)


class SokobanBoardParser(BoardParser):
    def characterToTileProperties(self, character: str) -> tuple:
        character = character.lower()
        if character == "h":
            return hole
        elif character == "b":
            return box
        elif character == "p":
            return player_tile
        elif character == " ":
            return classical_tile
        elif character == "w":
            return wall
        elif character == "e":
            return winning
