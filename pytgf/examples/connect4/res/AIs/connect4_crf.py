from typing import List

from pytgf.examples.connect4.controllers import Connect4BotPlayer

try:
    from crfbot import CRFBot
except ModuleNotFoundError:
    from .crfbot import CRFBot


class Connect4CRF(Connect4BotPlayer, CRFBot):

    def _getPrediction(self, seq: List[List[int]]):
        seq_dicts = [{'pl0': seq[i][0], 'pl1': seq[i][1]} for i in range(len(seq))]
        print(seq_dicts)
        return self._model.tag(seq_dicts)

    @property
    def _modelName(self) -> str:
        return "c4crf.bin"
