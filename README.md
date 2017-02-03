[![Codacy Badge](https://api.codacy.com/project/badge/Grade/21237f5f264c491186ee7c8ab9762f82)](https://www.codacy.com/app/angeal1105/pyTGF?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Angeall/pyTGF&amp;utm_campaign=Badge_Grade) [![Build Status](https://travis-ci.org/Angeall/pyTGF.svg?branch=master)](https://travis-ci.org/Angeall/pyTGF)

# PyTGF - Tile Game Framework

## Context
 - This module was made in the context of a master's thesis made at the University of Mons
  (UMONS) for a Master degree in Computer Sciences.
 - The project was made under the direction of the Professor Tom Mens.

## Goal
 The goal of this solution is to provide a stable framework to test AIs on tile-based games. 
 These games can optionally be cooperative, as the controllers can send messages to each others. 

## Dependencies

 - [`Python 3.x`](https://www.python.org/downloads/)
 - [`Pygame`](https://pypi.python.org/pypi/Pygame/)
 - [`Numpy`](https://pypi.python.org/pypi/numpy/)
 - [`Scipy`](https://pypi.python.org/pypi/scipy/)
 - [`Pathos`](https://pypi.python.org/pypi/pathos/)
 - [`Matplotlib`](https://pypi.python.org/pypi/matplotlib/)

## Examples
 Two examples have been developed with this framework. They are located in the `examples` package:
  
  - Lazerbike: A TRON-like game, where multiple bikes try to win upon its opponents by blocking them with their 
    lasers tray
  - Sokoban: A puzzle game where one or multiple players must push boxes into holes in order to reach a
    common destination
