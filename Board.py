import Pieces
from copy import deepcopy

# board
# Interfaces:
#   update_board_position(legalMove) # legalMove of the form e2e4
#   get_fen()
#
# Helpers
# Notes:
#     squares are referred to by algebraic notation


class ChessBoard:
    ALL_COLS = 'abcdefgh'
    ALL_ROWS = '12345678'
    EMPTY_SQUARE = '~'
    def __init__(self):
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

    def is_king_in_check_after_simulating_move(self, originSquare, destinationSquare):
        copyOfBoard = deepcopy(self)
        copyOfBoard.make_move(originSquare, destinationSquare)

        if copyOfBoard.get_contents_of_square(destinationSquare).is_white_piece():
            kingToValidate = copyOfBoard.whiteKing
        else:
            kingToValidate = copyOfBoard.blackKing

        return copyOfBoard.is_king_in_check(kingToValidate)

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

        kingToValidate = self.whiteKing if originPiece.is_white_piece() else self.blackKing
        if self.is_king_in_check_after_simulating_move(originSquare, destinationSquare):
            return False

        return True

    def execute_move(self, originSquare, destinationSquare):
        if self.is_valid_move(originSquare, destinationSquare):
            self.make_move(originSquare, destinationSquare)

        # Check ending conditions:
        #     Checkmate
        #     Stalemate
        #     50 move rule
        #     3 fold repetition

    def make_move(self, originSquare, destinationSquare):
        # blindly makes move without regard to validation
        originPiece = self.get_contents_of_square(originSquare)
        originPiece.execute_move(self, destinationSquare)
        self.resetEnPassantTargetSquareIfNeeded()

    def get_move(self, originSquare, destinationSquare, pawnPromotion = None):
        raise NotImplementedError

    def simulate_get_move(self, originSquare, destinationSquare, pawnPromotion = None):
        if pawnPromotion:
            self.promotePawnTo = pawnPromotion
        self.execute_move(originSquare, destinationSquare)
        self.promotePawnTo = None

    def is_king_in_check(self, kingPiece):
        return self.is_square_under_attack(kingPiece.current_square, kingPiece.get_color_of_opponent_side())

    def is_square_under_attack(self, square, colorOfAttackingSide):
        if colorOfAttackingSide == Pieces.Piece.WHITE:
            pieceList = self.white_pieces_on_the_board
        else:
            pieceList = self.black_pieces_on_the_board
        for piece in pieceList:
            if piece.is_legal_move(self, square):
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
