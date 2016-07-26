# piece


class Piece(object):
    WHITE = 'w'
    BLACK = 'b'
    def __init__(self, color, currentSquare = None):
        self.color = color
        assert self.is_white_piece() or self.is_black_piece()
        self.current_square = currentSquare

    # def __eq__(self, other):
    #     return type(self) == other

    # abstract methods
    def all_possible_moves(self, board):
        raise NotImplementedError

    def all_legal_moves(self, board):
        raise NotImplementedError

    def is_legal_move(self, board, destination_square):
        raise NotImplementedError

    def execute_move(self, board, destination_square):
        self.special_move_maintenance_before_executing_move(board, destination_square)
        originSquare = self.current_square
        pieceToMove = board.get_contents_of_square(originSquare)
        board.update_square_with_piece(pieceToMove, destination_square)
        pieceToMove.current_square = destination_square
        board.clear_square(originSquare)

    def special_move_maintenance_before_executing_move(self, board, destination_square):
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
    WHITE_PAWN_STARTING_ROW = 1
    BLACK_PAWN_STARTING_ROW = 6

    def special_move_maintenance_before_executing_move(self, board, destination_square):
        if destination_square == board.enPassantTargetSquare:
            # remove the pawn that created the en passant target square
            pawnToClearRow = board.get_row_number_from_square(self.current_square)
            pawnToClearCol = board.get_col_number_from_square(destination_square)
            board.clear_square(board.get_square_from_row_and_col_coordinates(pawnToClearRow, pawnToClearCol))

        elif self.is_forward_two_squares(board, destination_square) and self.is_on_starting_square(board):
            board.update_en_passant_target_square(self.get_square_one_forward(board))
            board.resetEnPassantTargetSquare = False  # to account for back to back en passant making moves

        elif self.is_pawn_on_final_row(board, destination_square):
            newPieceColor = self.color
            newPieceSquare = self.current_square
            promoteTo = board.promotePawnTo
            if promoteTo == 'r':
                newPiece = Rook
            elif promoteTo == 'n':
                newPiece = Knight
            elif promoteTo == 'b':
                newPiece = Bishop
            else:   # default to 'q' (queen) if no selection or if invalid
                newPiece = Queen

            board.add_piece_to_board(newPiece, newPieceColor, [newPieceSquare])

    def is_pawn_on_final_row(self, board, square):
        return abs(board.get_row_number_from_square(square) - self.get_starting_row()) == 6

    def get_starting_row(self):
        if self.is_white_piece():
            return self.WHITE_PAWN_STARTING_ROW
        return self.BLACK_PAWN_STARTING_ROW

    def is_on_starting_square(self, board):
        currentRow = board.get_row_number_from_square(self.current_square)
        return currentRow == self.get_starting_row()

    def is_forward_move(self, board, destination_square):
        if self.is_white_piece():
            return board.get_row_number_from_square(self.current_square) < board.get_row_number_from_square(destination_square)
        else:
            return board.get_row_number_from_square(self.current_square) > board.get_row_number_from_square(destination_square)

    def is_forward_num_of_squares(self, board, destination_square, numSquares):
        if not self.is_forward_move(board, destination_square):
            return False
        # check if any movement besides straight forward
        if abs(board.get_col_number_from_square(self.current_square) - board.get_col_number_from_square(destination_square)) != 0:
            return False
        return abs(board.get_row_number_from_square(self.current_square) - board.get_row_number_from_square(destination_square)) == numSquares

    def is_forward_one_square(self, board, destination_square):
        return self.is_forward_num_of_squares(board, destination_square, 1)

    def is_forward_two_squares(self, board, destination_square):
        return self.is_forward_num_of_squares(board, destination_square, 2)

    def is_forward_and_diagonal_one_square(self, board, destination_square):
        if not self.is_forward_move(board, destination_square):
            return False
        if abs(board.get_row_number_from_square(self.current_square) - board.get_row_number_from_square(destination_square)) != 1:
            return False
        if abs(board.get_col_number_from_square(self.current_square) - board.get_col_number_from_square(destination_square)) != 1:
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
    isFirstMove = True

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
    isFirstMove = True
    transformations = [(1, 1), (1, 0), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, 0), (-1, -1)]
    def special_move_maintenance_before_executing_move(self, board, destination_square):
        if self.isFirstMove:
            if self.is_legal_castling_move(board, destination_square):
                newRookSquare = self.get_square_king_passes_over_when_castling(destination_square)
                oldRookSquare = self.get_old_rook_square(destination_square)
                rookPiece = board.get_contents_of_square(oldRookSquare)
                board.clear_square(oldRookSquare)
                board.update_square_with_piece(rookPiece, newRookSquare)
                rookPiece.current_square = destination_square

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

    def get_square_king_passes_over_when_castling(self, destination_square):
        assert destination_square in ('g1', 'c1', 'g8', 'c8')
        if destination_square == 'g1':
            return 'f1'
        elif destination_square == 'c1':
            return 'd1'
        elif destination_square == 'g8':
            return 'f8'
        elif destination_square == 'c8':
            return 'd8'

    def get_old_rook_square(self, destination_square):
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

        if board.is_square_under_attack(self.get_square_king_passes_over_when_castling(destination_square), self.get_color_of_opponent_side()):
            return False
        # (destination square check will be handled by game logic that checks if the final position is in check)
        return True

    def is_legal_move(self, board, destination_square):
        # does not take into consideration: check, checkmate, castling
        if not self.is_viable_square_to_move_to(board, destination_square):
            return False

        if board.is_one_square_away(self.current_square, destination_square):
            return True

        # check for castle
        return self.is_legal_castling_move(board, destination_square)

    def get_possible_moves(self, board):
        possibleSquares = []
        currentCoordinates = board.get_row_and_col_coordinates_from_square(self.current_square)
        for trans in self.transformations:
            newCoordRow, newCoordCol = board.get_coordinates_after_applying_traversal_incrementer(currentCoordinates, trans)
            if not board.is_coordinate_on_board(newCoordRow, newCoordCol):
                continue
            posSquare = board.get_square_from_row_and_col_coordinates(newCoordRow, newCoordCol)
            if self.is_legal_move(board, posSquare):
                possibleSquares.append(posSquare)
        return possibleSquares


    def __str__(self):
        if self.color == 'w':
            return 'K'
        else:
            return 'k'

