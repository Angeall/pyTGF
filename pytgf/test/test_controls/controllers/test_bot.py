import unittest
from queue import Empty
from typing import List

from ....board import Builder
from ....characters.moves import MoveDescriptor
from ....characters.moves import Path
from ....characters.units import Particle
from ....characters.units import Unit
from ....controls.controllers import Bot, TeammatePayload
from ....game import Core, API


class ExampleAPI(API):
    def _decodeMoveFromPositiveNumber(self, player_number: int, encoded_move: int) -> MoveDescriptor:
        pass

    def _encodeMoveIntoPositiveNumber(self, player_number: int, move_descriptor: MoveDescriptor) -> int:
        pass

    def createMoveForDescriptor(self, unit: Unit, move_descriptor: MoveDescriptor, max_moves: int = -1,
                                force: bool = False, is_step: bool=False) -> Path:
        pass

    def isItOneTestMethod(self):
        if isinstance(self.game, ExampleGame):
            return True
        return False


class ExampleGame(Core):
    @property
    def _teamKillAllowed(self) -> bool:
        return False

    @property
    def _suicideAllowed(self) -> bool:
        return False

    def _collidePlayers(self, player1, player2, tile_id, frontal: bool = False, particle: Particle=None):
        pass


class ExampleBot(Bot):
    @property
    def possibleMoves(self) -> List[MoveDescriptor]:
        return []

    def selectMoveFollowingTeammateMessage(self, teammate_number: int, message):
        pass

    def _getGameStateAPI(self, game: Core):
        return ExampleAPI(game)

    def _isMoveInteresting(self, player_number: int, new_move_event) -> bool:
        return True

    def _isMoveAllowed(self, move) -> bool:
        pass

    def reactToTeammateMessage(self, teammate_number: int, message):
        pass

    def _selectNewMove(self, game_state: API):
        pass


class TestBot(unittest.TestCase):
    def setUp(self):
        self.game = ExampleGame(Builder(10, 10, 7, 6).create())
        self.bot1 = ExampleBot(1)
        self.bot1.gameState = self.game.copy()

    def test_api(self):
        """
        Tests if the controller creates well the custom API for the game
        """
        self.assertIsInstance(self.bot1.gameState, ExampleAPI)
        self.assertTrue(self.bot1.gameState.isItOneTestMethod())

    def test_send_message_to_teammate(self):
        """
        Tests that the message that we want to send to the teammates are well added to the message queue
        """
        self.bot1.sendMessageToTeammate(2, "S2")
        self.bot1.sendMessageToTeammate(3, "S3")
        msg1 = self.bot1.messagesToTeammates.get_nowait()  # type: TeammatePayload
        msg2 = self.bot1.messagesToTeammates.get_nowait()  # type: TeammatePayload
        self.assertRaises(Empty, self.bot1.messagesToTeammates.get_nowait)
        self.assertEqual(msg1.teammateNumber, 2)
        self.assertEqual(msg1.message, "S2")
        self.assertEqual(msg2.teammateNumber, 3)
        self.assertEqual(msg2.message, "S3")
