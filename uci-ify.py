#!/usr/bin/env python3
# Runs a strat as a barebones UCI engine

import sys
import chess

from strats import *

strat_list = [
	RandomMove,
	MinResponses,
	SuicideKing,
	Stockfish,
	GnuChess,
	Worstfish,
	LightSquares,
	DarkSquares,
	Equalizer,
	Swarm,
	Huddle,
	LightSquaresHardMode,
	DarkSquaresHardMode,
	Possessed,
]

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

		if len(command) == 0:
			continue

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
			# Nothing to do
			pass
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
			strat.full_setup(board = board)
		elif command[0] == "position":
			if command[1] == "startpos":
				moves_start = 2
				board.reset()
			elif command[1] == "fen":
				moves_start = 8
				try:
					fen_str = " ".join(command[2:8])
					board.set_fen(fen_str)
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

			# Parse commands
			curr_token_index = 1
			limit = None
			root_moves = None
			while curr_token_index < len(command):
				token = command[curr_token_index]
				tokens_left = len(command) - curr_token_index
				# 'ponder' and 'infinite' not supported
				if token == "searchmoves":
					board_moves_uci = []
					root_moves = []
					for move in list(board.legal_moves):
						board_moves_uci.append(board.uci(move))
					curr_token_index += 1
					while curr_token_index < len(command):
						if command[curr_token_index] in board_moves_uci:
							root_moves.append(chess.Move.from_uci(command[curr_token_index]))
							curr_token_index += 1
						else:
							curr_token_index -= 1
							break
				elif token in ["wtime", "btime", "winc", "binc", "movestogo", "depth", "nodes", "mate", "movetime"]:
					if tokens_left >= 1:
						if limit is None:
							limit = chess.engine.Limit()
						num = int(command[curr_token_index + 1])
						if token == "wtime":
							limit.white_clock = float(num) / 1000.0
						elif token == "btime":
							limit.black_clock = float(num) / 1000.0
						elif token == "winc":
							limit.white_inc = float(num) / 1000.0
						elif token == "binc":
							limit.black_inc = float(num) / 1000.0
						elif token == "movestogo":
							limit.remaining_moves = num
						elif token == "depth":
							limit.depth = num
						elif token == "nodes":
							limit.nodes = num
						elif token == "mate":
							limit.mate = num
						elif token == "movetime":
							limit.time = float(num) / 1000.0
						curr_token_index += 1
				curr_token_index += 1

			kwargs = {}
			if limit is not None:
				kwargs["limit"] = limit
			if root_moves is not None:
				kwargs["root_moves"] = root_moves

			move = strat.get_move(board, **kwargs)
			print("bestmove " + move.uci())
		elif command[0] == "d":
			# Debug command, dunno if it's standard but stockfish supports it
			print(board)
			print(board.fen())
			print(type(strat).__name__)
		else:
			print("Unknown command: " + command[0])

if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		# Gracefully exit
		pass
