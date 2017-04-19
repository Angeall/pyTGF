from distutils.core import setup

setup(
    name='pyTGF',
    version='',
    packages=['pytgf', 'pytgf.data', 'pytgf.data.decode', 'pytgf.data.routines', 'pytgf.data.benchmarking',
              'pytgf.game', 'pytgf.menu', 'pytgf.test', 'pytgf.test.test_data', 'pytgf.test.test_data.decode',
              'pytgf.test.test_board', 'pytgf.test.test_controls', 'pytgf.test.test_controls.wrappers',
              'pytgf.test.test_controls.controllers', 'pytgf.test.test_examples', 'pytgf.test.test_characters',
              'pytgf.test.test_characters.moves', 'pytgf.test.test_characters.units', 'pytgf.board',
              'pytgf.board.simulation', 'pytgf.utils', 'pytgf.controls', 'pytgf.controls.events',
              'pytgf.controls.wrappers', 'pytgf.controls.controllers', 'pytgf.examples', 'pytgf.examples.sokoban',
              'pytgf.examples.sokoban.res.AIs', 'pytgf.examples.sokoban.rules', 'pytgf.examples.sokoban.units',
              'pytgf.examples.sokoban.parsing', 'pytgf.examples.sokoban.controllers', 'pytgf.examples.connect4',
              'pytgf.examples.connect4.res.AIs', 'pytgf.examples.connect4.data', 'pytgf.examples.connect4.rules',
              'pytgf.examples.connect4.units', 'pytgf.examples.connect4.controllers', 'pytgf.examples.lazerbike',
              'pytgf.examples.lazerbike.res.AIs', 'pytgf.examples.lazerbike.data', 'pytgf.examples.lazerbike.rules',
              'pytgf.examples.lazerbike.units', 'pytgf.examples.lazerbike.control', 'pytgf.characters',
              'pytgf.characters.moves', 'pytgf.characters.units', 'pytgf.characters.utils'],
    url='https://github.com/Angeall/pyTGF',
    license='MIT',
    author='Anthony Rouneau',
    author_email='angeal1105@gmail.com',
    description='', requires=['multiprocess', 'pathos', 'pygame', 'matplotlib', 'numpy', 'scipy', 'pandas']
)
