# List of tasks to do

## Data Generation

- Create an abstract data generation algorithm + implement it to get the current algorithms (Throughout and Random). 
- Create a battle-based data generation algorithm implementing the abstract one.

## Game engine

- Add "laps" between actions. Real time = one lap for every controller. Turn-based = one lap per player
- Divide API and Core into Abstract/RealTime/TurnBased API and Core.
- Add a time limit to the Bots => fire warning when bot exceeded the limit.
- Fix the "can't quit the game" problem when exiting the `pygame` window while the `tkinter` end window is opened
- Generalize the game creation

## Examples

- Add comments
- Add a setting feature to Sokoban: Select the board

## Package management

- Structure the `data` package
- Delete the `ai` package

## GUI

- Add an optional settings page (as a button beneath the launch game button)