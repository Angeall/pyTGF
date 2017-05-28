from typing import List

from .event import Event


class MultipleEvents:
    def __init__(self, events: List[Event]):
        self.events = events