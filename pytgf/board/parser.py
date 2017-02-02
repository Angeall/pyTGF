"""
File containing the definition of an abstract BoardParser, and the definition of a TileProperty, used to create a Board
"""

from abc import ABCMeta, abstractmethod
from collections import namedtuple


class IncorrectShapeError(BaseException):
    """
    Exception raised when the parsed board is not rectangular.
    """
    pass


class InvalidCharacterError(BaseException):
    """
    Exception raised when an unknown character is parsed
    """
    pass


TileProperty = namedtuple("TileProperty", "deadly walkable internal_color border_color has_box winning has_player")


class BoardParser(metaclass=ABCMeta):
    """
    Defines an abstract Board Parser, that lacks the method that links a parsed character to a TileProperty
    """

    @abstractmethod
    def characterToTileProperties(self, character: str) -> TileProperty:
        """
        Returns: The tile properties that suits the parsed character, or None if the character is unknown
        """
        pass

    def parseFile(self, file_name: str) -> list:
        """
        Parse a text into a list of Tile types
        Args:
            file_name: The name of the file containing the text to parse into tile types

        Returns: A list of lists containing the types of the tiles in the lines of the future board.
        """
        file = open(file_name, "r")
        text = ""
        for line in file:
            text += line
        tiles_types = self.parse(text)
        return tiles_types

    def parse(self, text: str) -> list:
        """
        Parse a text into a list of Tile types
        Args:
            text: The text to parse into tile types

        Returns: A list of lists containing the types of the tiles in the lines of the future board.
        """
        lines = text.split("\n")  # Split the text into lines
        while lines[-1] == "":
            lines.pop()
        return self.parseLines(lines)

    def parseLines(self, lines) -> list:
        """
        Parse the given lines into a list of Tile types
        Args:
            lines: The lines to parse

        Returns:  A list of lists containing the types of the tiles in the lines of the future board.
        """
        if not self.isRectangularShape(lines):
            raise IncorrectShapeError("The given board has not a rectangular shape: the lines have not the same length")
        tiles = []
        for line in lines:
            tiles_line = []
            for char in line:
                tile_type = self.characterToTileProperties(char)  # type: class
                if tile_type is None:
                    raise InvalidCharacterError("The character %s is unknown for this board parser" % char)
                tiles_line.append(tile_type)
            tiles.append(tiles_line)
        return tiles

    @staticmethod
    def isRectangularShape(lines: list) -> bool:
        """
        Tests if the given lines have a rectangular shape (i.e. every lines have the same length)
        Args:
            lines: The lines to test

        Returns: True if the lines are in a rectangular shape, False otherwise
        """
        line_len = len(lines[0])
        for line in lines:
            if len(line) != line_len:
                return False
        return True
