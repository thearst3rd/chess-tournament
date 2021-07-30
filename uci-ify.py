#!/usr/bin/env python3
# Runs a strat as a barebones UCI engine

import sys
import chess

from strats import *

strat_list = [RandomMove, MinResponses, SuicideKing, Stockfish, GnuChess, Worstfish, LightSquares, DarkSquares,
		Equalizer, Swarm, Huddle]

def print_usage():
	print("Usage:")
	print("\t" + sys.argv[0] + " [strategy]")
	print("\t" + sys.argv[0] + " --help|-h")
	print()
	print("Strategies:")
	index = 0
	for strat in strat_list:
		if index == 5:
			print()
			index = 0
		index += 1
		print("\t" + strat.__name__, end = "")
	print()

def get_strat(name):
	name = name.lower()
	for strat in strat_list:
		if strat.__name__.lower().startswith(name):
			return strat()
	return None

def main():
	strat = None
	if len(sys.argv) > 1:
		if sys.argv[1] == "--help" or sys.argv[1] == "-h":
			print_usage()
			exit()
		strat = get_strat(sys.argv[1])
	if strat is None:
		strat = RandomMove()

	print("chess-tournament Strategy UCI-ifier")

	board = chess.Board()

	running = True
	while running:
		try:
			raw_command = input()
		except EOFError:
			continue
		command = raw_command.strip().split(" ")
		while "" in command:
			command.remove("")

		if command[0] == "uci":
			print("id name chess-tournament")
			print("id author thearst3rd")
			print()
			print("option name Strategy type combo default ", end = type(strat).__name__)
			for strategy in strat_list:
				print(" var ", end = strategy.__name__)
			print()
			print("uciok")
		elif command[0] == "quit":
			running = False
		elif command[0] == "isready":
			print("readyok")
		elif command[0] == "debug":
			# Nothing to do
			pass
		elif command[0] == "ucinewgame":
			strat.setup()
		elif command[0] == "setoption":
			if len(command) < 5 or command[1] != "name":
				print("Bad setoption")
				continue
			if command[2] != "Strategy":
				print("Invalid option \"" + command[2] + "\"")
				continue
			if command[3] != "value":
				print("Bad setoption")
				continue
			new_strat = get_strat(command[4])
			if new_strat is None:
				print("Unknown strat " + command[4])
				continue
			strat = new_strat
		elif command[0] == "position":
			if command[1] == "startpos":
				moves_start = 2
				board = chess.Board()
			elif command[1] == "fen":
				moves_start = 8
				try:
					fen_str = " ".join(command[2:8])
					board = chess.Board(fen_str)
				except:
					print("Bad fen")
					continue
			else:
				print("Bad position command")
				continue
			if len(command) > moves_start and command[moves_start] == "moves":
				for move_uci in command[(moves_start+1):]:
					try:
						move = board.parse_uci(move_uci)
						board.push(move)
					except ValueError:
						# Ignore and stop parsing moves
						break
			strat.full_setup(board = board)
		elif command[0] == "go":
			if board.is_game_over():
				print("bestmove (none)")
				continue
			move = strat.get_move(board)
			print("bestmove " + move.uci())
		elif command[0] == "d":
			# Debug command, dunno if it's standard but stockfish supports it
			print(board)
			print(board.fen())
			print(type(strat).__name__)
		else:
			print("Unknown command: " + command[0])

if __name__ == "__main__":
	main()
