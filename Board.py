import Pieces

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
        self.create_starting_position()

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
            self.update_square_with_piece(piece(color, sq), sq)

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

    def get_numerical_coordinates_from_algebratic_notation(self, letterFollowedByNumber):
        assert type(letterFollowedByNumber) == str and len(letterFollowedByNumber) == 2
        col = ord(letterFollowedByNumber[0]) - 97   # ord('a') == 97
        row = ord(letterFollowedByNumber[1]) - 49   # ord('1') == 49
        assert 0 <= col <= 7
        assert 0 <= row <= 7
        return row, col   # returns a tuple

    def is_square_on_board(self, square):
        row, col = self.get_numerical_coordinates_from_algebratic_notation(square)
        return self.is_coordinate_on_board(row, col)

    def is_square_empty(self, square):
        return self.get_piece_on_square(square) == self.EMPTY_SQUARE

    def is_coordinate_on_board(self, row, col):
        if (0 <= col <= 7) and (0 <= row <= 7):
            return True
        return False

    def update_square_with_piece(self, piece, square):
        row, col = self.get_numerical_coordinates_from_algebratic_notation(square)
        self.board[row][col] = piece

    def get_piece_on_square(self, square):
        row, col = self.get_numerical_coordinates_from_algebratic_notation(square)
        return self.board[row][col]

    def execute_move(self, originSquare, destinationSquare):
        originPiece = self.get_piece_on_square(originSquare)
        if originPiece.is_legal_move(self, destinationSquare):   # NEED TO ADD RULES LEVEL VALIDATION AS WELL AS PIECE LEVEL VALIDATION
            self.update_square_with_piece(self.EMPTY_SQUARE, originSquare)
            self.update_square_with_piece(originPiece, destinationSquare)

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
