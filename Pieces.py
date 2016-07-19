# piece


class Piece(object):
    WHITE = 'w'
    BLACK = 'b'
    WHITE_PAWN_STARTING_ROW = 1
    BLACK_PAWN_STARTING_ROW = 6
    def __init__(self, color, currentSquare = None):
        self.color = color
        assert self.is_white_piece() or self.is_black_piece()
        self.current_square = currentSquare

    def is_white_piece(self):
        return self.color == self.WHITE

    def is_black_piece(self):
        return self.color == self.BLACK

    def is_opponent_piece(self, piece):
        return self.color != piece.color

    def is_square_occupied_by_opponent_piece(self, board, square):
        if board.is_square_empty(square):
            return False
        return self.is_opponent_piece(board.get_contents_of_square(square))

    def all_possible_moves(self, board):
        raise NotImplementedError

    def all_legal_moves(self, board):
        raise NotImplementedError

    def is_legal_move(self, board, destination_square):
        raise NotImplementedError

    def is_viable_square_to_move_to(self, board, destination_square):
        if not board.is_square_on_board(destination_square):
            return False

        contentsOfDestinationSquare = board.get_contents_of_square(destination_square)
        if contentsOfDestinationSquare != board.EMPTY_SQUARE and contentsOfDestinationSquare.color == self.color:
            return False

        if self.current_square == destination_square:
            return False

        return True

    def is_legal_game_state(self, board):
        # To final check for all legal piece moves is whether or not the king of the same color is now in check
        # if a move leaves that color's king in check, it is illegal
        # This may better fit into the Rules class along with other general "clean up" checks, like 50 move rule, 3 fold, etc.
        # Some sort of game state function, that is determined separate form the mechanics of the individual piece.
        # Noting this here but will moved else where and relayed back.
        pass

    def __str__(self):
        raise NotImplementedError


class Pawn(Piece):
    # Move forward one if square in front is empty
    # move forward two if on starting square and both squares in front are empty
    # en passant:
    #     if moving forward two, create an en passant square on the bypassed square
    #     if attacking an en passant target square, make sure to clear the square containing the opponents pawn
    #         (different square than where attacking pawn ends up)
    # if an opponent's piece is diagonal, the pawn may move one square diagonally and replace the piece on that square.
    # if moving to last row, promote piece to Queen, Rook, Knight or Bishop.  All are valid moves, player should be prompted to choose.
    # any pawn move should reset the 50 move game counter.  (This might be better handled in the Rules class or FEN)
    def is_on_starting_square(self, board):
        currentRow = board.get_row_number_from_square(self.current_square)
        if self.is_white_piece():
            return currentRow == self.WHITE_PAWN_STARTING_ROW
        return currentRow == self.BLACK_PAWN_STARTING_ROW

    def is_forward_move(self, board, destination_square):
        if self.is_white_piece():
            return board.get_row_number_from_square(self.current_square) < board.get_row_number_from_square(destination_square)
        else:
            return board.get_row_number_from_square(self.current_square) > board.get_row_number_from_square(destination_square)

    def is_forward_num_of_squares(self, board, destination_square, numSquares):
        if not self.is_forward_move(board, destination_square):
            return False
        return abs(board.get_row_number_from_square(self.current_square) - board.get_row_number_from_square(destination_square)) == numSquares

    def is_forward_one_square(self, board, destination_square):
        return self.is_forward_num_of_squares(board, destination_square, 1)

    def is_forward_two_squares(self, board, destination_square):
        return self.is_forward_num_of_squares(board, destination_square, 2)

    def is_forward_and_diagonal_one_square(self, board, destination_square):
        if not self.is_forward_one_square(board, destination_square):
            return False
        return abs(board.get_col_from_square(self.current_square) - board.get_col_from_square(destination_square)) == 1

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
        if not self.is_viable_square_to_move_to(board, destination_square):
            return False

        if self.is_forward_one_square(board, destination_square):
            return board.is_square_empty(destination_square)

        elif self.is_forward_two_squares(board, destination_square):
            if not self.is_on_starting_square(board):
                return False
            if not board.is_empty_orthogonal_from(self.current_square, destination_square):
                return False
            if not board.is_square_empty(destination_square):
                return False
            board.update_en_passant_target_square(self.get_square_one_forward(board))
            return True

        return self.is_valid_square_to_attack(board, destination_square)

    def __str__(self):
        if self.color == 'w':
            return 'P'
        else:
            return 'p'


class Rook(Piece):
    # A rook may move forward, backward, or side to side until:
    #    it reaches the edge of the board
    #    it reaches the square just before a piece of its own color
    #    it reaches the square of an opponent's piece.  Replace the opponents piece with rook.
    # (castling is initiated by the king so does not need to be handled here.  The rook will be "teleported" to the other side of the king.

    def is_legal_move(self, board, destination_square):
        if not self.is_viable_square_to_move_to(board, destination_square):
            return False

        return board.is_empty_orthogonal_from(self.current_square, destination_square)

    def __str__(self):
        if self.color == 'w':
            return 'R'
        else:
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
    #     The target square contains an opponants piece

    def is_legal_move(self, board, destination_square):
        if not self.is_viable_square_to_move_to(board, destination_square):
            return False

        # is distance in L
        destRow, destCol = board.get_row_and_col_coordinates_from_square(destination_square)
        currRow, currCol = board.get_row_and_col_coordinates_from_square(self.current_square)

        if abs(currCol - destCol) == 1 and abs(currRow - destRow) == 2:
            return True
        if abs(currCol - destCol) == 2 and abs(currRow - destRow) == 1:
            return True

        return False

    def __str__(self):
        if self.color == 'w':
            return 'N'
        else:
            return 'n'


class Bishop(Piece):
    # The bishop moves diaganoally on it's own color until it reaches:
    #     The edge of the board
    #     a square directly before a piece of its own color
    #     a square containing an opponent's piece.

    def is_diagonal_from(self, destination_square):
        pass

    def is_legal_move(self, board, destination_square):
        if not self.is_viable_square_to_move_to(board, destination_square):
            return False

        return board.is_empty_diagonal_from(self.current_square, destination_square)

    def __str__(self):
        if self.color == 'w':
            return 'B'
        else:
            return 'b'


class Queen(Piece):
    # The queens can move to any square that a bishop or rook can

    def is_legal_move(self, board, destination_square):
        if not self.is_viable_square_to_move_to(board, destination_square):
            return False

        # check for either legal bishop or rook move
        if board.is_empty_diagonal_from(self.current_square, destination_square):
            return True
        if board.is_empty_orthogonal_from(self.current_square, destination_square):
            return True

        return False

    def __str__(self):
        if self.color == 'w':
            return 'Q'
        else:
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

    def is_legal_move(self, board, destination_square):
        # does not take into consideration: check, checkmate, castling
        if not self.is_viable_square_to_move_to(board, destination_square):
            return False
        return board.is_one_square_away(self.current_square, destination_square)

    def __str__(self):
        if self.color == 'w':
            return 'K'
        else:
            return 'k'


