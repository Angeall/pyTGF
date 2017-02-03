from distutils.core import setup

setup(
    name='pyTGF',
    version='0.1.0',
    packages=['pytgf', 'pytgf.game', 'pytgf.menu', 'pytgf.test', 'pytgf.test.test_board', 'pytgf.test.test_controls',
              'pytgf.test.test_controls.linkers', 'pytgf.test.test_controls.controllers', 'pytgf.test.test_examples',
              'pytgf.test.test_characters', 'pytgf.test.test_characters.moves', 'pytgf.test.test_characters.units',
              'pytgf.board', 'pytgf.utils', 'pytgf.controls', 'pytgf.controls.events', 'pytgf.controls.linkers',
              'pytgf.controls.controllers', 'pytgf.examples', 'pytgf.examples.sokoban', 'pytgf.examples.sokoban.AIs',
              'pytgf.examples.sokoban.rules', 'pytgf.examples.sokoban.units', 'pytgf.examples.sokoban.parsing',
              'pytgf.examples.sokoban.controllers', 'pytgf.examples.lazerbike', 'pytgf.examples.lazerbike.rules',
              'pytgf.examples.lazerbike.units', 'pytgf.examples.lazerbike.control', 'pytgf.characters',
              'pytgf.characters.ai', 'pytgf.characters.moves', 'pytgf.characters.units'],
    url='https://github.com/Angeall/pyTGF',
    license='MIT',
    author='Anthony Rouneau',
    author_email='angeal1105@gmail.com',
    description='', requires=['multiprocess', 'pathos', 'pygame', 'matplotlib', 'numpy', 'scipy']
)
