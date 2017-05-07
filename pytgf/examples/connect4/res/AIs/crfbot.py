import os
import random
from abc import ABCMeta, abstractmethod
from typing import List

import numpy as np
from pycrfsuite import Tagger

from pytgf.characters.moves import MoveDescriptor
from pytgf.controls.controllers import Bot
from pytgf.data.decode.action_sequence_decoder import ActionSequenceDecoder
from pytgf.game import API


class CRFBot(Bot, metaclass=ABCMeta):
    def __init__(self, player_number: int):
        super().__init__(player_number)
        self._model = Tagger()

    def getReady(self):
        print(1)
        self._loadModel()
        print("loaded")

    def _selectNewMove(self, game_state: API) -> MoveDescriptor:
        actions = np.array(game_state.getAllActionsHistories()).tolist()
        actions = ActionSequenceDecoder.getPlayersActionsSequence(actions)
        if len(actions) == 0:
            return random.choice(self.possibleMoves)
        actions_sequence = self._predict(actions, len(game_state.getPlayerNumbers()))
        return game_state.decodeMove(self.playerNumber, actions_sequence[-1])

    def _loadModel(self):
        path = os.path.join(self._modelPath, self._modelName)
        Tagger.open(self._model, path)

    def _decode(self, lst):
        return [int(class_) for class_ in lst]

    def _encode(self, lst, nb_player: int):
        return lst

    def _predict(self, lst: List[List[int]], nb_player: int):
        tab = self._encode(lst, nb_player)
        return self._decode(self._getPrediction(tab))

    @property
    def _modelPath(self) -> str:
        return os.path.join("res", "AIs")

    @property
    @abstractmethod
    def _modelName(self) -> str:
        pass

    @abstractmethod
    def _getPrediction(self, seq: List[List[int]]) -> List[str]:
        pass
