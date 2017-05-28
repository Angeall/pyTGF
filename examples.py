"""\n
Welcome to the examples of pyTGF.

Usage:
  examples.py [--help] <command> [-h | --help | <args>...]

Options:
  -h --help         Show this screen.
  --version         Show the version.

Commands:
   connect4      Launch the Connect 4 example
   sokoban       Launch the Sokoban example
   lazerbike     Launch the TRON Lazerbike example
"""
from docopt import docopt

from pytgf.examples.connect4.main import launch_gui as launch_c4
from pytgf.examples.lazerbike.main import launch_gui as launch_lb
from pytgf.examples.sokoban.main import launch_gui as launch_sokoban

if __name__ == '__main__':
    arguments = docopt(__doc__, options_first=True, version='1.0.0')
    try:
        if arguments['<command>'] == 'connect4':
            launch_c4()
        elif arguments['<command>'] == 'sokoban':
            launch_sokoban()
        elif arguments['<command>'] == 'lazerbike':
            launch_lb()
        else:
            exit("%s is not a command. See 'examples.py --help'." % (arguments['<command>']))
    except KeyboardInterrupt:
        exit("Keyboard interrupt")