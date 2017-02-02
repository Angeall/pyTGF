import unittest
from typing import Tuple, List

from multiprocess.connection import Pipe
from multiprocess.connection import PipeConnection

from pytgf.board import Builder
from pytgf.characters.moves import Path
from pytgf.characters.units import MovingUnit
from pytgf.controls.controllers import Bot
from pytgf.controls.events import BotEvent, SpecialEvent
from pytgf.controls.linkers.bot import BotLinker
from pytgf.game import Game, UnfeasibleMoveException, GameState

MOVE1 = "MOVE1"
MOVE2 = "MOVE2"
MSG1 = "DO_MOVE1"
MSG2 = "DO_MOVE2"


class ExampleBotLinker(BotLinker):
    def isMoveDescriptorAllowed(self, move_descriptor) -> bool:
        return type(move_descriptor) == str and move_descriptor[0:4] == 'MOVE'


class ExampleAPI(GameState):
    def __init__(self, game: Game):
        super().__init__(game)
        self.move1 = 0
        self.move2 = 0

    def isItOneTestMethod(self):
        if isinstance(self.game, ExampleGame):
            return True
        return False

    def performMove1(self):
        self.move1 += 1

    def performMove2(self):
        self.move2 += 1


class ExampleGame(Game):
    @property
    def _teamKillAllowed(self) -> bool:
        return False

    @property
    def _suicideAllowed(self) -> bool:
        return False

    def createMoveForDescriptor(self, unit: MovingUnit, move_descriptor, max_moves: int = -1,
                                force: bool = False) -> Path:
        raise UnfeasibleMoveException()

    def _collidePlayers(self, player1, player2, frontal: bool = False):
        pass


class ExampleBot(Bot):
    def _getGameStateAPI(self, game: Game):
        return ExampleAPI(game)

    def reactToEvents(self, events: List[BotEvent]):
        for event in events:

            new_move_event = event.moveDescriptor
            if new_move_event == MOVE1:
                self.gameState.performMove1()
            elif new_move_event == MOVE2:
                self.gameState.performMove2()
        return super().reactToEvents(events)

    def _isMoveInteresting(self, player_number: int, new_move_event) -> bool:
        return True

    def _isMoveAllowed(self, move: str) -> bool:
        if type(move) == str and move[0:4] == 'MOVE':
            return True
        return False

    def selectMoveFollowingTeammateMessage(self, teammate_number: int, message):
        if message == MSG1:
            return MOVE1
        elif message == MSG2:
            return MOVE2

    def _selectNewMove(self, game_state: ExampleAPI):
        return "MOVE1-" + str(game_state.move1) + '/' + "MOVE2-" + str(game_state.move2)


class TestBotLinker(unittest.TestCase):
    def setUp(self):
        self.game = ExampleGame(Builder(10, 10, 7, 6).create())
        self.game.addUnit(MovingUnit(1), 1, (0, 0))
        self.bot1 = ExampleBot(1)
        self.bot1.gameState = self.game.copy()
        self.linker1 = ExampleBotLinker(self.bot1)
        self.game.addUnit(MovingUnit(2), 1, (0, 0))
        self.bot2 = ExampleBot(2)
        self.bot2.gameState = self.game.copy()
        self.linker2 = ExampleBotLinker(self.bot2)
        self.game_info_pipe_parent1, self.game_info_pipe_child1 = Pipe()  # type: Tuple[PipeConnection, PipeConnection]
        self.game_info_pipe_parent2, self.game_info_pipe_child2 = Pipe()  # type: Tuple[PipeConnection, PipeConnection]
        self.move_pipe_parent1, self.move_pipe_child1 = Pipe()  # type: Tuple[PipeConnection, PipeConnection]
        self.move_pipe_parent2, self.move_pipe_child2 = Pipe()  # type: Tuple[PipeConnection, PipeConnection]
        self.linker1.setMainPipe(self.move_pipe_child1)
        self.linker1.setGameInfoPipe(self.game_info_pipe_child1)
        self.linker2.setMainPipe(self.move_pipe_child2)
        self.linker2.setGameInfoPipe(self.game_info_pipe_child2)
        self.collaboration_pipe_1, self.collaboration_pipe_2 = Pipe()
        self.linker1.addCollaborationPipe(2, self.collaboration_pipe_1)
        self.linker2.addCollaborationPipe(1, self.collaboration_pipe_2)

    def test_invalid_type_sent(self):
        """
        Tests that the linker raises an error when a message that is not a "BotEvent" is sent
        """
        self.move_pipe_parent1.send("")
        self.assertRaises(TypeError, self.linker1._routine, self.game_info_pipe_child1, self.move_pipe_child1)

    def test_send_move(self):
        """
        Tests that moves are sent correctly, that they affect the GameState and that the AI responds well
        """
        move1_event = BotEvent(1, MOVE1)
        move2_event = BotEvent(1, MOVE2)
        self.move_pipe_parent1.send(move1_event)
        self.move_pipe_parent1.send(move1_event)
        self.move_pipe_parent1.send(move1_event)
        self.move_pipe_parent1.send(move2_event)
        self.linker1._routine()
        self.assertFalse(self.move_pipe_parent1.poll())
        self.linker1._routine()
        self.assertTrue(self.move_pipe_parent1.poll())
        self.assertEqual(self.move_pipe_parent1.recv(), "MOVE1-3/MOVE2-1")

    def test_send_message_to_teammate(self):
        """
        Tests that messages are sent well between two teammates
        """
        self.bot1.sendMessageToTeammate(2, MSG1)
        self.linker1._routine()  # Will send the message
        self.linker2._routine()  # Will receive the message
        self.assertTrue(self.move_pipe_parent2.poll())
        self.assertEqual(self.move_pipe_parent2.recv(), "MOVE1")

    def test_send_end_event(self):
        """
        Checks if the linker's logical loop ends correctly when it receives the end event
        """
        self.game_info_pipe_parent1.send(SpecialEvent(SpecialEvent.END))
        self.linker1.run()
        # Should run indefinitely if no flag was sent
        self.assertTrue(True)

    def test_unit_dead(self):
        """
        Checks if the linker blocks the incoming message of a dead unit, and starts to send again when resurrected
        """
        self.game_info_pipe_parent1.send(SpecialEvent(SpecialEvent.UNIT_KILLED))
        self.move_pipe_parent1.send(BotEvent(1, MOVE1))
        self.linker1._routine()
        self.assertFalse(self.move_pipe_parent1.poll())
        self.linker1._routine()  # Message blocked
        self.assertFalse(self.move_pipe_parent1.poll())
        self.game_info_pipe_parent1.send(SpecialEvent(SpecialEvent.RESURRECT_UNIT))
        self.move_pipe_parent1.send(BotEvent(1, MOVE2))
        self.linker1._routine()  # Message received
        self.linker1._routine()  # Message sent
        self.assertTrue(self.move_pipe_parent1.poll())
        # The message "MOVE1" was correctly received while the unit was dead => the game state is updated
        # while the unit is dead
        self.assertEqual(self.move_pipe_parent1.recv(), "MOVE1-1/MOVE2-1")
