import os
from os.path import join
from typing import List

from pytgf.utils.code_gen import to_file_name, to_camel_case, create_module, write_file, CodeBlock

WAR_GAME = 0
DUEL_GAME = 1
PUZZLE_GAME = 2


class GameGenerator:
    def __init__(self, game_name: str, game_type: int, unit_names: List[str], turn_based: bool, width: int, height: int,
                 rows: int, columns: int, min_players: int, max_players: int, min_teams: int = 2, max_teams: int = 2,
                 suicide_allowed: bool = True, team_kill_allowed: bool = True):
        self.gameName = game_name
        self.gameDir = to_file_name(game_name)
        os.mkdir(self.gameDir)
        self.gameType = game_type
        self.turnBased = turn_based
        self.suicideAllowed = suicide_allowed
        self.teamKillAllowed = team_kill_allowed
        self.units = unit_names
        self.width = width
        self.height = height
        self.rows = rows
        self.columns = columns
        self.maxPlayers = max_players if game_type != DUEL_GAME else 2
        self.minPlayers = min_players if game_type != DUEL_GAME else 2
        self.minTeams = min(min_teams, self.minPlayers) if game_type != PUZZLE_GAME else 1
        self.maxTeams = min(max_teams, self.maxPlayers) if game_type != PUZZLE_GAME else 1

        self.rulesDir = join(self.gameDir, "rules")
        self.controllersDir = join(self.gameDir, "controllers")
        self.unitsDir = join(self.gameDir, "units")

        create_module(self.rulesDir)
        self.makeCore()
        self.makeAPI()
        create_module(self.controllersDir)
        self.makePlayer()
        self.makeWrappers()
        create_module(self.unitsDir)
        for unit_name in unit_names:
            self.makeUnit(unit_name, True, False)
        self.makeBuilder()
        self.makeMain()
        os.mkdir(join(self.gameDir, "res"))
        os.mkdir(join(self.gameDir, "res", "AIs"))

    def makeCore(self):
        imports = "from typing import Optional\nfrom pytgf.board import Tile, TileIdentifier, Board\n" \
                  "from pytgf.characters.units import Entity, Unit\nfrom pytgf.game.core import Core\n" \
                  "from pytgf.characters.moves import MoveDescriptor\n\n\n"
        init = ""
        suicide_property = CodeBlock("def _suicideAllowed(self) -> bool", ["return %s" % str(self.suicideAllowed)],
                                     ["@property"], [SUICIDE_ALLOWED_COMMENT])
        team_kill_property = CodeBlock("def _teamKillAllowed(self) -> bool", ["return %s" % str(self.teamKillAllowed)],
                                       ["@property"], [TEAM_KILL_ALLOWED_COMMENT])
        collide = CodeBlock("def _collidePlayers(self, player1: Unit, player2: Unit, tile_id: TileIdentifier,"
                            + "frontal: bool = False, entity: Optional[Entity] = None) -> None",
                            ["# FIXME if needed",
                             "return super()._collidePlayers(player1, player2, tile_id, frontal=frontal,"
                             "entity=entity)"], comment_lines=COLLIDE_COMMENTS)
        update_state = ""
        goal_reached = ""
        if self.gameType == PUZZLE_GAME:
            init = CodeBlock("def __init__(self, board: Board, ending_unit: Unit)",
                             ["super().__init__(board)",
                              "self._endingUnit = ending_unit  # type: Unit)"],
                             comment_lines=["Args:", "    ending_unit: The unit that will serve as opponent until the "
                                                     "goal of the game is reached"])
            goal_reached = CodeBlock("def goalReached(self) -> bool",
                                     ["# TODO Implement it",
                                      "raise NotImplementedError('Lack implementation for this game')"],
                                     comment_lines=["Returns: True if the goal of the game has been reached, "
                                                    "False otherwise"])
            if_goal_reached = CodeBlock("if self.goalReached()", ["self._endingUnit.setNbLives(0)"])
            update_state = CodeBlock("def updateGameState(self, unit: Unit, tile_id: TileIdentifier, "
                                     "move_descriptor: MoveDescriptor)",
                                     ["ret_val = super().updateGameState(unit, tile_id, move_descriptor)",
                                      if_goal_reached,
                                      "return ret_val"],
                                     comment_lines=["This method is called every time a unit reaches a new tile"])
        core_class = CodeBlock("class " + to_camel_case(self.gameName, True) + "Core(Core)",
                               [init, suicide_property, team_kill_property, collide, goal_reached, update_state],
                               comment_lines=[], class_level=True)
        code = imports + core_class.__str__()
        write_file(code, join(self.rulesDir, to_file_name(self.gameName) + "core.py"))

    def makeAPI(self):
        imports = "from pytgf.characters.moves import MoveDescriptor, Path\n" \
                  "from pytgf.characters.units import Unit\n" \
                  "from pytgf.board import Tile, TileIdentifier\nfrom pytgf.game import UnfeasibleMoveException\n"
        api_superclass = "API"
        if self.turnBased:
            api_superclass = "TurnBasedAPI"
            imports += "from pytgf.game.turnbased import TurnBasedAPI\n\n\n"
        else:
            imports += "from pytgf.game import API\n\n\n"

        move_gen = CodeBlock("def createMoveForDescriptor(self, unit: Unit, move_descriptor, force=False, is_step: "
                             "bool=False) -> Path",
                             ["# TODO ", "raise UnfeasibleMoveException('The event couldn\"t create a valid move')"],
                             comment_lines=CREATE_MOVE_COMMENTS)
        encode = CodeBlock("def _encodeMoveIntoPositiveNumber(self, player_number: int, "
                           "move_descriptor: MoveDescriptor) -> int",
                           ["# TODO", "raise NotImplementedError('Not yet implemented for this game')"],
                           comment_lines=ENCODE_COMMENTS)
        decode = CodeBlock("def _decodeMoveFromPositiveNumber(self, player_number: int, "
                           "encoded_move: int) -> MoveDescriptor",
                           ["# TODO", "raise NotImplementedError('Not yet implemented for this game')"],
                           comment_lines=DECODE_COMMENTS)
        api_class = CodeBlock("class " + to_camel_case(self.gameName, True) + "API(" + api_superclass + ")",
                              [move_gen, encode, decode],
                              comment_lines=[], class_level=True)
        code = imports + api_class.__str__()
        write_file(code, join(self.rulesDir, to_file_name(self.gameName) + "api.py"))

    def makePlayer(self):
        camel_case = to_camel_case(self.gameName, True)
        file_name = to_file_name(self.gameName)
        imports = "from abc import ABCMeta\nfrom typing import List\n\n" \
                  "from pytgf.characters.moves import MoveDescriptor\n" \
                  "from pytgf.controls.controllers import Controller, Bot\n\n" \
                  "from ..rules." + file_name + "api import " + camel_case + "API\n" \
                                                                             "from ..rules." + file_name + "core import " + camel_case + "Core\n"
        basic_player = CodeBlock("class " + camel_case + "Player(Controller, metaclass=ABCMeta)",
                                 ["pass"],
                                 comment_lines=["Defines the basic player for the " + self.gameName + "game"])

        possible_moves = CodeBlock("def possibleMoves(self) -> List[MoveDescriptor]",
                                   ["# FIXME if needed", "return []"], decorators=["@property"],
                                   comment_lines=["Returns: A list containing all the possible moves for this "
                                                  "controller if they can be listed."])

        get_api = CodeBlock("def _getGameStateAPI(self, game: " + camel_case + "Core) -> " + camel_case + "API",
                            ["return " + camel_case + "API(game)"], comment_lines=GAME_API_COMMENTS)

        is_move_interesting = CodeBlock("def _isMoveInteresting(self, player_number: int, "
                                        "new_move_event: MoveDescriptor) -> bool",
                                        ["#FIXME if needed", "return True"], comment_lines=MOVE_INTERESTING_COMMENTS)

        move_allowed = CodeBlock("def _isMoveAllowed(self, move: MoveDescriptor) -> bool",
                                 ["# FIXME if needed", "return move in self.possibleMoves"],
                                 comment_lines=MOVE_ALLOWED_COMMENTS)

        bot_player = CodeBlock("class " + camel_case + "BotPlayer(" + camel_case + "Player, Bot, metaclass=ABCMeta)",
                               [possible_moves, get_api, is_move_interesting, move_allowed],
                               comment_lines=["Defines the basic player for the " + self.gameName + "game"],
                               class_level=True)

        code = imports + basic_player.__str__() + "\n\n\n" + bot_player.__str__()
        write_file(code, join(self.controllersDir, "player.py"))

    def makeWrappers(self):
        imports = "from abc import ABCMeta\n\nfrom pytgf.characters.moves import MoveDescriptor\n" \
                  "from pytgf.controls.wrappers import ControllerWrapper, HumanControllerWrapper, BotControllerWrapper" \
                  "\n\n\n"

        camel_case = to_camel_case(self.gameName, True)

        move_allowed = CodeBlock("def isMoveDescriptorAllowed(self, move_descriptor: MoveDescriptor) -> bool",
                                 ["# FIXME if needed", "return True"], comment_lines=WRAPPER_MOVE_ALLOWED_COMMENTS)

        basic_wrapper = CodeBlock("class " + camel_case + "ControllerWrapper(ControllerWrapper, metaclass=ABCMeta)",
                                  [move_allowed], comment_lines=["Basic controller wrapper for this game"],
                                  class_level=True)

        bot_wrapper = CodeBlock("class " + camel_case + "BotControllerWrapper(BotControllerWrapper, " + camel_case +
                                "ControllerWrapper)", ["pass"], comment_lines=["Bot wrapper for this game"],
                                class_level=True)

        human_wrapper = CodeBlock("class " + camel_case + "HumanControllerWrapper(HumanControllerWrapper, " +
                                  camel_case + "ControllerWrapper)", ["pass"],
                                  comment_lines=["Human wrapper for this game"])
        code = imports + basic_wrapper.__str__() + bot_wrapper.__str__() + human_wrapper.__str__()
        write_file(code, join(self.controllersDir, "wrapper.py"))

    def makeUnit(self, unit_name: str, has_sprite: bool = False, is_entity: bool = False):
        superclass = "Entity" if is_entity else "Unit"
        imports = "from pytgf.characters.units import " + superclass + "\n"
        if has_sprite:
            imports += "from pytgf.characters.units.sprite import UnitSprite\n"
        imports += "\n\n"

        sprite = ""

        camel_case = to_camel_case(unit_name, True)

        if has_sprite:
            image_path = CodeBlock("def imageRelativePath(self) -> str",
                                   ["# TODO", "raise NotImplementedError('The image path is not set yet')"],
                                   ["@property"])
            sprite = CodeBlock("class " + camel_case + "Sprite(UnitSprite)",
                               [image_path], class_level=True)

        init = CodeBlock("def __init__(self, player_number: int, team_number: int, speed: int, graphics: bool=True)",
                         ["super().__init__(player_number, sprite=" + camel_case +
                          "Sprite(graphics), speed=speed)"])

        unit = CodeBlock("class " + camel_case + "(" + superclass + ")",
                         [init], class_level=True)

        code = imports + sprite.__str__() + unit.__str__()
        write_file(code, join(self.unitsDir, to_file_name(unit_name) + ".py"))

    def makeBuilder(self):
        camel_case = to_camel_case(self.gameName, True)
        file_name = to_file_name(self.gameName)
        main_loop_module, main_loop_class = ("turnbased", "TurnBasedMainLoop") \
            if self.turnBased else ("realtime", "RealTimeMainLoop")
        imports = "from typing import Tuple, Dict, Type, Optional\n\n" \
                  "from pytgf.board import Builder\nfrom pytgf.controls.controllers import Bot, Human\n" \
                  "from pytgf.game." + main_loop_module + " import " + main_loop_class + "\n\n" \
                  "from .controllers.wrapper import " + camel_case + "BotControllerWrapper, " \
                  + camel_case + "HumanControllerWrapper\n" \
                  "from .rules." + file_name + "core" + " import " + camel_case + "Core\n" + \
                  "from .rules." + file_name + "api" + " import " + camel_case + "API\n"

        for unit in self.units:
            unit_file_name = to_file_name(unit)
            unit_camel_case = to_camel_case(unit, True)
            imports += "from .%s.%s import %s\n" % ("units", unit_file_name, unit_camel_case)
        imports += "\n\n"

        if_bot = CodeBlock("if issubclass(player_class, Bot)",
                           ["wrapper = %sBotControllerWrapper(player_class(player_number))" % camel_case])
        if_human = CodeBlock("elif issubclass(player_class, Human)",
                             ["wrapper = %sHumanControllerWrapper(player_class(player_number))" % camel_case])
        else_ = CodeBlock("else",
                          ["raise TypeError(\"The type of the player (\'%s\') must either be a Bot or a "
                           "Human subclass.\" % (str(player_class)))"])
        add_controller = CodeBlock("def add_controller(main_loop: %s, player_class, "
                                   "player_number: int, player_team: int, speed: int,"
                                   "graphics: bool)" % main_loop_class,
                                   [if_bot, if_human, else_,
                                    "main_loop.addUnit(# TODO instantiate the wanted unit",
                                    "        wrapper, start_position, initial_action, team=player_team)"])

        controllers_loop = CodeBlock("for player_number, player_class in player_classes.items()",
                                     ["add_controller(main_loop, player_class, player_number, "
                                      "player_teams[player_number], int(speed), graphics)"])

        create_game = CodeBlock("def create_game(player_info: Tuple[Dict[int, Type], Dict[int, int]], width: int=%s, "
                                "height: int=%s, rows: int=%s, columns: int=%s, speed: int=1, "
                                "graphics: bool=True)" % (str(self.width), str(self.height), str(self.rows),
                                                          str(self.columns)),
                                ["builder = Builder(width, height, rows, columns)",
                                 "builder.setBordersColor((0, 125, 125))",
                                 "builder.setBackgroundColor((25, 25, 25))",
                                 "builder.setTilesVisible(False)",
                                 "board = builder.create()",
                                 "",
                                 "game = %sCore(board)" % camel_case,
                                 "main_loop = %s(%sAPI(game))" % (main_loop_class, camel_case),
                                 "player_classes = player_info[0]",
                                 "player_teams = player_info[1]",
                                 "",
                                 controllers_loop])

        code = imports + add_controller.__str__() + "\n\n" + create_game.__str__()
        write_file(code, join(self.gameDir, "builder.py"))

    def makeMain(self):
        camel_case = to_camel_case(self.gameName, True)
        imports = "from tkinter import Tk\nfrom tkinter.ttk import Frame, Label, Button\nimport pygame\n" \
                  "from pytgf.menu import AISelectorFrameBuilder, ButtonFrameBuilder, GUI\n\n" \
                  "from .builder import create_game\nfrom .%s.player import %sPlayer\n\n\n" \
                  % ("controllers", camel_case)
        global_vars = "selection_frame = None  # type: Frame\nmain_frame = None\n\n\n"

        get_selection_frame = CodeBlock("def get_selection_frame() -> Frame",
                                        ["return selection_frame"])

        build_main_frame = CodeBlock("def build_main_frame(window: Tk, gui: GUI) -> Frame",
                                     ["global main_frame",
                                      "builder = ButtonFrameBuilder(\"%s\", window)" % self.gameName,
                                      "builder.setTitleColor(\"#FF0000\")",
                                      "builder.addButton((\"Play\", lambda: gui.goToFrame(get_selection_frame())))",
                                      "builder.addButton((\"Quit\", gui.quit))",
                                      "main_frame = builder.create()",
                                      "return main_frame"], comment_lines=["Build the GUI of the game"])

        build_selection_frame = CodeBlock("def build_selection_frame(window: Tk, gui: GUI) -> Frame",
                                          ["global selection_frame",
                                           "builder = AISelectorFrameBuilder(\"Player selection\", window, " +
                                           "%sPlayer," % camel_case,
                                           "lambda: launch_game(gui, builder.getSelection()), gui.goToPreviousFrame, "
                                           "max_teams=%s, min_teams=%s, players_description={1: ''})"
                                           % (str(self.maxTeams), str(self.minTeams)),
                                           "selection_frame = builder.create()",
                                           "return selection_frame"])

        end_popup = CodeBlock('def end_popup(string_result)',
                              ["popup = Tk()",
                               "popup.title('Game finished')",
                               "label = Label(popup, text=string_result)",
                               "label.grid(row=0, column=0, columnspan=4)",
                               "button1 = Button(text=\"Play again\", command=lambda: relaunch_gui(popup), width=15)",
                               "button1.grid(row=1, column=1)",
                               "button2 = Button(text=\"Quit\", command=popup.destroy, width=15)",
                               "button2.grid(row=1, column=2)"])

        if_results = CodeBlock("if result is None", ["return"])
        elif_results = CodeBlock("elif len(result) == 0", ["string_result = \"DRAW\""])
        else_results = CodeBlock("else",
                                 ['winning_players_strings = ["Player " + str(player.playerNumber) '
                                  'for player in result]',
                                  'string_result = "WON: " + str(winning_players_strings)'])

        launch_game = CodeBlock("def launch_game(gui: GUI, player_info: tuple)",
                                ["gui.quit()",
                                 "pygame.init()",
                                 "",
                                 "main_loop = create_game(player_info)",
                                 "",
                                 "result = main_loop.run()",
                                 if_results,
                                 elif_results,
                                 else_results,
                                 "end_popup(string_result)"])

        relaunch_gui = CodeBlock("def relaunch_gui(window)", ["pygame.quit()", "window.destroy()", "launch_gui()"])

        launch_gui = CodeBlock("def launch_gui()",
                               ["window = Tk()",
                                "gui = GUI(\"%s\", window)" % self.gameName,
                                "gui.addFrame(build_main_frame(window, gui))",
                                "gui.addFrame(build_selection_frame(window, gui))",
                                "gui.mainloop()"])

        main = CodeBlock("if __name__ == \"__main__\"", ["launch_gui()"], class_level=True)

        code = imports + global_vars + get_selection_frame.__str__() + "\n\n" + build_main_frame.__str__() + "\n\n" + \
            build_selection_frame.__str__() + "\n\n" + end_popup.__str__() + "\n\n" + launch_game.__str__() + "\n\n" \
               + relaunch_gui.__str__() + "\n\n" + launch_gui.__str__() + "\n\n" + main.__str__()

        write_file(code, join(self.gameDir, "main.py"))


SUICIDE_ALLOWED_COMMENT = 'Returns: Whether the game must kill a unit colliding on its own entities'
TEAM_KILL_ALLOWED_COMMENT = 'Returns: Whether the game must kill two units from the same team if they collide with' \
                            + 'each other'
COLLIDE_COMMENTS = ["Handle the case where the first given player collides with an entity of the second given player",
                    "(Careful : two moving units (alive units) colliding each other cause a frontal collision that",
                    "hurts both units)", "",
                    "Args:",
                    "    player1: The first given player",
                    "    player2: The second given player",
                    "    frontal: If true, the collision is frontal and kills the two players",
                    "    entity: Optionally the entity causing the collision"]

CREATE_MOVE_COMMENTS = ["Creates a move following the given event coming from the given unit",
                        "",
                        "Args:",
                        "   unit: The unit that triggered the event",
                        "   move_descriptor: The descriptor of the move triggered by the given unit",
                        "   force: Optional, a bot controller will force the move as it does not need to "
                        "check if the move is possible",
                        "   is_step:",
                        "       Optional, True indicates that the move will serve to perform a step in an API.",
                        "       It can be ignored if the moves do not differ from a step or from a complete move",
                        "",
                        "Returns: A Path of move(s) triggered by the given event for the given unit",
                        "",
                        "Raises:",
                        "   UnfeasibleMoveException: If the move is not possible."]

DECODE_COMMENTS = ["Decode the given encoded move into a correct move descriptor.",
                   "",
                   "Args:",
                   "    player_number: The number representing the player that could perform the move.",
                   "    encoded_move: The positive integer representing an encoded move (to be decoded..)",
                   "",
                   "Returns:",
                   "    The decoded move, hence a correct move descriptor for the given player",
                   "    (does not check if the move is feasible)."]

ENCODE_COMMENTS = ["Encode a move to be performed (hence, this API must be in a state where the "
                   "move represented by the descriptor",
                   "has not yet been performed !)",
                   "",
                   "Args:",
                   "    player_number: The number representing the player that could perform the move",
                   "    move_descriptor: The descriptor of the move to be performed by the given player",
                   "",
                   "Returns: A positive integer that represents the move descriptor"]

GAME_API_COMMENTS = ["Get the API specific to this game",
                     "",
                     "Args:",
                     "  game: The game core that the API will use",
                     "",
                     "Returns: The specific API"]

MOVE_INTERESTING_COMMENTS = ["Args:",
                             "    player_number: The player that performs the given move",
                             "    new_move_event: The descriptor of the performed move",
                             "",
                             "Returns: True if the given move must trigger a new move selection from this controller"]

MOVE_ALLOWED_COMMENTS = ["Args:",
                         "    move: The descriptor of the wanted move",
                         "",
                         "Returns: True if the given move descriptor is allowed by the game"]

WRAPPER_MOVE_ALLOWED_COMMENTS = ["Args:",
                                 "    move_descriptor: The descriptor of the move that will be analysed by this method",
                                 "",
                                 "Returns: True if the given move description is allowed by the game."]
