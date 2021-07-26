# Chess Tournament/Playground

This repository is a collection of chess strategies, as well as a small framework for playing against them in the python interactive mode.

These strategies are largely inspired by [Tom 7's various chess shenanigans](tom7.org/chess). After watching his Elo World video, I wanted to play against some of the chess players myself, but didn't feel like figuring out how to compile his C++ code and get all that working. So rather, I decided to reimplement parts of it in Python and use nice pre-existing libraries to do the heavy lifting.

## The Strategies

Name | Description | Properties
--- | --- | ---
RandomMove | Just picks a move at random
MinResponses | Picks a move that minimizes the amount of responses that the opponent will have
SuicideKing | Tries to move its king as close as possible to the enemy king
Stockfish | Plays moves from the [Stockfish](https://stockfishchess.org/) engine, by default at depth 18 | *Engine*
GnuChess | Plays moves from the [GNU Chess](https://www.gnu.org/software/chess/) engine in UCI mode, by default at depth 10 | *Engine*
Worstfish | Uses Stockfish at depth 10 to play the worst possible move | *Engine*
LightSquares | Prefers moving its pieces onto light squares
DarkSquares | Same as above but for dark squares
Equalizer | Will move the piece that has moved the least number of times onto a square that has been visited the least number of times. Fewer moves takes priority over less visited squares | *Stateful*

## How to use the framework

### Prerequisites

I've tested this with python3. It might work with python2, idk ¯\\\_(ツ)\_/¯

The only library needed is [python-chess](https://python-chess.readthedocs.io/en/latest/index.html):
```
pip install chess
```

**To use engines:** Make sure that `stockfish` and `gnuchessu` are installed and on your `PATH`. Stockfish can be downloaded on Windows, Linux, and macOS from [their official website](https://stockfishchess.org/). GNU Chess can be installed on Linux via your favorite package manager, or built [from source](https://ftp.gnu.org/gnu/chess/) to get the latest version. There might be binaries for other platforms available for download ¯\\\_(ツ)\_/¯

### Usage

Launch python in interactive mode:

```
python3 -i main.py
```

Now, you can set whatever strategies you want by setting the `strat1` and `strat2` variables:

```
>>> strat1 = MinResponses()
>>> strat2 = Worstfish()
```

Finally, run a game:

```
>>> run_game()
```

The game will be printed in PGN format as it unfolds.

**To play against the strategies:** Make one (or both) of the strategies an instance of `Human`. For example:

```
>>> strat1 = Human()
>>> strat2 = LightSquares()
>>> run_game()
```

When it is your turn, it will ask for your moves which you can enter in SAN or UCI format.

## Some TODOs

As I stated earlier, these strategies are inspired by Tom 7, and some of those strategies were very interesting (such as the blindfolded strats), and I want to get as many of those implemented as possible.

Here are some things I'd like to get done at some point:

* Implement blindfolded strategies
	* Not sure if I want to compile Tom 7's C++ sources and get it to communicate the result with my program, or if I should redo it from scratch using python machine learning libraries...
* Implement NES Chessmaster communication
	* Maybe also the chess engine from [that weird cartridge I have for the original Game Boy](https://gamefaqs.gamespot.com/gameboy/569621-4-in-1-fun-pak)?
* Add a bunch of the smaller strategies
* Implement a graphical chessboard, especially for human playing
* Make it so all games will output to a file to enable documenting games between the players
* Prolly more
