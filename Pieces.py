# piece


class Piece(object):
    WHITE = 'w'
    BLACK = 'b'

    def __init__(self, color, current_square=None):
        self.color = color
        assert self.is_white_piece() or self.is_black_piece()
        self.current_square = current_square

    # abstract method
    def get_possible_squares_to_move_to(self, board):
        raise NotImplementedError

    # abstract method
    def is_legal_move(self, board, destination_square):
        raise NotImplementedError

    # abstract method
    def is_defending_square(self, board, square):
        raise NotImplementedError

    # abstract method
    def can_move_to_square(self, board, square, ensure_own_king_safety=True):
        raise NotImplementedError

    def all_legal_squares_to_move_to(self, board):
        possible_squares = self.get_possible_squares_to_move_to(board)
        legal_squares = []
        if self.is_white_piece():
            king_to_verify = board.whiteKing
        else:
            king_to_verify = board.blackKing
        for sq in possible_squares:
            if not board.is_square_on_board(sq):
                continue
            if self.is_legal_move(board, sq) \
                    and not board.is_king_in_check_after_simulating_move(
                        self.current_square, sq, king_to_verify):
                legal_squares.append(sq)
        return legal_squares

    def execute_move(self, board, destination_square):
        self.special_move_maintenance_before_executing_move(board, destination_square)
        origin_square = self.current_square
        piece_to_move = board.get_contents_of_square(origin_square)
        board.update_square_with_piece(piece_to_move, destination_square)
        piece_to_move.current_square = destination_square
        board.clear_square(origin_square)

    def special_move_maintenance_before_executing_move(self, board, destination_square):
        # override where needed, otherwise no maintenance will take place
        pass

    def is_white_piece(self):
        return self.color == self.WHITE

    def is_black_piece(self):
        return self.color == self.BLACK

    def get_color_of_opponent_side(self):
        if self.is_white_piece():
            return self.BLACK
        return self.WHITE

    def is_opponent_piece(self, piece):
        return self.color != piece.color

    def is_square_occupied_by_opponent_piece(self, board, square):
        if board.is_square_empty(square):
            return False
        return self.is_opponent_piece(board.get_contents_of_square(square))

    def is_viable_square_to_move_to(self, board, destination_square):
        if not board.is_square_on_board(destination_square):
            return False

        contents_of_destination_square = board.get_contents_of_square(destination_square)
        if contents_of_destination_square != board.EMPTY_SQUARE and contents_of_destination_square.color == self.color:
            return False

        return self.current_square != destination_square

    def get_possible_squares_from_transformations(self, board, transformations):
        # used with Knight, Pawn and King
        possible_squares = []
        pos_sq = self.current_square
        for trans in transformations:
            pos_row, pos_col = board.get_row_and_col_coordinates_from_square(pos_sq)
            pos_row, pos_col = board.get_coordinates_after_applying_traversal_incrementer((pos_row, pos_col), trans)
            if board.is_coordinate_on_board(pos_row, pos_col):
                possible_squares.append(board.get_square_from_row_and_col_coordinates(pos_row, pos_col))
        return possible_squares

    def get_possible_moves_using_incrementer(self, board, incrementers_list):
        # used with Bishop, Rook and Queen
        possible_squares = []
        for incrementer in incrementers_list:
            pos_sq = self.current_square
            pos_row, pos_col = board.get_row_and_col_coordinates_from_square(pos_sq)
            pos_row, pos_col = board.get_coordinates_after_applying_traversal_incrementer(
                (pos_row, pos_col), incrementer)
            while self.continue_traversing_transformation(board, pos_row, pos_col):
                possible_squares.append(board.get_square_from_row_and_col_coordinates(pos_row, pos_col))
                pos_row, pos_col = board.get_coordinates_after_applying_traversal_incrementer(
                    (pos_row, pos_col), incrementer)

        return possible_squares

    def continue_traversing_transformation(self, board, pos_row, pos_col):
        return board.is_coordinate_on_board(pos_row, pos_col) \
               and (board.is_coordinate_empty(pos_row, pos_col)
                    or self.is_square_occupied_by_opponent_piece(
                        board, board.get_square_from_row_and_col_coordinates(pos_row, pos_col)))

    def is_own_king_safe_after_move(self, board, destination_square):
        if self.is_white_piece():
            king_to_verify = board.whiteKing
        else:
            king_to_verify = board.blackKing
        return not board.is_king_in_check_after_simulating_move(self.current_square, destination_square, king_to_verify)

    def get_name(self):
        raise NotImplementedError

    def __str__(self):
        if self.is_white_piece():
            return self.get_name().upper()
        return self.get_name().lower()


class Pawn(Piece):
    # Move forward one if square in front is empty
    # move forward two if on starting square and both squares in front are empty
    # en passant:
    #     if moving forward two, create an en passant square on the bypassed square
    #     if attacking an en passant target square, make sure to clear the square containing the opponents pawn
    #         (different square than where attacking pawn ends up)
    # if an opponent's piece is diagonal, the pawn may move one square diagonally and replace the piece on that square.
    # if moving to last row, promote piece to Queen, Rook, Knight or Bishop.
    # All are valid moves, player should be prompted to choose.
    # any pawn move should reset the 50 move game counter.  (This might be better handled in the Rules class or FEN)
    WHITE_PAWN_STARTING_ROW = 1
    BLACK_PAWN_STARTING_ROW = 6
    transformationsWhite = [(1, 0), (2, 0), (1, -1), (1, 1)]
    transformationsBlack = [(-1, 0), (-2, 0), (-1, -1), (-1, 1)]

    def special_move_maintenance_before_executing_move(self, board, destination_square):
        if destination_square == board.enPassantTargetSquare:
            # remove the pawn that created the en passant target square
            pawn_to_clear_row = board.get_row_number_from_square(self.current_square)
            pawn_to_clear_col = board.get_col_number_from_square(destination_square)
            board.update_square_with_piece(board.EMPTY_SQUARE,
                                           board.get_square_from_row_and_col_coordinates(
                                               pawn_to_clear_row, pawn_to_clear_col))

        elif self.is_forward_two_squares(board, destination_square) and self.is_on_starting_square(board):
            board.update_en_passant_target_square(self.get_square_one_forward(board))
            board.resetEnPassantTargetSquare = False  # to account for back to back en passant making moves

        elif self.is_pawn_on_final_row(board, destination_square):
            new_piece_color = self.color
            new_piece_square = self.current_square
            promote_to = board.promotePawnTo
            if promote_to == 'r':
                new_piece = Rook
            elif promote_to == 'n':
                new_piece = Knight
            elif promote_to == 'b':
                new_piece = Bishop
            else:  # default to 'q' (queen) if no selection or if invalid
                new_piece = Queen

            board.add_piece_to_board(new_piece, new_piece_color, [new_piece_square])

    def is_pawn_on_final_row(self, board, square):
        return abs(board.get_row_number_from_square(square) - self.get_starting_row()) == 6

    def get_starting_row(self):
        if self.is_white_piece():
            return self.WHITE_PAWN_STARTING_ROW
        return self.BLACK_PAWN_STARTING_ROW

    def is_on_starting_square(self, board):
        current_row = board.get_row_number_from_square(self.current_square)
        return current_row == self.get_starting_row()

    def is_forward_move(self, board, destination_square):
        if self.is_white_piece():
            return board.get_row_number_from_square(
                self.current_square) < board.get_row_number_from_square(destination_square)
        else:
            return board.get_row_number_from_square(
                self.current_square) > board.get_row_number_from_square(destination_square)

    def is_forward_num_of_squares(self, board, destination_square, num_squares):
        if not self.is_forward_move(board, destination_square):
            return False
        # check if any movement besides straight forward
        if abs(board.get_col_number_from_square(self.current_square)
                - board.get_col_number_from_square(destination_square)) != 0:
            return False
        return abs(board.get_row_number_from_square(self.current_square)
                   - board.get_row_number_from_square(destination_square)) == num_squares

    def is_forward_one_square(self, board, destination_square):
        return self.is_forward_num_of_squares(board, destination_square, 1)

    def is_forward_two_squares(self, board, destination_square):
        return self.is_forward_num_of_squares(board, destination_square, 2)

    def is_forward_and_diagonal_one_square(self, board, destination_square):
        if not self.is_forward_move(board, destination_square):
            return False
        if abs(board.get_row_number_from_square(self.current_square)
                - board.get_row_number_from_square(destination_square)) != 1:
            return False
        if abs(board.get_col_number_from_square(self.current_square)
                - board.get_col_number_from_square(destination_square)) != 1:
            return False
        return True

    def get_square_one_forward(self, board):
        row, col = board.get_row_and_col_coordinates_from_square(self.current_square)
        if self.is_white_piece():
            row += 1
        else:
            row -= 1
        return board.get_square_from_row_and_col_coordinates(row, col)

    def is_valid_square_to_attack(self, board, destination_square):
        if not self.is_forward_and_diagonal_one_square(board, destination_square):
            return False
        if self.is_square_occupied_by_opponent_piece(board, destination_square):
            return True
        return destination_square == board.enPassantTargetSquare

    def is_legal_move(self, board, destination_square):
        return self.can_move_to_square(board, destination_square)

    def is_defending_square(self, board, square):
        return self.can_move_to_square(board, square, False)

    def can_move_to_square(self, board, square, ensure_own_king_safety=True):
        if not self.is_viable_square_to_move_to(board, square):
            return False

        if self.is_forward_one_square(board, square):
            if not board.is_square_empty(square):
                return False
        elif self.is_forward_two_squares(board, square):
            if not self.is_on_starting_square(board):
                return False
            if not board.is_empty_orthogonal_from(self.current_square, square):
                return False
            if not board.is_square_empty(square):
                return False

        elif not self.is_valid_square_to_attack(board, square):
            return False

        if ensure_own_king_safety:
            return self.is_own_king_safe_after_move(board, square)
        return True

    def get_possible_squares_to_move_to(self, board):
        if self.is_white_piece():
            transformations = self.transformationsWhite
        else:
            transformations = self.transformationsBlack
        return self.get_possible_squares_from_transformations(board, transformations)

    def get_name(self):
        return 'p'


class Rook(Piece):
    # A rook may move forward, backward, or side to side until:
    #    it reaches the edge of the board
    #    it reaches the square just before a piece of its own color
    #    it reaches the square of an opponent's piece.  Replace the opponents piece with rook.
    # (castling is initiated by the king so does not need to be handled here.
    # The rook will be "teleported" to the other side of the king.
    isFirstMove = True
    orthogonalTransformationsIncrementers = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    def special_move_maintenance_before_executing_move(self, board, destination_square):
        # check to see if castling privileges should be revoked
        if self.isFirstMove:
            if self.current_square == 'a1':
                board.canWhiteCastleLong = False
            elif self.current_square == 'h1':
                board.canWhiteCastleShort = False
            elif self.current_square == 'a8':
                board.canBlackCastleLong = False
            elif self.current_square == 'h8':
                board.canBlackCastleShort = False
            self.isFirstMove = False

    def is_legal_move(self, board, destination_square):
        return self.can_move_to_square(board, destination_square)

    def is_defending_square(self, board, square):
        return self.can_move_to_square(board, square, False)

    def can_move_to_square(self, board, square, ensure_own_king_safety=True):
        if not self.is_viable_square_to_move_to(board, square):
            return False

        if not board.is_empty_orthogonal_from(self.current_square, square):
            return False

        if ensure_own_king_safety:
            return self.is_own_king_safe_after_move(board, square)
        return True

    def get_possible_squares_to_move_to(self, board):
        return self.get_possible_moves_using_incrementer(board, self.orthogonalTransformationsIncrementers)

    def get_name(self):
        return 'r'


class Knight(Piece):
    # A knight has 8 possible target squares it can jump to:
    #     Forward two then left or right one
    #     Left two then forward or backward one
    #     Right two then forward or backward one
    #     Backward two then left or right one
    # The knight may only jump to the above target squares if:
    #     The target square is on the board
    #     The target square is empty
    #     The target square contains an opponents piece
    transformations = [(1, 2), (1, -2), (2, 1), (2, -1), (-1, 2), (-1, -2), (-2, 1), (-2, -1)]

    def is_move_in_knight_shape(self, board, destination_square):
        # aka is move in "L" shape
        dest_row, dest_col = board.get_row_and_col_coordinates_from_square(destination_square)
        curr_row, curr_col = board.get_row_and_col_coordinates_from_square(self.current_square)

        if abs(curr_col - dest_col) == 1 and abs(curr_row - dest_row) == 2:
            return True
        if abs(curr_col - dest_col) == 2 and abs(curr_row - dest_row) == 1:
            return True

        return False

    def is_legal_move(self, board, destination_square):
        return self.can_move_to_square(board, destination_square)

    def is_defending_square(self, board, square):
        return self.can_move_to_square(board, square, False)

    def can_move_to_square(self, board, square, ensure_own_king_safety=True):
        if not self.is_viable_square_to_move_to(board, square):
            return False

        if not self.is_move_in_knight_shape(board, square):
            return False

        if ensure_own_king_safety:
            return self.is_own_king_safe_after_move(board, square)
        return True

    def get_possible_squares_to_move_to(self, board):
        return self.get_possible_squares_from_transformations(board, self.transformations)

    def get_name(self):
        return 'n'


class Bishop(Piece):
    # The bishop moves diagonally on it's own color until it reaches:
    #     The edge of the board
    #     a square directly before a piece of its own color
    #     a square containing an opponent's piece.
    diagonalTransformationIncrementers = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

    def is_diagonal_from(self, destination_square):
        pass

    def is_legal_move(self, board, destination_square):
        return self.can_move_to_square(board, destination_square)

    def is_defending_square(self, board, square):
        return self.can_move_to_square(board, square, False)

    def can_move_to_square(self, board, square, ensure_own_king_safety=True):
        if not self.is_viable_square_to_move_to(board, square):
            return False

        if not board.is_empty_diagonal_from(self.current_square, square):
            return False

        if ensure_own_king_safety:
            return self.is_own_king_safe_after_move(board, square)
        return True

    def get_possible_squares_to_move_to(self, board):
        return self.get_possible_moves_using_incrementer(board, self.diagonalTransformationIncrementers)

    def get_name(self):
        return 'b'


class Queen(Piece):
    # The queens can move to any square that a bishop or rook can
    diagonalAndOrthogonalTransformationIncrementers = [
        (1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]

    def is_move_along_empty_diagonal_or_orthogonal(self, board, destination_square):
        # check for either legal bishop or rook move
        if board.is_empty_diagonal_from(self.current_square, destination_square):
            return True
        if board.is_empty_orthogonal_from(self.current_square, destination_square):
            return True

    def is_legal_move(self, board, destination_square):
        return self.can_move_to_square(board, destination_square)

    def is_defending_square(self, board, square):
        return self.can_move_to_square(board, square, False)

    def can_move_to_square(self, board, square, ensure_own_king_safety=True):
        if not self.is_viable_square_to_move_to(board, square):
            return False

        if not self.is_move_along_empty_diagonal_or_orthogonal(board, square):
            return False

        if ensure_own_king_safety:
            return self.is_own_king_safe_after_move(board, square)
        return True

    def get_possible_squares_to_move_to(self, board):
        return self.get_possible_moves_using_incrementer(board, self.diagonalAndOrthogonalTransformationIncrementers)

    def get_name(self):
        return 'q'


class King(Piece):
    # The king can move one square in any direction.
    # castling:  The king can move two squares to the right or left,
    #            and place the rook located in the direction of that move on the square it passed over, IF:
    #      The king is not in check
    #      The king does not pass through check
    #      The king does not land in check
    #      The king has not already moved
    #      The rook it is moving toward has not already moved.
    #      There are no other pieces between the king and the rook (before castling is done)
    isFirstMove = True
    transformations = [(1, 1), (1, 0), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, 0), (-1, -1), (0, 2), (0, -2)]

    def special_move_maintenance_before_executing_move(self, board, destination_square):
        if self.isFirstMove:
            if self.is_legal_castling_move(board, destination_square):
                new_rook_square = self.get_square_king_passes_over_when_castling(destination_square)
                old_rook_square = self.get_old_rook_square(destination_square)
                rook_piece = board.get_contents_of_square(old_rook_square)
                board.clear_square(old_rook_square)
                board.update_square_with_piece(rook_piece, new_rook_square)
                rook_piece.current_square = new_rook_square

            self.isFirstMove = False
            if self.is_white_piece():
                board.canWhiteCastleShort = False
                board.canWhiteCastleLong = False
            else:
                board.canBlackCastleShort = False
                board.canBlackCastleLong = False

    def is_castling_short_still_available(self, board, destination_square):
        if self.is_white_piece() and self.current_square == 'e1' and destination_square == 'g1':
            return board.canWhiteCastleShort
        elif self.current_square == 'e8' and destination_square == 'g8':
            return board.canBlackCastleShort
        return False

    def is_castling_long_still_available(self, board, destination_square):
        if self.is_white_piece() and self.current_square == 'e1' and destination_square == 'c1':
            return board.canWhiteCastleLong
        elif self.current_square == 'e8' and destination_square == 'c8':
            return board.canBlackCastleLong
        return False

    def is_castling_still_available(self, board, destination_square):
        return self.is_castling_short_still_available(board, destination_square) \
               or self.is_castling_long_still_available(board, destination_square)

    @staticmethod
    def get_square_king_passes_over_when_castling(destination_square):
        assert destination_square in ('g1', 'c1', 'g8', 'c8')
        if destination_square == 'g1':
            return 'f1'
        elif destination_square == 'c1':
            return 'd1'
        elif destination_square == 'g8':
            return 'f8'
        elif destination_square == 'c8':
            return 'd8'

    @staticmethod
    def get_old_rook_square(destination_square):
        assert destination_square in ('g1', 'c1', 'g8', 'c8')
        if destination_square == 'g1':
            return 'h1'
        elif destination_square == 'c1':
            return 'a1'
        elif destination_square == 'g8':
            return 'h8'
        elif destination_square == 'c8':
            return 'a8'

    def is_legal_castling_move(self, board, destination_square):
        if not self.isFirstMove:
            return False
        if not self.is_castling_still_available(board, destination_square):
            return False

        if not board.is_empty_orthogonal_from(self.current_square, destination_square):
            return False

        if board.is_king_in_check(self):
            return False

        # (destination square check will be handled by game logic that checks if the final position is in check)

        return not board.is_square_under_attack(
            self.get_square_king_passes_over_when_castling(destination_square),
            self.get_color_of_opponent_side())

    def is_legal_move(self, board, destination_square):
        return self.can_move_to_square(board, destination_square)

    def is_defending_square(self, board, square):
        return self.can_move_to_square(board, square, False)

    def can_move_to_square(self, board, square, ensure_own_king_safety=True):
        # does not take into consideration: check, checkmate, castling
        if not self.is_viable_square_to_move_to(board, square):
            return False

        if not board.is_one_square_away(self.current_square, square) \
                and not self.is_legal_castling_move(board, square):
            return False

        if ensure_own_king_safety:
            return self.is_own_king_safe_after_move(board, square)
        return True

    def get_possible_squares_to_move_to(self, board):
        return self.get_possible_squares_from_transformations(board, self.transformations)

    def get_name(self):
        return 'k'
