from pytgf.controls.event import Event


class SpecialEvent(Event):
    RESURRECT_UNIT = 2
    UNIT_KILLED = 1
    END = 0

    def __init__(self, flag: int):
        self.flag = flag
