"""
File containing the definition of ta builder of a AI Selection Frame
"""

import inspect
import pickle
import traceback
from os import listdir
from os.path import isfile, join, splitext
from tkinter import *
from tkinter.ttk import *
from typing import Callable, Dict, Tuple

import pytgf.utils.gui
from pytgf.controls.controllers import Controller
from pytgf.menu.basicframe import BasicFrameBuilder


class AISelectorFrameBuilder(BasicFrameBuilder):
    """
    Defines the Builder of a Frame in which we can select the controller type of each player
    """

    NONE_STRING = "None"
    CONFIG_FILE_NAME = "config.bin"
    TEAM_STRING = "Team "
    PLAYER_STRING = "Player "

    def __init__(self, title: str, parent: Tk, ai_type, ok_action: Callable[[], None],
                 cancel_action: Callable[[], None], min_players: int=2, max_players: int=4, min_teams: int=2,
                 max_teams: int=4, players_description: dict=None):
        """
        Instantiates the builder
        Args:
            title: The title of the frame
            parent: The parent window on which the widgets was added
            ai_type: The AI class type to look for
            ok_action: The action performed when the Confirm button is pressed
            cancel_action: The action performed when the Cancel button is pressed
            min_players: The minimum number of players required to play this game
            max_players: The maximum number of players allowed to play this game
            min_teams: The minimum number of teams required to play this game
            max_teams: The maximum number of teams allowed to play this game (1 = no teams)
            players_description:
                An optional dictionary containing additional information to display for the players.
                Keys: player numbers. Values: additional description
        """
        super().__init__(title, parent)
        self.selectors = []
        self.ais = None
        self.aiClasses = None
        self._aiType = ai_type
        self.minPlayers = min_players
        self.minTeams = min_teams
        self.maxPlayers = max_players
        self.maxTeams = max_teams
        self.okAction = ok_action
        self.selectedAIs = {}
        self.selectedTeams = {}
        self._aiSelectors = []
        self._teamSelectors = []
        self.cancelAction = cancel_action
        self.playersDescription = players_description

    # -------------------- PUBLIC METHODS -------------------- #

    def getSelection(self) -> Tuple[Dict[int, Controller], Dict[int, int]]:
        """
        Returns:

            - The selection as a dictionary with player number as key and the selected controller class as value.
            - The teams for each players in a dictionary. Key : player number, Value : team number
        """
        return self.selectedAIs, self.selectedTeams

    def create(self) -> Frame:
        """
        Returns: The frame containing the selectors and the ok and cancel buttons
        """
        frame = super().create()
        for i in range(1, self.maxPlayers + 1):
            self._addSelector(frame, i)
        self._addButtons(frame)
        self._loadInstance()
        return frame

    # -------------------- PROTECTED METHODS -------------------- #

    def _saveInstance(self) -> None:
        """
        Serializes the selection into a file
        """
        lst = [self.selectedAIs, self.selectedTeams]
        file = open(self.CONFIG_FILE_NAME, mode="bw")
        pickle.dump(lst, file)

    def _loadInstance(self) -> None:
        """
        Load a serialized file (if there is one) containing the selection
        """
        try:
            file = open(self.CONFIG_FILE_NAME, mode="br")
            lst = pickle.load(file)
            self.selectedAIs = lst[0]
            self.selectedTeams = lst[1]
            self._updateSelection()
        except FileNotFoundError:
            pass
        except ImportError:
            pass

    def _updateSelection(self) -> None:
        """
        Updates the values in the combobox's using self.selectedAIs and self.selectedTeams
        """
        for player_number in self.selectedAIs:
            self._aiSelectors[player_number-1].set(self.selectedAIs[player_number].__name__)

        for player_number in self.selectedTeams:
            self._teamSelectors[player_number-1].set(self.TEAM_STRING + str(self.selectedTeams[player_number]))

    def _setupControllerCombobox(self, combobox: Combobox, player_number: int) -> None:
        """
        Setups the combobox so it displays the different controllers available
        Args:
            combobox: The combobox to setup
            player_number: The player for which the combobox is being set up
        """
        if self.ais is None:
            self._lookForAIs()
        combobox['values'] = self.ais
        combobox.set(self.NONE_STRING)
        combobox.state(("readonly",))
        combobox.bind("<<ComboboxSelected>>", lambda event: self._addControllerToSelection(player_number,
                                                                                           combobox.get()))
        combobox.grid(column=1, row=0)
        self._aiSelectors.append(combobox)

    def _setupTeamCombobox(self, combobox, player_number) -> None:
        """
        Sets the team selection combobox

        Args:
            combobox: The combobox to setup
            player_number: The player number for which we want to setup the combobox
        """
        values = [self.TEAM_STRING + str(team) for team in range(1, self.maxPlayers+1)]
        combobox['values'] = values
        combobox.set(self.TEAM_STRING + str(player_number))
        self.selectedTeams[player_number] = player_number
        combobox.state(("readonly",))
        combobox.bind("<<ComboboxSelected>>",
                      lambda event: self._addTeamToSelection(player_number, int(combobox.get().split(" ")[1])))
        combobox.grid(column=2, row=0)
        self._teamSelectors.append(combobox)

    def _setupPlayerLabel(self, label: Label, player_number) -> None:
        """
        Sets the player description correctly

        Args:
            label: The label to setup for the given player
            player_number: The number representing the player for which we want to set the label
        """
        player_desc = self.PLAYER_STRING + str(player_number)
        if self.playersDescription is not None and player_number in self.playersDescription.keys():
            player_desc += " (" + self.playersDescription[player_number] + ")"
        label['text'] = player_desc
        label['background'] = self.backgroundColor
        label['width'] = 30
        label.grid(column=0, row=0, padx=(0, 10))

    def _addControllerToSelection(self, player_number: int, class_name: type) -> None:
        """
        Reacts to a selection for a player and adds it to the selection

        Args:
            player_number: The player that selected a new controller
            class_name: The name of the selected controller
        """
        if class_name != self.NONE_STRING:
            self.selectedAIs[player_number] = self.aiClasses[class_name]
        else:
            if player_number in self.selectedAIs.keys():
                del self.selectedAIs[player_number]

    def _addTeamToSelection(self, player_number: int, team_number: int) -> None:
        """
        Reacts when a new team is selected for the given player

        Args:
            player_number: The number representing the player that selected the team
            team_number: The number of the newly selected team
        """
        self.selectedTeams[player_number] = team_number

    def _addSelector(self, frame: Frame, player_number: int) -> None:
        """
        Add a selector for the given player to the given frame

        Args:
            frame: The frame to which the selector will be added
            player_number: The number of the player for which add the selector
        """
        container = Frame(frame, style=self.FRAME_STYLE)
        label = Label(container)
        self._setupPlayerLabel(label, player_number)
        combo_controller = Combobox(container, width=20)
        combo_team = Combobox(container)
        self._setupControllerCombobox(combo_controller, player_number)
        if self.maxTeams > 1:
            self._setupTeamCombobox(combo_team, player_number)

        container.grid(row=player_number + 2, column=1)

    def _lookForAIs(self) -> None:
        """
        Look into the "AIs" folder for compatibles AIs or Human controllers and fill *self.ais*
        """
        folder = "AIs"
        files = [f for f in listdir(folder) if isfile(join(folder, f))]
        self.ais = []
        self.aiClasses = {}
        sys.path.insert(0, folder)
        for file in files:
            file_name = splitext(file)[0]
            try:
                module = __import__(file_name)
                for name, cls in inspect.getmembers(module):  # Explore the classes inside the file
                    if inspect.isclass(cls):
                        if not inspect.isabstract(cls):  # The abstract type cannot be instantiated as it is
                            if issubclass(cls, self._aiType):
                                self.aiClasses[name] = cls
                                self.ais.append(name)
            except ImportError:
                print("Error while listings AIs:")
                traceback.print_exc()
                continue

        self.ais.insert(0, self.NONE_STRING)

    def _confirmSelection(self) -> None:
        """
        Put a frame around the action to perform when the OK button is pressed.
        It ensures that there is enough players selected to play
        """
        if len(self.selectedAIs) < self.minPlayers:
            self._showNotEnoughPopup()
        elif self.maxTeams > 1:
            different_teams = []
            for ai in self.selectedAIs:
                team_number = self.selectedTeams[ai]
                if team_number not in different_teams:
                    different_teams.append(team_number)
            if self.minTeams > len(different_teams) or len(different_teams) > self.maxTeams:
                self._showIncorrectTeamsPopup()
            else:
                self._saveInstance()
                self.okAction()
        else:
            self._saveInstance()
            self.okAction()

    def _addButtons(self, frame: Frame) -> None:
        """
        Adds the OK and the Cancel button to the bottom of the selectors
        Args:
            frame: The frame to which add the buttons
        """
        ok_button = Button(frame, text="OK", command=self._confirmSelection)
        cancel_button = Button(frame, text="Cancel", command=self.cancelAction)
        ok_button.grid(row=self.maxPlayers+3, column=1, pady=(40, 0))
        cancel_button.grid(row=self.maxPlayers+4, column=1, pady=(5, 0))

    def _showNotEnoughPopup(self) -> None:
        """
        Displays a popup that announces to the user that there is not enough players selected.
        """
        popup = Toplevel(self.parent)
        popup.transient(self.parent)
        popup.resizable(False, False)
        label = Label(popup, text="Not enough players selected. The minimum number of players is " +
                                  str(self.minPlayers))
        label.grid(row=0, column=0, columnspan=3)
        bt = Button(popup, text="OK", command=popup.destroy)
        bt.grid(row=1, column=1)
        pytgf.utils.gui.center_popup(popup, self.parent)

    def _showIncorrectTeamsPopup(self):
        """
        Displays a popup that announces to the user that there is not a correct number of teams selected.
        """
        popup = Toplevel(self.parent)
        popup.transient(self.parent)
        popup.resizable(False, False)
        label = Label(popup, text="The number of teams selected is incorrect. The number of teams must be between " +
                                  str(self.minTeams) + " and " + str(self.maxTeams))
        label.grid(row=0, column=0, columnspan=3)
        bt = Button(popup, text="OK", command=popup.destroy)
        bt.grid(row=1, column=1)
        pytgf.utils.gui.center_popup(popup, self.parent)
