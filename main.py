# Chess Tournament/Playground framework in Python
# by Terry Hearst

import chess

from strats import *


##                           ##
## TOURNAMENT IMPLEMENTATION ##
##                           ##

# Global variables

board = chess.Board()
strat1 = RandomMove()
strat2 = RandomMove()

def setup_game():
	global board, strat1, strat2
	board = chess.Board()
	strat1.setup()
	strat2.setup()

def run_game():
	setup_game()
	continue_game()

def continue_game():
	if board.turn == chess.BLACK and not board.is_game_over() and not isinstance(strat2, Human):
		print(board.fullmove_number)
	while not board.is_game_over():
		strat = strat1 if board.turn == chess.WHITE else strat2
		move = strat.get_move(board)
		if move is None:
			return

		if isinstance(strat1, Human) or isinstance(strat2, Human):
			print(board.fullmove_number, end = (".   " if board.turn == chess.WHITE else "... "))
			print(board.san(move))
		else:
			if board.turn == chess.WHITE:
				print(board.fullmove_number, end = ". ")
			print(board.san(move), end = " ", flush = True)

		board.push(move)
		strat1.update_state(board)
		strat2.update_state(board)
	print(board.outcome().result())

setup_game()
