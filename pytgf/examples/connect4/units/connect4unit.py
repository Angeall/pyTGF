from ....characters.units import Unit

__author__ = "Anthony Rouneau"


class Connect4Unit(Unit):
    def __init__(self, player_number: int):
        super().__init__(player_number)
