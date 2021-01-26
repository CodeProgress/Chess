import Pieces
from copy import deepcopy


class ChessBoard:
    ALL_COLS = 'abcdefgh'
    ALL_ROWS = '12345678'
    EMPTY_SQUARE = '~'

    def __init__(self):
        self.board = []
        self.is_game_over = False
        self.most_resent_player_has_resigned = False
        self.past_game_states = {}
        self.fifty_move_counter = 0
        self.outcome = None
        self.ignore_move_order = False
        self.squaresAttackingWhiteKing = []  # check, double check
        self.squaresAttackingBlackKing = []
        self.pieces_off_the_board = []
        self.white_pieces_on_the_board = []
        self.black_pieces_on_the_board = []
        self.enPassantTargetSquare = ''
        self.resetEnPassantTargetSquare = False
        self.canBlackCastleLong = True
        self.canBlackCastleShort = True
        self.canWhiteCastleLong = True
        self.canWhiteCastleShort = True
        self.promotePawnTo = None  # q, r, n or b.  To be set in a "get_move" type method and used in Pieces.Pawn
        self.create_starting_position()
        self.whiteKing = self.get_contents_of_square('e1')
        self.blackKing = self.get_contents_of_square('e8')
        self.sideToMove = 0  # 0 = white, 1 = black

    def create_starting_position(self):
        self.create_empty_board()
        self.add_standard_initial_pieces_to_board()

    def create_empty_board(self):
        for row in range(8):
            row_list = []
            for _ in self.ALL_COLS:
                row_list.append(self.EMPTY_SQUARE)
            self.board.append(row_list)

    def add_piece_to_board(self, piece, color, squares):
        for sq in squares:
            assert self.is_square_on_board(sq)
            piece_to_add = piece(color, sq)
            self.update_square_with_piece(piece_to_add, sq)
            if piece_to_add.is_white_piece():
                self.white_pieces_on_the_board.append(piece_to_add)
            elif piece_to_add.is_black_piece():
                self.black_pieces_on_the_board.append(piece_to_add)

    def move_piece_from_on_the_board_to_off_the_board(self, piece):
        if piece.is_white_piece():
            self.white_pieces_on_the_board.remove(piece)
        elif piece.is_black_piece():
            self.black_pieces_on_the_board.remove(piece)
        self.pieces_off_the_board.append(piece)

    def add_standard_initial_pieces_to_board(self):
        # add pawns
        self.add_piece_to_board(Pieces.Pawn, 'w', ['a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2'])
        self.add_piece_to_board(Pieces.Pawn, 'b', ['a7', 'b7', 'c7', 'd7', 'e7', 'f7', 'g7', 'h7'])

        # add rooks
        self.add_piece_to_board(Pieces.Rook, 'w', ['a1', 'h1'])
        self.add_piece_to_board(Pieces.Rook, 'b', ['a8', 'h8'])

        # add knights
        self.add_piece_to_board(Pieces.Knight, 'w', ['b1', 'g1'])
        self.add_piece_to_board(Pieces.Knight, 'b', ['b8', 'g8'])

        # add bishops
        self.add_piece_to_board(Pieces.Bishop, 'w', ['c1', 'f1'])
        self.add_piece_to_board(Pieces.Bishop, 'b', ['c8', 'f8'])

        # add queens
        self.add_piece_to_board(Pieces.Queen, 'w', ['d1'])
        self.add_piece_to_board(Pieces.Queen, 'b', ['d8'])

        # add kings
        self.add_piece_to_board(Pieces.King, 'w', ['e1'])
        self.add_piece_to_board(Pieces.King, 'b', ['e8'])

    def get_square_from_row_and_col_coordinates(self, row, col):
        assert type(row) == int and type(col) == int
        assert 0 <= row <= 7
        assert 0 <= col <= 7
        row_as_chr = chr(row + 49)
        col_as_chr = chr(col + 97)
        square = col_as_chr + row_as_chr
        assert self.is_square_on_board(square)
        return square

    def get_row_and_col_coordinates_from_square(self, square):
        return self.get_row_number_from_square(square), self.get_col_number_from_square(square)

    def get_row_number_from_square(self, square):
        assert self.is_valid_square(square)
        row = ord(square[1]) - 49  # ord('1') == 49
        return row

    def get_col_number_from_square(self, square):
        assert self.is_valid_square(square)
        col = ord(square[0]) - 97  # ord('a') == 97
        return col

    @staticmethod
    def is_valid_square(square):
        if type(square) != str:
            return False
        if len(square) != 2:
            return False
        row = ord(square[1]) - 49  # ord('1') == 49
        col = ord(square[0]) - 97  # ord('a') == 97
        return (0 <= row <= 7) and (0 <= col <= 7)

    def is_square_on_board(self, square):
        if not self.is_valid_square(square):
            return False
        row, col = self.get_row_and_col_coordinates_from_square(square)
        return self.is_coordinate_on_board(row, col)

    def is_square_empty(self, square):
        return self.get_contents_of_square(square) == self.EMPTY_SQUARE

    def is_coordinate_empty(self, row, col):
        assert self.is_coordinate_on_board(row, col)
        return self.board[row][col] == self.EMPTY_SQUARE

    @staticmethod
    def is_coordinate_on_board(row, col):
        if (0 <= row <= 7) and (0 <= col <= 7):
            return True
        return False

    def assign_value_to_square(self, value, square):
        row, col = self.get_row_and_col_coordinates_from_square(square)
        self.board[row][col] = value

    def clear_square(self, square):
        if not self.is_square_empty(square):
            self.assign_value_to_square(self.EMPTY_SQUARE, square)

    def update_en_passant_target_square(self, new_en_passant_square):
        self.enPassantTargetSquare = new_en_passant_square

    def update_square_with_piece(self, piece, square):
        if not self.is_square_empty(square):
            self.move_piece_from_on_the_board_to_off_the_board(self.get_contents_of_square(square))
        self.clear_square(square)
        self.assign_value_to_square(piece, square)

    def get_contents_of_square(self, square):
        row, col = self.get_row_and_col_coordinates_from_square(square)
        return self.board[row][col]

    def is_one_square_away(self, origin_square, destination_square):
        origin_sq_row, origin_sq_col = self.get_row_and_col_coordinates_from_square(origin_square)
        dest_sq_row, dest_sq_col = self.get_row_and_col_coordinates_from_square(destination_square)
        return abs(origin_sq_row - dest_sq_row) <= 1 and abs(origin_sq_col - dest_sq_col) <= 1

    def is_empty_diagonal_from(self, origin_square, destination_square):
        # these should already be checked
        assert self.is_square_on_board(origin_square) and self.is_square_on_board(destination_square)
        assert origin_square != destination_square

        origin_sq_row, origin_sq_col = self.get_row_and_col_coordinates_from_square(origin_square)
        dest_sq_row, dest_sq_col = self.get_row_and_col_coordinates_from_square(destination_square)

        # check if diagonal
        row_dif = abs(origin_sq_row - dest_sq_row)
        if row_dif != abs(origin_sq_col - dest_sq_col):
            return False

        # now check if that diagonal is empty
        if origin_sq_row > dest_sq_row:
            # count down
            between_sq_row_coords = range(origin_sq_row - 1, dest_sq_row, -1)
        else:
            # count up
            between_sq_row_coords = range(origin_sq_row + 1, dest_sq_row)

        if origin_sq_col > dest_sq_col:
            # count down
            between_sq_col_coords = range(origin_sq_col - 1, dest_sq_col, -1)
        else:
            # count up
            between_sq_col_coords = range(origin_sq_col + 1, dest_sq_col)

        assert len(between_sq_row_coords) == len(between_sq_col_coords)

        for i in range(len(between_sq_row_coords)):
            if not self.is_coordinate_empty(between_sq_row_coords[i], between_sq_col_coords[i]):
                return False
        return True

    def is_empty_orthogonal_from(self, origin_square, destination_square):
        # these should already be checked
        assert self.is_square_on_board(origin_square) and self.is_square_on_board(destination_square)
        assert origin_square != destination_square

        origin_sq_row, origin_sq_col = self.get_row_and_col_coordinates_from_square(origin_square)
        dest_sq_row, dest_sq_col = self.get_row_and_col_coordinates_from_square(destination_square)

        if origin_sq_row == dest_sq_row:
            fixed_row = origin_sq_row
            range_to_check = range(min(origin_sq_col, dest_sq_col) + 1, max(origin_sq_col, dest_sq_col))
            for col in range_to_check:
                if not self.is_coordinate_empty(fixed_row, col):
                    return False
        elif origin_sq_col == dest_sq_col:
            fixed_col = origin_sq_col
            range_to_check = range(min(origin_sq_row, dest_sq_row) + 1, max(origin_sq_row, dest_sq_row))
            for row in range_to_check:
                if not self.is_coordinate_empty(row, fixed_col):
                    return False
        else:
            return False  # the squares are not orthogonal
        return True

    def reset_en_passant_target_square_if_needed(self):
        # reset the en passant square (makes sure it's only available for one turn)
        if self.resetEnPassantTargetSquare:
            self.update_en_passant_target_square('')
            self.resetEnPassantTargetSquare = False
        if self.enPassantTargetSquare != '':
            self.resetEnPassantTargetSquare = True

    def is_king_in_check_after_simulating_move(self, origin_square, destination_square, king_to_validate):
        copy_of_board = deepcopy(self)
        copy_of_board.make_move(origin_square, destination_square)

        if king_to_validate.current_square != origin_square:
            square_of_king_after_move = king_to_validate.current_square
        else:
            square_of_king_after_move = destination_square

        return copy_of_board.is_square_defended_by_opponent(
            square_of_king_after_move, king_to_validate.get_color_of_opponent_side())

    def is_valid_move_order(self, origin_piece):
        if self.ignore_move_order:
            return True
        if origin_piece.is_white_piece() and not self.is_whites_turn():
            return False
        elif origin_piece.is_black_piece() and not self.is_blacks_turn():
            return False
        return True

    def is_valid_move(self, origin_square, destination_square):
        if self.is_square_empty(origin_square):
            return False

        origin_piece = self.get_contents_of_square(origin_square)

        if not self.is_valid_move_order(origin_piece):
            return False

        return origin_piece.is_legal_move(self, destination_square)

    def get_king_of_side_that_is_moving(self):
        if self.is_whites_turn():
            return self.whiteKing
        return self.blackKing

    def update_past_game_states(self):
        game_state = str(self)
        if game_state in self.past_game_states:
            self.past_game_states[game_state] += 1
        else:
            self.past_game_states[game_state] = 1

    def is_non_reversible_move(self, origin_square, destination_square):
        # pawn move
        if type(self.get_contents_of_square(origin_square)) == Pieces.Pawn:
            return True
        # or capture
        return not self.is_square_empty(destination_square)

    def get_path_traversal_incrementer(self, start_sq, middle_sq):
        start_row, start_col = self.get_row_and_col_coordinates_from_square(start_sq)
        middle_row, middle_col = self.get_row_and_col_coordinates_from_square(middle_sq)

        row_inc = middle_row - start_row
        col_inc = middle_col - start_col

        divider_to_get_back_to_one_to_one_ratio = max(abs(row_inc), abs(col_inc))
        row_inc //= divider_to_get_back_to_one_to_one_ratio
        col_inc //= divider_to_get_back_to_one_to_one_ratio

        return row_inc, col_inc

    @staticmethod
    def get_coordinates_after_applying_traversal_incrementer(coordinates, incrementer):
        return coordinates[0] + incrementer[0], coordinates[1] + incrementer[1]

    def get_next_piece_along_path(self, start_sq, middle_sq):
        traversal_incrementer = self.get_path_traversal_incrementer(start_sq, middle_sq)
        next_pos_coordinates = self.get_coordinates_after_applying_traversal_incrementer(
            self.get_row_and_col_coordinates_from_square(middle_sq), traversal_incrementer)
        while self.is_coordinate_on_board(next_pos_coordinates[0], next_pos_coordinates[1]):
            if self.is_square_empty(
                    self.get_square_from_row_and_col_coordinates(next_pos_coordinates[0], next_pos_coordinates[1])):
                next_pos_coordinates = self.get_coordinates_after_applying_traversal_incrementer(
                    next_pos_coordinates, traversal_incrementer)
            else:
                return self.get_contents_of_square(
                    self.get_square_from_row_and_col_coordinates(next_pos_coordinates[0], next_pos_coordinates[1]))
        return self.EMPTY_SQUARE  # this signifies that nothing is along path and the end of the board has been reached

    def update_squares_attacking_king(self, last_moved_piece_origin_square, last_moved_piece_current_square):
        squares_from_which_check_is_being_delivered = []

        last_moved_piece = self.get_contents_of_square(last_moved_piece_current_square)
        if last_moved_piece.is_white_piece():
            opponent_king = self.blackKing
        else:
            opponent_king = self.whiteKing

        # regular check: is the king square a valid move from the lastMovedPieceCurrentSquare?
        if last_moved_piece.is_legal_move(self, opponent_king.current_square):
            squares_from_which_check_is_being_delivered.append(last_moved_piece_current_square)

        # discover check?
        if self.is_empty_diagonal_from(opponent_king.current_square, last_moved_piece_origin_square):
            pos_piece_along_path = self.get_next_piece_along_path(
                opponent_king.current_square, last_moved_piece_origin_square)
            if pos_piece_along_path != self.EMPTY_SQUARE \
                    and pos_piece_along_path.color != opponent_king.color \
                    and (type(pos_piece_along_path) == Pieces.Queen or type(pos_piece_along_path) == Pieces.Bishop):
                squares_from_which_check_is_being_delivered.append(pos_piece_along_path.current_square)
        elif self.is_empty_orthogonal_from(opponent_king.current_square, last_moved_piece_origin_square):
            pos_piece_along_path = self.get_next_piece_along_path(
                opponent_king.current_square, last_moved_piece_origin_square)
            if pos_piece_along_path != self.EMPTY_SQUARE \
                    and pos_piece_along_path.color != opponent_king.color \
                    and (type(pos_piece_along_path) == Pieces.Queen or type(pos_piece_along_path) == Pieces.Rook):
                squares_from_which_check_is_being_delivered.append(pos_piece_along_path.current_square)

        if self.is_whites_turn():
            self.squaresAttackingBlackKing = squares_from_which_check_is_being_delivered
            self.squaresAttackingWhiteKing = []  # if we made it this far, the king wasn't in check, so reset
        else:
            self.squaresAttackingWhiteKing = squares_from_which_check_is_being_delivered
            self.squaresAttackingBlackKing = []

    def is_king_in_check(self, king):
        if king.is_white_piece():
            return len(self.squaresAttackingWhiteKing) != 0
        return len(self.squaresAttackingBlackKing) != 0

    def update_side_to_move(self):
        self.sideToMove ^= 1

    def adjust_fifty_move_counter(self, origin_square, destination_square):
        if self.is_non_reversible_move(origin_square, destination_square):
            self.fifty_move_counter = 0
        else:
            self.fifty_move_counter += .5  # half move

    def execute_move(self, origin_square, destination_square):
        if self.is_valid_move(origin_square, destination_square):
            self.make_move(origin_square, destination_square)
            # game state related housekeeping
            self.update_past_game_states()
            self.update_squares_attacking_king(origin_square, destination_square)
            if self.is_ending_condition():
                self.is_game_over = True
            else:
                self.update_side_to_move()
            return True
        return False

    def make_move(self, origin_square, destination_square):
        # blindly makes move without regard to validation
        self.adjust_fifty_move_counter(origin_square, destination_square)
        origin_piece = self.get_contents_of_square(origin_square)
        origin_piece.execute_move(self, destination_square)
        self.reset_en_passant_target_square_if_needed()

    def attempt_to_make_move(self, move):
        # move is of the form e2e4 or e7e8q
        if move == 'resign':
            self.most_resent_player_has_resigned = True
            return True

        if type(move) != str:
            return False

        if len(move) < 4 or len(move) > 5:
            return False

        origin_square = move[:2]
        destination_square = move[2:4]
        if len(move) == 5:
            self.promotePawnTo = move[-1]

        if not self.is_valid_square(origin_square) or not self.is_valid_square(destination_square):
            return False

        if not self.execute_move(origin_square, destination_square):
            return False

        self.promotePawnTo = None
        return True

    def simulate_get_move(self, origin_square, destination_square, pawn_promotion=None):
        if pawn_promotion:
            self.promotePawnTo = pawn_promotion
        self.execute_move(origin_square, destination_square)
        self.promotePawnTo = None

    def get_squares_along_path(self, start_sq, end_sq):
        squares = []
        incrementer = self.get_path_traversal_incrementer(start_sq, end_sq)
        starting_coords = self.get_row_and_col_coordinates_from_square(start_sq)
        ending_coords = self.get_row_and_col_coordinates_from_square(end_sq)
        pos_coords = self.get_coordinates_after_applying_traversal_incrementer(starting_coords, incrementer)
        while pos_coords != ending_coords:
            assert self.is_coordinate_empty(pos_coords[0], pos_coords[1])
            squares.append(self.get_square_from_row_and_col_coordinates(pos_coords[0], pos_coords[1]))
            pos_coords = self.get_coordinates_after_applying_traversal_incrementer(pos_coords, incrementer)
        return squares

    def can_capture_attacking_piece(self, square_of_attacking_piece, king_under_attack):
        if self.is_square_under_attack_from_non_king_piece(square_of_attacking_piece, king_under_attack.color):
            return True

    def can_block_path_of_attacking_piece(self, square_of_attacking_piece, king_under_attack):
        attacking_piece = self.get_contents_of_square(square_of_attacking_piece)
        if type(attacking_piece) == Pieces.Queen \
                or type(attacking_piece) == Pieces.Bishop \
                or type(attacking_piece) == Pieces.Rook:
            squares_along_path = self.get_squares_along_path(
                king_under_attack.current_square, square_of_attacking_piece)
            for sq in squares_along_path:
                if self.can_move_to_square_with_non_king_piece(sq, king_under_attack.color):
                    return True
        return False

    def get_squares_attacking_king(self, king):
        if king.is_white_piece():
            return self.squaresAttackingWhiteKing
        return self.squaresAttackingBlackKing

    def is_checkmate(self, king):
        if not self.is_king_in_check(king):
            return False

        squares_attacking_king = self.get_squares_attacking_king(king)

        # King move (for single check and double check)
        if king.all_legal_squares_to_move_to(self):
            return False

        if len(squares_attacking_king) == 1:
            square_of_attacking_piece = squares_attacking_king[0]

            if self.can_capture_attacking_piece(square_of_attacking_piece, king):
                return False

            if self.can_block_path_of_attacking_piece(square_of_attacking_piece, king):
                return False

        # if len > 1, that's double check and would have needed to be a king move which was already determined

        if self.is_whites_turn():
            self.outcome = "Checkmate!! White Wins"
        else:
            self.outcome = "Checkmate!! Black Wins"
        return True

    def is_stalemate(self, king):
        if self.is_king_in_check(king):
            return False

        if king.is_white_piece():
            piece_list = self.white_pieces_on_the_board
        else:
            piece_list = self.black_pieces_on_the_board

        # no legal moves
        for piece in piece_list:
            if piece.all_legal_squares_to_move_to(self):
                return False

        self.outcome = "Stalemate! Draw"
        return True

    def is_fifty_moves_without_pawn_move_or_capture(self):
        if abs(self.fifty_move_counter - 50) < .001:  # fifty_move_counter is double...
            self.outcome = "Fifty Moves without pawn move or capture! Draw"
            return True
        return False

    def is_three_fold_repetition(self):
        if str(self) not in self.past_game_states:
            return False
        if self.past_game_states[str(self)] == 3:
            self.outcome = "Three Fold Repetition! Draw"
            return True
        return False

    def is_resignation(self):
        if self.most_resent_player_has_resigned:
            if self.is_whites_turn():
                self.outcome = "Black Wins! (white resigned)"
            else:
                self.outcome = "White Wins! (black resigned)"
            return True
        return False

    def is_ending_condition(self):
        if self.is_whites_turn():
            opponent_king = self.blackKing
        else:
            opponent_king = self.whiteKing
        if self.is_checkmate(opponent_king):
            return True
        if self.is_fifty_moves_without_pawn_move_or_capture():
            return True
        if self.is_three_fold_repetition():
            return True
        if self.is_resignation():
            return True
        if self.is_stalemate(opponent_king):
            return True
        return False

    def is_whites_turn(self):
        return self.sideToMove == 0

    def is_blacks_turn(self):
        return self.sideToMove == 1

    def is_square_defended_by_opponent(self, square, color_of_attacking_side):
        if color_of_attacking_side == Pieces.Piece.WHITE:
            piece_list = self.white_pieces_on_the_board
        else:
            piece_list = self.black_pieces_on_the_board
        for piece in piece_list:
            if type(piece) == Pieces.Pawn:
                if piece.is_valid_square_to_attack(self, square) and piece.is_defending_square(self, square):
                    return True
            else:
                if piece.is_defending_square(self, square):
                    return True
        return False

    def is_square_under_attack(self, square, color_of_attacking_side, include_king=True):
        if color_of_attacking_side == Pieces.Piece.WHITE:
            piece_list = self.white_pieces_on_the_board
        else:
            piece_list = self.black_pieces_on_the_board
        for piece in piece_list:
            if not include_king and type(piece) == Pieces.King:
                continue
            if type(piece) == Pieces.Pawn:
                if piece.is_valid_square_to_attack(self, square) and piece.is_legal_move(self, square):
                    return True
            else:
                if piece.is_legal_move(self, square):
                    return True
        return False

    def is_square_under_attack_from_non_king_piece(self, square, color_of_attacking_side):
        return self.is_square_under_attack(square, color_of_attacking_side, False)

    def can_move_to_square_with_non_king_piece(self, square, color_to_move):
        if color_to_move == Pieces.Piece.WHITE:
            piece_list = self.white_pieces_on_the_board
            king_to_validate = self.whiteKing
        else:
            piece_list = self.black_pieces_on_the_board
            king_to_validate = self.blackKing
        for piece in piece_list:
            if type(piece) == Pieces.King:
                continue
            if piece.is_legal_move(self, square) \
                    and not self.is_king_in_check_after_simulating_move(piece.current_square, square, king_to_validate):
                return True
        return False

    def __str__(self):
        board_as_str = ''
        for i, row in enumerate(self.board[::-1]):
            board_as_str += str(8 - i) + ' | ' + ' '.join(map(str, row))
            board_as_str += '\n'
        board_as_str += '   ' + '-' * 16 + '\n'
        board_as_str += '    '  # position forthcoming column labels
        for col in self.ALL_COLS:
            board_as_str += col + ' '
        return board_as_str[:-1]
