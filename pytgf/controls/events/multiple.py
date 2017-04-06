from typing import List

from pytgf.controls.events import Event


class MultipleEvents:
    def __init__(self, events: List[Event]):
        self.events = events