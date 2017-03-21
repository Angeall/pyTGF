from pytgf.characters.units import MovingUnit

__author__ = "Anthony Rouneau"


class Connect4Unit(MovingUnit):
    def __init__(self, player_number: int):
        super().__init__(player_number)
        self.lastColumnPlayed = -1

    def setLastColumnPlayed(self, last_column_played: int):
        self.lastColumnPlayed = last_column_played
