[![Codacy Badge](https://api.codacy.com/project/badge/Grade/21237f5f264c491186ee7c8ab9762f82)](https://www.codacy.com/app/angeal1105/pyTGF?utm_source=github.com&utm_medium=referral&utm_content=Angeall/pyTGF&utm_campaign=badger) [![Build Status](https://travis-ci.org/Angeall/pyTGF.svg?branch=master)](https://travis-ci.org/Angeall/pyTGF)

# PyTGF - Tile Game Framework

## Context
 - This module was made in the context of a master's thesis made at the University of Mons
  (UMONS) for a Master degree in Computer Sciences.
 - The project was made under the direction of the Professor Tom Mens.

### Goal
 The goal of this solution is to provide a stable framework to test AIs on grid-based games. 
 These games can optionally be cooperative, as the controllers can send messages to each others. 

## Dependencies

 - [`Python 3.x`](https://www.python.org/downloads/)
 - [`Pygame`](https://pypi.python.org/pypi/Pygame/)
 - [`Numpy`](https://pypi.python.org/pypi/numpy/)
 - [`Scipy`](https://pypi.python.org/pypi/scipy/)
 - [`Pathos`](https://pypi.python.org/pypi/pathos/)
 - [`Matplotlib`](https://pypi.python.org/pypi/matplotlib/)
 - [`Pandas (required for the data module)`](https://pypi.python.org/pypi/pandas/) 
 - [`Docopt`](https://pypi.python.org/pypi/docopt/)

## Examples
 Three examples have been developed with this framework. They are located in the `examples` package:
  
  - Lazerbike: A TRON-like game, where multiple bikes try to win upon its opponents by blocking them with their 
    lasers tray
  - Sokoban: A puzzle game where one or multiple players must push boxes into holes in order to reach a
    common destination
  - Connect 4: The well-known grid game in which two players fight to place 4 discs in a row on a 6x7 grid board.
  
### Run the examples
 To run the examples, just run the `examples.py` file followed by one of the three commands below:
  - `lazerbike`
  - `sokoban`
  - `connect4`
  
## Creating a new game
 A script has ben written in order to help users to create a new game. This script creates all the files
 needed to implement a new game, and leaves TODOs and FIXMEs in the code to indicate where the code
 must be adapted to implement the game.
 
 To launch this script, just run the `make.py` file followed by the required arguments. These can be
 listed using `--help` when launching the script.