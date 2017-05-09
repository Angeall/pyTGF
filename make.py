"""\n
pyTGF game maker

Usage:
  make.py [--help] NAME TYPE ROWS COLUMNS [options] [ --unit UNIT_NAME ]...
  
Arguments:
  NAME            Defines the name of the game to create
  TYPE            Defines the type of the game to create (0: War, 1: Duel, 2: Puzzle)
  ROWS            Defines the number of rows in the game board
  COLUMNS         Defines the number of columns in the game board

Options:
  -h --help               Show this screen.
  --version               Show the version.
  -t --turn               Sets the game turn based
  --width INT             Defines the width of the Frame in which the game will run [Default: 720]
  --height INT            Defines the height of the Frame in which the game will run [Default: 480]
  --unit STR              Defines the name of a new unit to create in the game
  --min-players INT       Defines the minimum number of players needed to launch the game [Default: 2]
  --max-players INT       Defines the maximum number of players needed to launch the game [Default: 4]
  --min-teams INT         Defines the minimum number of teams needed to launch the game [Default: 2]
  --max-teams INT         Defines the maximum number of teams needed to launch the game [Default: 4]
  --suicide INT           Defines if the game must accept suicidal moves (1) or not (0) [Default: 1]
  --teamkill INT          Defines if the game must accept team kills (1) or not (0) [Default: 1]  
"""
from docopt import docopt

from pytgf.gen.generate_new_game import GameGenerator

if __name__ == '__main__':
    args = docopt(__doc__, version='1.0.0')
    try:
        gen = GameGenerator(args['NAME'], int(args['TYPE']), args['--unit'], bool(int(args['--turn'])),
                            int(args['--width']), int(args['--height']), int(args['ROWS']), int(args['COLUMNS']),
                            int(args['--min-players']), int(args['--max-players']), int(args['--min-teams']),
                            int(args['--max-teams']), bool(int(args['--suicide'])), bool(int(args['--teamkill'])))
        pass
    except KeyboardInterrupt:
        exit("Keyboard interrupt")