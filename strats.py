# Strategies for the chess tournament

import math
import random

import chess
import chess.engine


##                ##
## GENERIC STRATS ##
##                ##

# Base for all strategies
class Strategy:
	def __init__(self):
		self.setup()

	def setup(self):
		# Here a stateful strategy can initialize its state
		pass

	def get_name(self):
		# Returns the name of the strategy. As a default, return a pretty printed version of the class name
		# To split a camel case string, I used code from here:
		# https://stackoverflow.com/questions/29916065/how-to-do-camelcase-split-in-python
		name = type(self).__name__
		splitted = re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', name)).split()
		if splitted[-1] == "Strategy":
			del splitted[-1] 	# Remove the word "Strategy"
		return " ".join(splitted)

	def get_move(self, board: chess.Board) -> chess.Move:
		# Here is the code in which a strategy will determine which move it would play on the current board
		# NOTE: If this strategy is stateful, it should NOT update its state here, rather in update_state

		# This method MUST be overwritten
		raise NotImplementedError

	def update_state(self, board: chess.Board):
		# Here strategy can update its state based on the move that was played. Only the resulting board is given: the
		# last move can be obtained with board.peek()
		pass

# A type of strategy where it will evaluate the resulting positions of each legal move, and choose the move with the
# highest evaluation. The function "evaluate" must be implemented
class EvalPositionStrategy(Strategy):
	def get_move(self, board: chess.Board) -> chess.Move:
		candidates = []
		best_eval = -math.inf

		for move in list(board.legal_moves):
			board.push(move)
			current_eval = self.evaluate(board)
			board.pop()

			if current_eval > best_eval:
				candidates = [move]
				best_eval = current_eval
			elif current_eval == best_eval:
				candidates.append(move)

		return random.choice(candidates)

	def evaluate(board: chess.Board):
		raise NotImplementedError

class UciEngineStrategy(Strategy):
	def __init__(self, engine_name: str, limit):
		self.engine = chess.engine.SimpleEngine.popen_uci(engine_name)

		# "limit" can either be a chess.engine.Limit, or an integer depth value
		if isinstance(limit, chess.engine.Limit):
			self.limit = limit
		else:
			self.limit = chess.engine.Limit(depth = limit)

		super().__init__()

	def get_move(self, board: chess.Board) -> chess.Move:
		result = self.engine.play(board, self.limit)
		return result.move

	def __del__(self):
		self.engine.quit()


##                 ##
## CONCRETE STRATS ##
##                 ##

# Human player class, reads moves from stdin
class Human(Strategy):
	def get_move(self, board: chess.Board) -> chess.Move:
		try:
			input_str = input("Enter move >> ")
			if input_str == "quit":
				return None
			move = board.parse_san(input_str)
			return move
		except ValueError:
			print("Invalid move")
			return self.get_move()

# Simple random strategy
class RandomMove(Strategy):
	def get_move(self, board: chess.Board) -> chess.Move:
		return random.choice(list(board.legal_moves))

# Plays a move that gives the opponent the least possible responses
class MinResponses(EvalPositionStrategy):
	def evaluate(self, board: chess.Board):
		return -board.legal_moves.count()

# Minimizes the distance between the two kings
class SuicideKing(EvalPositionStrategy):
	def evaluate(self, board: chess.Board):
		white_king = board.king(chess.WHITE)
		black_king = board.king(chess.BLACK)
		return -chess.square_distance(white_king, black_king)

# Stockfish
class Stockfish(UciEngineStrategy):
	def __init__(self, limit = 18):
		super().__init__("stockfish", limit)

# GNU Chess
class GnuChess(UciEngineStrategy):
	def __init__(self, limit = 10):
		super().__init__("gnuchessu", limit)
		self.engine.configure({"Hash": 1024})

# Uses stockfish to play the worst possible move. Note that this derives from EvalPositionStrategy rather than
# UciEngineStrategy since it needs to get a score for all positions (including the bad ones)
class Worstfish(EvalPositionStrategy):
	def __init__(self):
		self.engine = chess.engine.SimpleEngine.popen_uci("stockfish")
		super().__init__()

	def __del__(self):
		self.engine.quit()

	def evaluate(self, board: chess.Board):
		result = self.engine.analyse(board, chess.engine.Limit(depth = 10))
		score = result["score"].relative.score(mate_score = 1000000)
		return score

class LightOrDarkSquares(EvalPositionStrategy):
	def __init__(self, target_color: chess.Color = None):
		if target_color is None:
			self.target_color = random.choice([chess.WHITE, chess.BLACK])
		else:
			self.target_color = target_color

		super().__init__()

	def evaluate(self, board: chess.Board):
		our_color = not board.turn

		our_pieces  = board.pieces(chess.PAWN,   our_color)
		our_pieces |= board.pieces(chess.KNIGHT, our_color)
		our_pieces |= board.pieces(chess.BISHOP, our_color)
		our_pieces |= board.pieces(chess.ROOK,   our_color)
		our_pieces |= board.pieces(chess.QUEEN,  our_color)
		our_pieces |= board.pieces(chess.KING,   our_color)

		color_mask = chess.BB_LIGHT_SQUARES if self.target_color == chess.WHITE else chess.BB_DARK_SQUARES

		return len(our_pieces & color_mask)

class LightSquares(LightOrDarkSquares):
	def __init__(self):
		super().__init__(chess.WHITE)

class DarkSquares(LightOrDarkSquares):
	def __init__(self):
		super().__init__(chess.BLACK)

# Moves a piece that has been moved the least amount of times to a square visited the least amount of times
class Equalizer(Strategy):
	def setup(self):
		# We don't know if we're playing as white or black, so just keep copies of both. Might be better if I can find a
		# nice way to inform the strategy what color it's playing

		self.white_moved = [None] * 64
		self.white_visited = [0] * 64
		self.black_moved = [None] * 64
		self.black_visited = [0] * 64

		for i in range(16):
			# First and second rank contain white pieces
			self.white_moved[i] = 0
			self.white_visited[i] = 1
			# 7th and 8th ranks contain black pieces
			self.black_moved[i + 48] = 0
			self.black_visited[i + 48] = 1

	def get_move(self, board: chess.Board) -> chess.Move:
		candidates = []
		least_moved_count = math.inf
		least_visited_count = math.inf

		if board.turn == chess.WHITE:
			moved = self.white_moved
			visited = self.white_visited
		else:
			moved = self.black_moved
			visited = self.black_visited

		for move in list(board.legal_moves):
			moved_count = moved[move.from_square]
			visited_count = visited[move.to_square]
			if moved_count < least_moved_count:
				least_moved_count = moved_count
				candidates = [move]
				least_visited_count = visited_count
			elif moved_count == least_moved_count:
				if visited_count < least_visited_count:
					least_visited_count = visited_count
					candidates = [move]
				elif visited_count == least_visited_count:
					candidates.append(move)

		return random.choice(candidates)

	def update_state(self, board: chess.Board):
		move = board.pop()

		if board.turn == chess.WHITE:
			moved = self.white_moved
			visited = self.white_visited
			their_moved = self.black_moved
			their_visited = self.black_visited
		else:
			moved = self.black_moved
			visited = self.black_visited
			their_moved = self.white_moved
			their_visited = self.white_visited

		# If this is a castling move, update the values for the rook as well
		if board.is_castling(move):
			rank = chess.square_rank(move.to_square)
			if board.is_kingside_castling(move):
				rook_from = chess.square(7, rank)
				rook_to = chess.square(5, rank)
			else:
				rook_from = chess.square(0, rank)
				rook_to = chess.square(3, rank)
			moved[rook_to] = moved[rook_from] + 1
			moved[rook_from] = None
			visited[rook_to] += 1

		# Remove any captured piece from their side
		their_moved[move.to_square] = None
		if board.is_en_passant(move):
			pawn_square = board.ep_square
			if board.turn == chess.WHITE:
				pawn_square -= 8
			else:
				pawn_square += 8
			their_moved[pawn_square] = None

		moved[move.to_square] = moved[move.from_square] + 1
		moved[move.from_square] = None
		visited[move.to_square] += 1

		board.push(move)

	def print_board(self):
		print("White:")
		print("Moved:                         Visited:")
		for i in range(8):
			rank = 7 - i
			for file in range(8):
				square = chess.square(file, rank)
				if self.white_moved[square] is None:
					print(" .", end = " ")
				else:
					print("{:2d}".format(self.white_moved[square]), end = " ")
			print("      ", end = "")
			for file in range(8):
				square = chess.square(file, rank)
				print("{:2d}".format(self.white_visited[square]), end = " ")
			print()

		print()
		print("Black:")
		print("Moved:                         Visited:")
		for i in range(8):
			rank = 7 - i
			for file in range(8):
				square = chess.square(file, rank)
				if self.black_moved[square] is None:
					print(" .", end = " ")
				else:
					print("{:2d}".format(self.black_moved[square]), end = " ")
			print("      ", end = "")
			for file in range(8):
				square = chess.square(file, rank)
				print("{:2d}".format(self.black_visited[square]), end = " ")
			print()
