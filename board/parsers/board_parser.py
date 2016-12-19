from abc import ABCMeta, abstractmethod


class IncorrectShapeError(BaseException):
    pass


class InvalidCharacterError(BaseException):
    pass


class InvalidCharacterConversionError(BaseException):
    pass


class BoardParser(metaclass=ABCMeta):

    @abstractmethod
    def characterToTileType(self, character: str):
        """
        Returns: the Tile type, which can be instantiated later, corresponding to the given character
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
            text += (line.strip() + "\n")
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
                try:
                    tile_type = self.characterToTileType(char)  # type: class
                    if type(tile_type) != type:
                        msg = "The character %s was converted into a %s rather than a instantiable class" \
                                % (char, str(type(tile_type)))
                        raise InvalidCharacterConversionError(msg)
                    tiles_line.append(tile_type)
                except KeyError:
                    raise InvalidCharacterError("The character %s is unknown for this board parser" % char)
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
