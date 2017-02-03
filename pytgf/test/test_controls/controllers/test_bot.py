import unittest
from queue import Empty

from pytgf.board import Builder
from pytgf.characters.moves import Path
from pytgf.characters.units import MovingUnit
from pytgf.controls.controllers import Bot, TeammatePayload
from pytgf.game import Game, GameState


class ExampleAPI(GameState):
    def isItOneTestMethod(self):
        if isinstance(self.game, ExampleGame):
            return True
        return False


class ExampleGame(Game):
    @property
    def _teamKillAllowed(self) -> bool:
        return False

    @property
    def _suicideAllowed(self) -> bool:
        return False

    def createMoveForDescriptor(self, unit: MovingUnit, move_descriptor, max_moves: int = -1,
                                force: bool = False) -> Path:
        pass

    def _collidePlayers(self, player1, player2, frontal: bool = False):
        pass


class ExampleBot(Bot):
    def selectMoveFollowingTeammateMessage(self, teammate_number: int, message):
        pass

    def _getGameStateAPI(self, game: Game):
        return ExampleAPI(game)

    def _isMoveInteresting(self, player_number: int, new_move_event) -> bool:
        return True

    def _isMoveAllowed(self, move) -> bool:
        pass

    def reactToTeammateMessage(self, teammate_number: int, message):
        pass

    def _selectNewMove(self, game_state: GameState):
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
