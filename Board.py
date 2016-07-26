import Pieces
from copy import deepcopy

# Notes:
#     squares are referred to by algebraic notation


class ChessBoard:
    ALL_COLS = 'abcdefgh'
    ALL_ROWS = '12345678'
    EMPTY_SQUARE = '~'
    def __init__(self):
        self.is_game_over = False
        self.most_resent_player_has_resigned = False
        self.past_game_states = {}
        self.fifty_move_counter = 0
        self.outcome = None
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
        self.promotePawnTo = None # q, r, n or b.  To be set in a "get_move" type method and used in Pieces.Pawn
        self.create_starting_position()
        self.whiteKing = self.get_contents_of_square('e1')
        self.blackKing = self.get_contents_of_square('e8')
        self.sideToMove = 0   # 0 = white, 1 = black

    def create_starting_position(self):
        self.create_empty_board()
        self.add_standard_initial_pieces_to_board()

    def create_empty_board(self):
        self.board = []
        for row in range(8):
            rowList = []
            for col in self.ALL_COLS:
                rowList.append(self.EMPTY_SQUARE)
            self.board.append(rowList)

    def add_piece_to_board(self, piece, color, squares):
        for sq in squares:
            assert self.is_square_on_board(sq)
            pieceToAdd = piece(color, sq)
            self.update_square_with_piece(pieceToAdd, sq)
            if pieceToAdd.is_white_piece():
                self.white_pieces_on_the_board.append(pieceToAdd)
            elif pieceToAdd.is_black_piece():
                self.black_pieces_on_the_board.append(pieceToAdd)

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
        rowAsChr = chr(row + 49)
        colAsChr = chr(col + 97)
        square = colAsChr + rowAsChr
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

    def is_valid_square(self, square):
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

    def is_coordinate_on_board(self, row, col):
        if (0 <= row <= 7) and (0 <= col <= 7):
            return True
        return False

    def assign_value_to_square(self, value, square):
        row, col = self.get_row_and_col_coordinates_from_square(square)
        self.board[row][col] = value

    def clear_square(self, square):
        if not self.is_square_empty(square):
            self.assign_value_to_square(self.EMPTY_SQUARE, square)

    def update_en_passant_target_square(self, newEnPassantSquare):
        self.enPassantTargetSquare = newEnPassantSquare

    def update_square_with_piece(self, piece, square):
        if not self.is_square_empty(square):
            self.move_piece_from_on_the_board_to_off_the_board(self.get_contents_of_square(square))
        self.clear_square(square)
        self.assign_value_to_square(piece, square)

    def get_contents_of_square(self, square):
        row, col = self.get_row_and_col_coordinates_from_square(square)
        return self.board[row][col]

    def is_one_square_away(self, originSquare, destinationSquare):
        originSqRow, originSqCol = self.get_row_and_col_coordinates_from_square(originSquare)
        destSqRow, destSqCol = self.get_row_and_col_coordinates_from_square(destinationSquare)
        return abs(originSqRow - destSqRow) <= 1 and abs(originSqCol-destSqCol) <= 1

    def is_empty_diagonal_from(self, originSquare, destinationSquare):
        # these should already be checked
        assert self.is_square_on_board(originSquare) and self.is_square_on_board(destinationSquare)
        assert originSquare != destinationSquare

        originSqRow, originSqCol = self.get_row_and_col_coordinates_from_square(originSquare)
        destSqRow, destSqCol = self.get_row_and_col_coordinates_from_square(destinationSquare)

        # check if diagonal
        rowDif = abs(originSqRow-destSqRow)
        if rowDif != abs(originSqCol-destSqCol):
            return False

        # now check if that diagonal is empty
        if originSqRow > destSqRow:
            # count down
            inbetweenSqRowCoords = range(originSqRow-1, destSqRow, -1)
        else:
            # count up
            inbetweenSqRowCoords = range(originSqRow+1, destSqRow)

        if originSqCol > destSqCol:
            # count down
            inbetweenSqColCoords = range(originSqCol-1, destSqCol, -1)
        else:
            # count up
            inbetweenSqColCoords = range(originSqCol+1, destSqCol)

        assert len(inbetweenSqRowCoords) == len(inbetweenSqColCoords)

        for i in range(len(inbetweenSqRowCoords)):
            if not self.is_coordinate_empty(inbetweenSqRowCoords[i], inbetweenSqColCoords[i]):
                return False
        return True

    def is_empty_orthogonal_from(self, originSquare, destinationSquare):
        # these should already be checked
        assert self.is_square_on_board(originSquare) and self.is_square_on_board(destinationSquare)
        assert originSquare != destinationSquare

        originSqRow, originSqCol = self.get_row_and_col_coordinates_from_square(originSquare)
        destSqRow, destSqCol = self.get_row_and_col_coordinates_from_square(destinationSquare)

        if originSqRow == destSqRow:
            fixedRow = originSqRow
            rangeToCheck = range(min(originSqCol, destSqCol)+1, max(originSqCol, destSqCol))
            for col in rangeToCheck:
                if not self.is_coordinate_empty(fixedRow, col):
                    return False
        elif originSqCol == destSqCol:
            fixedCol = originSqCol
            rangeToCheck = range(min(originSqRow, destSqRow)+1, max(originSqRow, destSqRow))
            for row in rangeToCheck:
                if not self.is_coordinate_empty(row, fixedCol):
                    return False
        else:
            return False    # the squares are not orthogonal
        return True

    def resetEnPassantTargetSquareIfNeeded(self):
        # reset the enpassant square (makes sure it's only available for one turn)
        if self.resetEnPassantTargetSquare:
            self.update_en_passant_target_square('')
            self.resetEnPassantTargetSquare = False
        if self.enPassantTargetSquare != '':
            self.resetEnPassantTargetSquare = True

    def is_king_in_check_after_simulating_move(self, originSquare, destinationSquare, kingToValidate):
        copyOfBoard = deepcopy(self)
        copyOfBoard.make_move(originSquare, destinationSquare)

        if kingToValidate.current_square != originSquare:
            squareOfKingAfterMove = kingToValidate.current_square
        else:
            squareOfKingAfterMove = destinationSquare

        return copyOfBoard.is_square_under_attack(squareOfKingAfterMove, kingToValidate.get_color_of_opponent_side())

    def is_valid_move(self, originSquare, destinationSquare):
        # This is the super method that must incorporate all of the rules of the game
        # possible overlap between this and execute_move method.
        # perhaps this is better handled in the game/rules class (or at least the non-piece specific parts)

        if originSquare == destinationSquare:
            return False

        # is legal move from the piece's perspective:
        if self.is_square_empty(originSquare):
            return False
        originPiece = self.get_contents_of_square(originSquare)
        if not originPiece.is_legal_move(self, destinationSquare):
            return False

        return not self.is_king_in_check_after_simulating_move(originSquare, destinationSquare, self.get_king_of_side_that_is_moving())

    def get_king_of_side_that_is_moving(self):
        if self.is_whites_turn():
            return self.whiteKing
        return self.blackKing

    def update_past_game_states(self):
        gameState = str(self)
        if gameState in self.past_game_states:
            self.past_game_states[gameState] += 1
        else:
            self.past_game_states[gameState] = 1

    def is_non_reversible_move(self, originSquare, destinationSquare):
        # pawn move
        if type(self.get_contents_of_square(originSquare)) == Pieces.Pawn:
            return True
        # or capture
        return not self.is_square_empty(destinationSquare)

    def get_path_traversal_incrementer(self, startSq, middleSq):
        startRow, startCol = self.get_row_and_col_coordinates_from_square(startSq)
        middleRow, middleCol = self.get_row_and_col_coordinates_from_square(middleSq)

        rowInc = middleRow - startRow
        colInc = middleCol - startCol

        dividerToGetBackToOneToOneRatio = max(abs(rowInc), abs(colInc))
        rowInc /= dividerToGetBackToOneToOneRatio
        colInc /= dividerToGetBackToOneToOneRatio

        return (rowInc, colInc)

    def get_coordinates_after_applying_traversal_incrementer(self, coordinates, incrementer):
        return (coordinates[0] + incrementer[0], coordinates[1] + incrementer[1])

    def get_next_piece_along_path(self, startSq, middleSq):
        traversalIncrementer = self.get_path_traversal_incrementer(startSq, middleSq)
        nextPosCoordinates = self.get_coordinates_after_applying_traversal_incrementer(
            self.get_row_and_col_coordinates_from_square(middleSq), traversalIncrementer)
        while self.is_coordinate_on_board(nextPosCoordinates[0], nextPosCoordinates[1]):
            if self.is_square_empty(self.get_square_from_row_and_col_coordinates(nextPosCoordinates[0], nextPosCoordinates[1])):
                nextPosCoordinates = self.get_coordinates_after_applying_traversal_incrementer(nextPosCoordinates, traversalIncrementer)
            else:
                return self.get_contents_of_square(self.get_square_from_row_and_col_coordinates(nextPosCoordinates[0], nextPosCoordinates[1]))
        return self.EMPTY_SQUARE   # this signifies that nothing is along path and the end of the board has been reached

    def update_squares_attacking_king(self, lastMovedPieceOriginSquare, lastMovedPieceCurrentSquare):
        squaresFromWhichCheckIsBeingDelivered = []

        lastMovedPiece = self.get_contents_of_square(lastMovedPieceCurrentSquare)
        if lastMovedPiece.is_white_piece():
            opponentKing = self.blackKing
        else:
            opponentKing = self.whiteKing

        # regular check: is the king square a valid move from the lastMovedPieceCurrentSquare?
        if lastMovedPiece.is_legal_move(self, opponentKing.current_square):
            squaresFromWhichCheckIsBeingDelivered.append(lastMovedPieceCurrentSquare)

        # discover check?
        if self.is_empty_diagonal_from(opponentKing.current_square, lastMovedPieceOriginSquare):
            posPieceAlongPath = self.get_next_piece_along_path(opponentKing.current_square, lastMovedPieceOriginSquare)
            if posPieceAlongPath != self.EMPTY_SQUARE \
                    and posPieceAlongPath.color != opponentKing.color \
                    and (type(posPieceAlongPath) == Pieces.Queen or type(posPieceAlongPath) == Pieces.Bishop):
                squaresFromWhichCheckIsBeingDelivered.append(posPieceAlongPath.current_square)
        elif self.is_empty_orthogonal_from(opponentKing.current_square, lastMovedPieceOriginSquare):
            posPieceAlongPath = self.get_next_piece_along_path(opponentKing.current_square, lastMovedPieceOriginSquare)
            if posPieceAlongPath != self.EMPTY_SQUARE \
                    and posPieceAlongPath.color != opponentKing.color \
                    and (type(posPieceAlongPath) == Pieces.Queen or type(posPieceAlongPath) == Pieces.Rook):
                squaresFromWhichCheckIsBeingDelivered.append(posPieceAlongPath.current_square)

        if self.is_whites_turn():
            self.squaresAttackingBlackKing = squaresFromWhichCheckIsBeingDelivered
            self.squaresAttackingWhiteKing = []  # if we made it this far, the king wasn't in check, so reset
        else:
            self.squaresAttackingWhiteKing = squaresFromWhichCheckIsBeingDelivered
            self.squaresAttackingBlackKing = []

    def is_king_in_check(self, king):
        if king.is_white_piece():
            return len(self.squaresAttackingWhiteKing) != 0
        return len(self.squaresAttackingBlackKing) != 0

    def update_side_to_move(self):
        self.sideToMove ^= 1

    def execute_move(self, originSquare, destinationSquare):
        if self.is_valid_move(originSquare, destinationSquare):
            self.make_move(originSquare, destinationSquare)
            # game state related housekeeping
            self.update_past_game_states()
            self.update_squares_attacking_king(originSquare, destinationSquare)
            if self.is_non_reversible_move(originSquare, destinationSquare):
                self.fifty_move_counter = 0
            else:
                self.fifty_move_counter += .5  # half move
            if self.is_ending_condition():
                self.is_game_over = True
            else:
                self.update_side_to_move()

    def make_move(self, originSquare, destinationSquare):
        # blindly makes move without regard to validation
        originPiece = self.get_contents_of_square(originSquare)
        originPiece.execute_move(self, destinationSquare)
        self.resetEnPassantTargetSquareIfNeeded()

    def attempt_to_make_move(self, move):
        # move is of the form e2e4 or e7e8q
        if move == 'resign':
            self.most_resent_player_has_resigned = True
            return True

        if type(move) != str:
            return False

        if len(move) < 4 or len(move) > 5:
            return False

        originSquare = move[:2]
        destinationSquare = move[2:4]
        if len(move) == 5:
            self.promotePawnTo = move[-1]

        if not self.is_valid_square(originSquare) or not self.is_valid_square(destinationSquare):
            return False

        self.execute_move(originSquare, destinationSquare)
        self.promotePawnTo = None
        return True

    def simulate_get_move(self, originSquare, destinationSquare, pawnPromotion = None):
        if pawnPromotion:
            self.promotePawnTo = pawnPromotion
        self.execute_move(originSquare, destinationSquare)
        self.promotePawnTo = None

    def get_squares_along_path(self, startSq, endSq):
        squares = []
        incrementer = self.get_path_traversal_incrementer(startSq, endSq)
        startingCoords = self.get_row_and_col_coordinates_from_square(startSq)
        endingCoords = self.get_row_and_col_coordinates_from_square(endSq)
        posCoords = self.get_coordinates_after_applying_traversal_incrementer(startingCoords, incrementer)
        while posCoords != endingCoords:
            assert self.is_coordinate_empty(posCoords[0], posCoords[1])
            squares.append(self.get_square_from_row_and_col_coordinates(posCoords[0], posCoords[1]))
            posCoords = self.get_coordinates_after_applying_traversal_incrementer(posCoords, incrementer)
        return squares

    def is_checkmate(self, king):
        if not self.is_king_in_check(king):
            return False

        if king.is_white_piece():
            squaresAttackingKing = self.squaresAttackingWhiteKing
        else:
            squaresAttackingKing = self.squaresAttackingBlackKing

        # King move (for single check and double check)
        for posSqToMoveTo in king.get_possible_moves(self):
            if not self.is_king_in_check_after_simulating_move(king.current_square, posSqToMoveTo, king):
                return False

        if len(squaresAttackingKing) == 1:
            squareOfAttackingPiece = squaresAttackingKing[0]
            # capture square
            if self.is_square_under_attack_from_non_king_piece(squareOfAttackingPiece, king.get_color_of_opponent_side()):
                return False

            # block path
            attackingPiece = self.get_contents_of_square(squareOfAttackingPiece)
            if type(attackingPiece) == Pieces.Queen or type(attackingPiece) == Pieces.Bishop or type(attackingPiece) == Pieces.Rook:
                squaresAlongPath = self.get_squares_along_path(king.current_square, squareOfAttackingPiece)
                for sq in squaresAlongPath:
                    if self.can_move_to_square_with_non_king_piece(sq, king.color):
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

        # no legal moves
        if king.get_possible_moves(self):
            return False

        self.outcome = "Stalemate! Draw"
        return False

    def is_fifty_moves_without_pawn_move_or_capture(self):
        if abs(self.fifty_move_counter - 50) < .001:    # fifty_move_counter is double...
            self.outcome = "Draw"
            return True
        return False

    def is_three_fold_repetition(self):
        if str(self) not in self.past_game_states:
            return False
        if self.past_game_states[str(self)] == 3:
            self.outcome = "Draw"
            return True
        return False

    def is_resignation(self):
        return self.most_resent_player_has_resigned

    def is_ending_condition(self):
        if self.is_whites_turn():
            opponentKing = self.blackKing
        else:
            opponentKing = self.whiteKing
        if self.is_checkmate(opponentKing):
            return True
        if self.is_fifty_moves_without_pawn_move_or_capture():
            return True
        if self.is_three_fold_repetition():
            return True
        if self.is_resignation():
            return True
        if self.is_checkmate(opponentKing):
            return True
        if self.is_stalemate(opponentKing):
            return True
        return False

    def is_whites_turn(self):
        return self.sideToMove == 0

    def is_blacks_turn(self):
        return self.sideToMove == 1

    def is_square_under_attack(self, square, colorOfAttackingSide, includeKing=True):
        if colorOfAttackingSide == Pieces.Piece.WHITE:
            pieceList = self.white_pieces_on_the_board
            kingToValidate = self.whiteKing
        else:
            pieceList = self.black_pieces_on_the_board
            kingToValidate = self.blackKing
        for piece in pieceList:
            if not includeKing and type(piece) == Pieces.King:
                continue
            if type(piece) == Pieces.Pawn:
                if piece.is_valid_square_to_attack(self, square) and self.is_king_in_check_after_simulating_move(piece.current_square, square, kingToValidate):
                    return True
            else:
                if piece.is_legal_move(self, square):
                    return True
        return False

    def is_square_under_attack_from_non_king_piece(self, square, colorOfAttackingSide):
        return self.is_square_under_attack(square, colorOfAttackingSide, False)

    def can_move_to_square_with_non_king_piece(self, square, colorToMove):
        if colorToMove == Pieces.Piece.WHITE:
            pieceList = self.white_pieces_on_the_board
            kingToValidate = self.whiteKing
        else:
            pieceList = self.black_pieces_on_the_board
            kingToValidate = self.blackKing
        for piece in pieceList:
            if type(piece) == Pieces.King:
                continue
            if piece.is_legal_move(self, square) and not self.is_king_in_check_after_simulating_move(piece.current_square, square, kingToValidate):
                return True
        return False

    def __str__(self):
        boardAsStr = ''
        for i, row in enumerate(self.board[::-1]):
            boardAsStr += str(8-i) + ' | ' + ' '.join(map(str, row))
            boardAsStr += '\n'
        boardAsStr += '   ' + '-' * 16 + '\n'
        boardAsStr += '    '  # position forthcoming column labels
        for col in self.ALL_COLS:
            boardAsStr += col + ' '
        return boardAsStr[:-1]

b = ChessBoard()
print b
