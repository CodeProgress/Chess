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
        self.pieces_off_the_board = []

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
        return self.get_contents_of_square(square) == self.EMPTY_SQUARE

    def is_coordinate_on_board(self, row, col):
        if (0 <= col <= 7) and (0 <= row <= 7):
            return True
        return False

    def assign_value_to_square(self, value, square):
        row, col = self.get_numerical_coordinates_from_algebratic_notation(square)
        self.board[row][col] = value

    def clear_square(self, square):
        if not self.is_square_empty(square):
            self.pieces_off_the_board.append(self.get_contents_of_square(square))
            self.assign_value_to_square(self.EMPTY_SQUARE, square)

    def update_square_with_piece(self, piece, square):
        self.assign_value_to_square(piece, square)
        piece.current_square = square

    def get_contents_of_square(self, square):
        row, col = self.get_numerical_coordinates_from_algebratic_notation(square)
        return self.board[row][col]

    def validate_move(self, originSquare, destinationSquare):
        # This is the super method that must incorporate all of the rules of the game
        # possible overlap between this and execute_move method.
        # perhaps this is better handled in the game/rules class (or at least the non-piece specific parts)
        # things to validate:
        # originSquare contains a piece and is not empty
        # originSquare and destinatioSquare are different
        # is legal move from the piece's perspective: originPiece.is_legal_move(self, destinationSquare)
        # is legal move from game perspective:
        #     does the current move put the king in check?
        #     is the king in check and therefore the move must eliminate check
        #     is the move a castle?  Will require castling validation and a different execute move that moves two pieces at once
        #     is the game already over?  (This should actually be handled before ever reaching this point)
        #     50 move rule
        #     3 fold repetition
        pass

    def execute_move(self, originSquare, destinationSquare):
        # blindly executes move without regard to legality
        originPiece = self.get_contents_of_square(originSquare)
        self.clear_square(originSquare)
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
