from pytgf.characters.units import MovingUnit


class Bottom(MovingUnit):
    def __init__(self, player_number: int):
        super().__init__(player_number)
