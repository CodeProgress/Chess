# engine
import random
from copy import deepcopy


class Engine:
    def __init__(self):
        self.piece_values = {'p': 1, 'b': 3, 'n': 3, 'r': 5, 'q': 9, 'k': 10000,
                             'P': 1, 'B': 3, 'N': 3, 'R': 5, 'Q': 9, 'K': 10000}

    @staticmethod
    def get_all_moves(board):
        moves = []
        if board.is_whites_turn():
            pieces = board.white_pieces_on_the_board
        else:
            pieces = board.black_pieces_on_the_board
        for piece in pieces:
            for move in piece.all_legal_squares_to_move_to(board):
                moves.append((piece.current_square, move))
        return moves

    def get_random_move(self, board):
        return random.choice(self.get_all_moves(board))

    def get_material_score(self, board):
        if board.is_whites_turn():
            own_pieces = board.white_pieces_on_the_board
            opponent_pieces = board.black_pieces_on_the_board
        else:
            own_pieces = board.black_pieces_on_the_board
            opponent_pieces = board.white_pieces_on_the_board

        own_total = sum(self.piece_values[str(piece)] for piece in own_pieces)
        opp_total = sum(self.piece_values[str(piece)] for piece in opponent_pieces)

        score = float(own_total)/opp_total
        return score

    def get_one_ply_materialistic_move_and_score(self, board):
        moves = self.get_all_moves(board)
        random.shuffle(moves)
        best_move = moves[0]
        best_score = -100000
        for move in moves:
            copy_board = deepcopy(board)
            copy_board.make_move(move[0], move[1])
            pos_new_score = self.get_material_score(copy_board)
            if pos_new_score > best_score:
                best_move = move
                best_score = pos_new_score
        return best_move, best_score

    def get_one_ply_materialistic_move(self, board):
        return self.get_one_ply_materialistic_move_and_score(board)[0]
