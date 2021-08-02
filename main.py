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

def run_game():
	global board
	board = chess.Board()
	continue_game()

def continue_game():
	strat1.full_setup(board = board)
	strat2.full_setup(board = board)
	do_game_loop()

def do_game_loop():
	if board.turn == chess.BLACK and not board.is_game_over() and not isinstance(strat2, Human):
		print(board.fullmove_number, end = "... ")
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
