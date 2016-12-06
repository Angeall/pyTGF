from os import listdir, curdir
from os.path import isfile, join, splitext
import sys, inspect

from tkinter import *
from tkinter.ttk import *
from menu.basicframe import BasicFrameBuilder
import utils.gui


class AISelectorFrameBuilder(BasicFrameBuilder):
    NONE_STRING = "None"

    def __init__(self, title: str, parent: Tk, ai_type, ok_action, cancel_action, min_players=2, max_players=4,
                 players_description: dict=None):
        """
        Instantiates the builder
        Args:
            title: The title of the frame
            parent: The parent window on which the widgets was added
            ai_type: The AI class type to look for
            ok_action: The action performed when the Confirm button is pressed
            cancel_action: The action performed when the Cancel button is pressed
            min_players: The minimum number of players to play this game
            max_players: The maximum number of players to play this game
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
        self.maxPlayers = max_players
        self.okAction = ok_action
        self.selectedAIs = {}
        self.teamsSelection = {}
        self.cancelAction = cancel_action
        self.playersDescription = players_description

    def getSelection(self) -> tuple:
        """
        Returns:
            - The selection as a dictionary with player number as key and the selected controller class as value.
            - The teams for each players in a dictionary. Key : player number, Value : team number
        """
        return self.selectedAIs, self.teamsSelection

    def create(self) -> Frame:
        """
        Returns: The frame containing the selectors and the ok and cancel buttons
        """
        frame = super().create()
        for i in range(1, self.maxPlayers + 1):
            self._addSelector(frame, i)
        self._addButtons(frame)
        return frame

    def _setupControllerCombobox(self, combobox, player_number):
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
        combobox.bind("<<ComboboxSelected>>", lambda event: self._addControllerToSelection(player_number, combobox.get()))
        combobox.grid(column=1, row=0)

    def _setupTeamCombobox(self, combobox, player_number):
        values = ["Team " + str(team) for team in range(1, self.maxPlayers+1)]
        combobox['values'] = values
        combobox.set("Team " + str(player_number))
        self.teamsSelection[player_number] = player_number
        combobox.state(("readonly",))
        combobox.bind("<<ComboboxSelected>>", lambda event: self._addTeamToSelection(player_number, combobox.get()))
        combobox.grid(column=2, row=0)

    def _setupPlayerLabel(self, label, player_number):
        player_desc = "Player " + str(player_number)
        if self.playersDescription is not None and player_number in self.playersDescription.keys():
            player_desc += " (" + self.playersDescription[player_number] + ")"
        label['text'] = player_desc
        label['background'] = self.backgroundColor
        label['width'] = 30
        label.grid(column=0, row=0, padx=(0, 10))

    def _addControllerToSelection(self, player_number, class_name):
        """
        Reacts to a selection for a player and adds it to the selection
        Args:
            player_number:
            class_name:

        Returns:

        """
        if class_name != self.NONE_STRING:
            self.selectedAIs[player_number] = self.aiClasses[class_name]
        else:
            if player_number in self.selectedAIs.keys():
                del self.selectedAIs[player_number]

    def _addTeamToSelection(self, player_number, team_number):
        self.teamsSelection[player_number] = team_number

    def _addSelector(self, frame, player_number: int) -> None:
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
        path = list(sys.path)
        sys.path.insert(0, folder)

        for file in files:
            file_name = splitext(file)[0]
            try:
                module = __import__(file_name)
                for name, cls in inspect.getmembers(module):  # Explore the classes inside the file
                    if cls is not self._aiType:  # The basic type cannot be instantiated as it is
                        if inspect.isclass(cls) and issubclass(cls, self._aiType):
                            self.aiClasses[name] = cls
                            self.ais.append(name)
            except ImportError:
                continue

        sys.path[:] = path
        self.ais.insert(0, self.NONE_STRING)

    def _confirmSelection(self) -> None:
        """
        Put a frame around the action to perform when the OK button is pressed.
        It ensures that there is enough players selected to play
        """
        if len(self.selectedAIs) >= self.minPlayers:
            self.okAction()
        else:
            self._showNotEnoughPopup()

    def _addButtons(self, frame) -> None:
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
        utils.gui.center_popup(popup, self.parent)
