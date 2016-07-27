import unittest
import Board
import Pieces


class Tests(unittest.TestCase):
    def setUp(self):
        self.board = Board.ChessBoard()
        self.longMessage = True

    def tearDown(self):
        self.board = None

    def is_pawn_promotion(self, piece, destination):
        return (
            piece is Pieces.Pawn
            and (
                self.board.get_row_number_from_square(destination) == 0
                or self.board.get_row_number_from_square(destination) == 7
            )
        )

    def verify_piece_is_properly_moved(self, piece, destination):
        if not self.is_pawn_promotion(piece, destination):
            self.assertIsInstance(self.board.get_contents_of_square(destination), piece,
                                  "Square does not contain the correct piece")
        else:
            # auto-promotion is to queen, other promotions tested in specific pawn promotion tests
            self.assertIsInstance(self.board.get_contents_of_square(destination), Pieces.Queen,
                                  "Square does not contain the correct piece")

    def verify_legal_move(self, piece, origin, destination):
        self.assertTrue(self.board.get_contents_of_square(origin).is_legal_move(self.board, destination))
        self.board.execute_move(origin, destination)
        self.verify_piece_is_properly_moved(piece, destination)
        self.assertTrue(self.board.is_square_empty(origin))

    def verify_illegal_move_is_not_made(self, piece, origin, destination):
        self.assertFalse(self.board.is_valid_move(origin, destination))
        is_destination_square_initially_empty = self.board.is_square_empty(destination)
        self.board.execute_move(origin, destination)
        self.assertEquals(piece, type(self.board.get_contents_of_square(origin)),
                          "Square does not contain the correct piece")
        if is_destination_square_initially_empty:
            self.assertTrue(self.board.is_square_empty(destination))


class MaintenanceTests(Tests):
    def setUp(self):
        self.board = Board.ChessBoard()
        self.board.ignore_move_order = True
        self.longMessage = True

    def test_first_side_to_move_is_white(self):
        self.assertTrue(self.board.is_whites_turn())

    def test_converting_algebraic_notation_to_numerical_coordinates(self):
        cols = 'abcdefgh'
        for row in range(8):
            for col in cols:
                algebraic_notation = col + str(row + 1)
                expected_coordinates = (row, cols.index(col))
                actual_coordinates = self.board.get_row_and_col_coordinates_from_square(algebraic_notation)
                self.assertEquals(expected_coordinates, actual_coordinates,
                                  "Incorrect conversion from algebraic notation to numeric coordinates")

    def test_printing_of_initial_piece_setup(self):
        expected_board_printout = "8 | r n b q k b n r" + "\n" \
                                  "7 | p p p p p p p p" + "\n" \
                                  "6 | ~ ~ ~ ~ ~ ~ ~ ~" + "\n" \
                                  "5 | ~ ~ ~ ~ ~ ~ ~ ~" + "\n" \
                                  "4 | ~ ~ ~ ~ ~ ~ ~ ~" + "\n" \
                                  "3 | ~ ~ ~ ~ ~ ~ ~ ~" + "\n" \
                                  "2 | P P P P P P P P" + "\n" \
                                  "1 | R N B Q K B N R" + "\n" \
                                  "   ----------------" + "\n" \
                                  "    a b c d e f g h"

        actual_board_printout = str(self.board)
        self.assertEquals(expected_board_printout, actual_board_printout,
                          "Initial board and piece setup printing incorrectly")

    def test_printing_game_after_first_four_moves(self):
        self.board.execute_move('e2', 'e4')
        self.board.execute_move('a7', 'a5')
        self.board.execute_move('g1', 'f3')
        self.board.execute_move('a8', 'a6')

        expected_board_printout = "8 | ~ n b q k b n r" + "\n" \
                                  "7 | ~ p p p p p p p" + "\n" \
                                  "6 | r ~ ~ ~ ~ ~ ~ ~" + "\n" \
                                  "5 | p ~ ~ ~ ~ ~ ~ ~" + "\n" \
                                  "4 | ~ ~ ~ ~ P ~ ~ ~" + "\n" \
                                  "3 | ~ ~ ~ ~ ~ N ~ ~" + "\n" \
                                  "2 | P P P P ~ P P P" + "\n" \
                                  "1 | R N B Q K B ~ R" + "\n" \
                                  "   ----------------" + "\n" \
                                  "    a b c d e f g h"

        actual_board_printout = str(self.board)
        self.assertEquals(expected_board_printout, actual_board_printout,
                          "Board position printout does not properly reflect executed moves")


class MoveSpecificTests(Tests):
    def setUp(self):
        self.board = Board.ChessBoard()
        self.board.ignore_move_order = True
        self.longMessage = True

    def test_squares_contain_correct_piece_types_after_first_four_moves(self):
        self.board.execute_move('d2', 'd4')  # White Pawn
        self.board.execute_move('b7', 'b5')  # Black Pawn
        self.board.execute_move('d1', 'd3')  # White Queen
        self.board.execute_move('c8', 'b7')  # Black Bishop

        self.assertEquals(Pieces.Pawn, type(self.board.get_contents_of_square('d4')),
                          "Square does not contain the correct piece")
        self.assertEquals(Pieces.Pawn, type(self.board.get_contents_of_square('b5')),
                          "Square does not contain the correct piece")
        self.assertEquals(Pieces.Queen, type(self.board.get_contents_of_square('d3')),
                          "Square does not contain the correct piece")
        self.assertEquals(Pieces.Bishop, type(self.board.get_contents_of_square('b7')),
                          "Square does not contain the correct piece")

        self.assertTrue(self.board.is_square_empty('d2'), "Expected square to be empty")
        self.assertFalse(self.board.is_square_empty('b7'), "Expected square to be occupied")
        self.assertTrue(self.board.is_square_empty('d1'), "Expected square to be empty")
        self.assertTrue(self.board.is_square_empty('c8'), "Expected square to be empty")

    def test_piece_current_square_value_updates_after_executing_move(self):
        self.board.execute_move('c2', 'c4')  # White Pawn
        self.assertEquals('c4', self.board.get_contents_of_square('c4').current_square,
                          "Piece's current square incorrect after moving to a new square")

        self.board.execute_move('b8', 'c6')  # Black Knight
        self.assertEquals('c6', self.board.get_contents_of_square('c6').current_square,
                          "Piece's current square incorrect after moving to a new square")

    def test_legal_knight_moves(self):
        # white side
        self.verify_legal_move(Pieces.Knight, 'b1', 'c3')
        self.verify_legal_move(Pieces.Knight, 'c3', 'b1')
        self.verify_legal_move(Pieces.Knight, 'b1', 'a3')
        self.verify_legal_move(Pieces.Knight, 'a3', 'b5')
        self.verify_legal_move(Pieces.Knight, 'g1', 'f3')
        self.verify_legal_move(Pieces.Knight, 'f3', 'd4')
        self.verify_legal_move(Pieces.Knight, 'd4', 'b3')
        self.board.execute_move('d2', 'd3')  # move pawn out of the way for the next night move
        self.verify_legal_move(Pieces.Knight, 'b3', 'd2')
        self.verify_legal_move(Pieces.Knight, 'd2', 'b1')

        # black side
        self.verify_legal_move(Pieces.Knight, 'b8', 'c6')
        self.verify_legal_move(Pieces.Knight, 'c6', 'e5')
        self.verify_legal_move(Pieces.Knight, 'g8', 'f6')
        self.verify_legal_move(Pieces.Knight, 'f6', 'd5')
        self.verify_legal_move(Pieces.Knight, 'd5', 'f4')
        self.verify_legal_move(Pieces.Knight, 'f4', 'd3')  # capture white pawn, check on the king
        self.board.execute_move('e1', 'd2')
        self.verify_legal_move(Pieces.Knight, 'd3', 'f2')
        self.verify_legal_move(Pieces.Knight, 'f2', 'h1')

    def test_illegal_knight_moves(self):
        # white side
        self.verify_illegal_move_is_not_made(Pieces.Knight, 'b1', 'b3')
        self.verify_illegal_move_is_not_made(Pieces.Knight, 'b1', 'c2')
        self.verify_illegal_move_is_not_made(Pieces.Knight, 'b1', 'c4')
        self.verify_illegal_move_is_not_made(Pieces.Knight, 'b1', 'd2')
        self.verify_illegal_move_is_not_made(Pieces.Knight, 'b1', 'e2')
        self.verify_illegal_move_is_not_made(Pieces.Knight, 'b1', 'a2')
        self.verify_illegal_move_is_not_made(Pieces.Knight, 'b1', 'd7')
        self.verify_illegal_move_is_not_made(Pieces.Knight, 'b1', 'a4')
        self.verify_illegal_move_is_not_made(Pieces.Knight, 'g1', 'g2')
        self.verify_illegal_move_is_not_made(Pieces.Knight, 'g1', 'g3')
        self.verify_illegal_move_is_not_made(Pieces.Knight, 'g1', 'g4')
        self.verify_illegal_move_is_not_made(Pieces.Knight, 'g1', 'h4')
        self.verify_illegal_move_is_not_made(Pieces.Knight, 'g1', 'h2')

        # black side
        self.verify_illegal_move_is_not_made(Pieces.Knight, 'b8', 'b6')
        self.verify_illegal_move_is_not_made(Pieces.Knight, 'g8', 'g6')
        self.verify_illegal_move_is_not_made(Pieces.Knight, 'g8', 'h8')

    def test_legal_bishop_moves(self):
        # clear the runway for all bishop moves
        self.board.execute_move('g2', 'g3')
        self.board.execute_move('b2', 'b3')
        self.board.execute_move('b7', 'b6')
        self.board.execute_move('g7', 'g6')

        # white side
        self.verify_legal_move(Pieces.Bishop, 'c1', 'b2')
        self.verify_legal_move(Pieces.Bishop, 'f1', 'g2')
        self.verify_legal_move(Pieces.Bishop, 'b2', 'h8')
        self.verify_legal_move(Pieces.Bishop, 'g2', 'a8')
        self.verify_legal_move(Pieces.Bishop, 'a8', 'b7')
        self.verify_legal_move(Pieces.Bishop, 'h8', 'g7')

        # black side
        self.assertEquals('w', self.board.get_contents_of_square('b7').color)
        self.verify_legal_move(Pieces.Bishop, 'c8', 'b7')
        self.assertEquals('b', self.board.get_contents_of_square('b7').color)
        self.verify_legal_move(Pieces.Bishop, 'f8', 'g7')
        self.verify_legal_move(Pieces.Bishop, 'b7', 'c6')
        self.verify_legal_move(Pieces.Bishop, 'c6', 'a4')
        self.verify_legal_move(Pieces.Bishop, 'a4', 'b3')  # capture pawn
        self.verify_legal_move(Pieces.Bishop, 'b3', 'c2')
        self.verify_legal_move(Pieces.Bishop, 'c2', 'b1')
        self.verify_legal_move(Pieces.Bishop, 'b1', 'a2')
        self.verify_legal_move(Pieces.Bishop, 'a2', 'd5')
        self.verify_legal_move(Pieces.Bishop, 'd5', 'h1')

    def test_illegal_bishop_moves(self):
        # white side
        self.verify_illegal_move_is_not_made(Pieces.Bishop, 'c1', 'b2')
        self.verify_illegal_move_is_not_made(Pieces.Bishop, 'c1', 'a1')
        self.verify_illegal_move_is_not_made(Pieces.Bishop, 'c1', 'c2')
        self.verify_illegal_move_is_not_made(Pieces.Bishop, 'f1', 'g2')
        self.verify_illegal_move_is_not_made(Pieces.Bishop, 'f1', 'e2')
        self.verify_illegal_move_is_not_made(Pieces.Bishop, 'f1', 'a6')
        self.board.execute_move('b2', 'b3')
        self.board.execute_move('c1', 'b2')
        self.verify_illegal_move_is_not_made(Pieces.Bishop, 'b2', 'h8')
        self.board.execute_move('b2', 'd4')
        self.verify_illegal_move_is_not_made(Pieces.Bishop, 'd4', 'f2')
        self.verify_illegal_move_is_not_made(Pieces.Bishop, 'd4', 'g1')

        # black side
        self.verify_illegal_move_is_not_made(Pieces.Bishop, 'c8', 'a8')
        self.verify_illegal_move_is_not_made(Pieces.Bishop, 'c8', 'b7')
        self.verify_illegal_move_is_not_made(Pieces.Bishop, 'f8', 'g7')
        self.verify_illegal_move_is_not_made(Pieces.Bishop, 'f8', 'e8')
        self.verify_illegal_move_is_not_made(Pieces.Bishop, 'f8', 'a3')
        self.board.execute_move('g7', 'g6')
        self.board.execute_move('f8', 'g7')
        self.verify_illegal_move_is_not_made(Pieces.Bishop, 'g7', 'c3')
        self.board.execute_move('g7', 'd4')
        self.verify_illegal_move_is_not_made(Pieces.Bishop, 'd4', 'h8')
        self.verify_illegal_move_is_not_made(Pieces.Bishop, 'd4', 'e6')

    def test_legal_rook_moves(self):
        # white side
        self.board.execute_move('a2', 'a4')
        self.verify_legal_move(Pieces.Rook, 'a1', 'a3')
        self.verify_legal_move(Pieces.Rook, 'a3', 'h3')
        self.verify_legal_move(Pieces.Rook, 'h3', 'h6')
        self.verify_legal_move(Pieces.Rook, 'h6', 'a6')
        self.verify_legal_move(Pieces.Rook, 'a6', 'b6')
        self.verify_legal_move(Pieces.Rook, 'b6', 'b3')
        self.verify_legal_move(Pieces.Rook, 'b3', 'a3')
        self.verify_legal_move(Pieces.Rook, 'a3', 'a1')
        self.verify_legal_move(Pieces.Rook, 'a1', 'a3')
        self.verify_legal_move(Pieces.Rook, 'a3', 'c3')
        self.verify_legal_move(Pieces.Rook, 'c3', 'c7')
        self.verify_legal_move(Pieces.Rook, 'c7', 'b7')
        self.verify_legal_move(Pieces.Rook, 'b7', 'a7')
        self.verify_legal_move(Pieces.Rook, 'a7', 'a8')
        self.verify_legal_move(Pieces.Rook, 'a8', 'b8')
        self.verify_legal_move(Pieces.Rook, 'b8', 'c8')

        # black side
        self.board.execute_move('h7', 'h5')
        self.verify_legal_move(Pieces.Rook, 'h8', 'h6')
        self.verify_legal_move(Pieces.Rook, 'h6', 'c6')
        self.verify_legal_move(Pieces.Rook, 'c6', 'c8')
        self.verify_legal_move(Pieces.Rook, 'c8', 'c2')
        self.verify_legal_move(Pieces.Rook, 'c2', 'c1')
        self.verify_legal_move(Pieces.Rook, 'c1', 'b1')
        self.verify_legal_move(Pieces.Rook, 'b1', 'a1')
        self.board.execute_move('e2', 'e3')  # clear space for king to run
        self.verify_legal_move(Pieces.Rook, 'a1', 'd1')
        self.board.execute_move('e1', 'e2')
        self.verify_legal_move(Pieces.Rook, 'd1', 'f1')
        self.verify_legal_move(Pieces.Rook, 'f1', 'g1')
        self.verify_legal_move(Pieces.Rook, 'g1', 'h1')
        self.verify_legal_move(Pieces.Rook, 'h1', 'h2')
        self.verify_legal_move(Pieces.Rook, 'h2', 'h4')

    def test_illegal_rook_moves(self):
        # white side
        self.verify_illegal_move_is_not_made(Pieces.Rook, 'a1', 'a2')
        self.verify_illegal_move_is_not_made(Pieces.Rook, 'a1', 'b1')
        self.verify_illegal_move_is_not_made(Pieces.Rook, 'a1', 'a5')
        self.verify_illegal_move_is_not_made(Pieces.Rook, 'a1', 'd1')
        self.verify_illegal_move_is_not_made(Pieces.Rook, 'a1', 'h8')
        self.board.execute_move('h2', 'h4')
        self.board.execute_move('h1', 'h2')
        self.verify_illegal_move_is_not_made(Pieces.Rook, 'h2', 'h4')
        self.verify_illegal_move_is_not_made(Pieces.Rook, 'h2', 'f2')
        self.board.execute_move('h2', 'h3')
        self.board.execute_move('h3', 'a3')
        self.board.execute_move('c2', 'c3')
        self.verify_illegal_move_is_not_made(Pieces.Rook, 'a3', 'h3')
        self.verify_illegal_move_is_not_made(Pieces.Rook, 'a3', 'c3')
        self.verify_illegal_move_is_not_made(Pieces.Rook, 'a3', 'd3')
        self.verify_illegal_move_is_not_made(Pieces.Rook, 'a3', 'e3')
        self.board.execute_move('a3', 'a7')
        self.verify_illegal_move_is_not_made(Pieces.Rook, 'a7', 'a2')

        # black side
        self.verify_illegal_move_is_not_made(Pieces.Rook, 'a8', 'a5')
        self.verify_illegal_move_is_not_made(Pieces.Rook, 'a8', 'b8')
        self.verify_illegal_move_is_not_made(Pieces.Rook, 'a8', 'e8')
        self.board.execute_move('a8', 'a7')  # capture white
        self.verify_illegal_move_is_not_made(Pieces.Rook, 'a7', 'b7')
        self.verify_illegal_move_is_not_made(Pieces.Rook, 'a7', 'b6')
        self.verify_illegal_move_is_not_made(Pieces.Rook, 'a7', 'e4')
        self.verify_illegal_move_is_not_made(Pieces.Rook, 'a7', 'c5')
        self.verify_illegal_move_is_not_made(Pieces.Rook, 'a7', 'd4')

    def test_legal_queen_moves(self):
        # white side
        self.board.execute_move('d2', 'd4')
        self.verify_legal_move(Pieces.Queen, 'd1', 'd3')
        self.verify_legal_move(Pieces.Queen, 'd3', 'a6')
        self.verify_legal_move(Pieces.Queen, 'a6', 'h6')
        self.verify_legal_move(Pieces.Queen, 'h6', 'e3')
        self.verify_legal_move(Pieces.Queen, 'e3', 'a3')
        self.verify_legal_move(Pieces.Queen, 'a3', 'a7')
        self.verify_legal_move(Pieces.Queen, 'a7', 'a8')
        self.verify_legal_move(Pieces.Queen, 'a8', 'b8')
        self.verify_legal_move(Pieces.Queen, 'b8', 'b7')
        self.verify_legal_move(Pieces.Queen, 'b7', 'f3')
        self.verify_legal_move(Pieces.Queen, 'f3', 'f6')
        self.verify_legal_move(Pieces.Queen, 'f6', 'g7')
        self.verify_legal_move(Pieces.Queen, 'g7', 'h8')
        self.verify_legal_move(Pieces.Queen, 'h8', 'h7')

        # black side
        self.board.execute_move('d7', 'd5')
        self.verify_legal_move(Pieces.Queen, 'd8', 'd6')
        self.verify_legal_move(Pieces.Queen, 'd6', 'h6')
        self.verify_legal_move(Pieces.Queen, 'h6', 'h7')
        self.verify_legal_move(Pieces.Queen, 'h7', 'h2')
        self.verify_legal_move(Pieces.Queen, 'h2', 'h1')
        self.verify_legal_move(Pieces.Queen, 'h1', 'g2')
        self.verify_legal_move(Pieces.Queen, 'g2', 'e4')
        self.verify_legal_move(Pieces.Queen, 'e4', 'd4')
        self.verify_legal_move(Pieces.Queen, 'd4', 'a7')
        self.verify_legal_move(Pieces.Queen, 'a7', 'a2')
        self.verify_legal_move(Pieces.Queen, 'a2', 'b2')
        self.verify_legal_move(Pieces.Queen, 'b2', 'h8')
        self.verify_legal_move(Pieces.Queen, 'h8', 'a1')

    def test_illegal_queen_moves(self):
        # white side
        self.verify_illegal_move_is_not_made(Pieces.Queen, 'd1', 'd2')
        self.verify_illegal_move_is_not_made(Pieces.Queen, 'd1', 'e2')
        self.verify_illegal_move_is_not_made(Pieces.Queen, 'd1', 'e1')
        self.verify_illegal_move_is_not_made(Pieces.Queen, 'd1', 'c1')
        self.verify_illegal_move_is_not_made(Pieces.Queen, 'd1', 'c2')
        self.board.execute_move('d2', 'd4')
        self.board.execute_move('d1', 'd3')
        self.board.execute_move('d3', 'a6')
        self.board.execute_move('c2', 'c4')
        self.verify_illegal_move_is_not_made(Pieces.Queen, 'a6', 'd3')
        self.verify_illegal_move_is_not_made(Pieces.Queen, 'a6', 'c4')
        self.board.execute_move('c4', 'c5')
        self.board.execute_move('a6', 'd3')
        self.verify_illegal_move_is_not_made(Pieces.Queen, 'd3', 'g7')
        self.verify_illegal_move_is_not_made(Pieces.Queen, 'd3', 'h4')
        self.verify_illegal_move_is_not_made(Pieces.Queen, 'd3', 'c1')
        self.board.execute_move('d3', 'h7')
        self.verify_illegal_move_is_not_made(Pieces.Queen, 'h7', 'f7')
        self.verify_illegal_move_is_not_made(Pieces.Queen, 'h7', 'h2')

        # black side
        self.board.execute_move('d7', 'd5')
        self.board.execute_move('d8', 'd6')
        self.verify_illegal_move_is_not_made(Pieces.Queen, 'd6', 'a3')
        self.board.execute_move('d6', 'c5')
        self.board.execute_move('c5', 'a3')
        self.verify_illegal_move_is_not_made(Pieces.Queen, 'a3', 'a1')
        self.verify_illegal_move_is_not_made(Pieces.Queen, 'a3', 'e7')
        self.board.execute_move('a3', 'h3')
        self.verify_illegal_move_is_not_made(Pieces.Queen, 'h3', 'h8')
        self.board.execute_move('h3', 'h7')
        self.board.execute_move('h7', 'b1')
        self.verify_illegal_move_is_not_made(Pieces.Queen, 'b1', 'b6')
        self.verify_illegal_move_is_not_made(Pieces.Queen, 'b1', 'h8')

    def test_legal_king_moves(self):
        self.board.execute_move('e2', 'e3')
        self.verify_legal_move(Pieces.King, 'e1', 'e2')
        self.verify_legal_move(Pieces.King, 'e2', 'd3')
        self.verify_legal_move(Pieces.King, 'd3', 'c4')
        # try all surrounding moves
        self.verify_legal_move(Pieces.King, 'c4', 'c5')
        self.verify_legal_move(Pieces.King, 'c5', 'c4')
        self.verify_legal_move(Pieces.King, 'c4', 'd5')
        self.verify_legal_move(Pieces.King, 'd5', 'c4')
        self.verify_legal_move(Pieces.King, 'c4', 'd4')
        self.verify_legal_move(Pieces.King, 'd4', 'c4')
        self.verify_legal_move(Pieces.King, 'c4', 'd3')
        self.verify_legal_move(Pieces.King, 'd3', 'c4')
        self.verify_legal_move(Pieces.King, 'c4', 'c3')
        self.verify_legal_move(Pieces.King, 'c3', 'c4')
        self.verify_legal_move(Pieces.King, 'c4', 'b3')
        self.verify_legal_move(Pieces.King, 'b3', 'c4')
        self.verify_legal_move(Pieces.King, 'c4', 'b4')
        self.verify_legal_move(Pieces.King, 'b4', 'c4')
        self.verify_legal_move(Pieces.King, 'c4', 'b5')
        self.verify_legal_move(Pieces.King, 'b5', 'c4')
        self.board.execute_move('c7', 'c5')
        self.verify_legal_move(Pieces.King, 'c4', 'c5')

    def test_illegal_king_moves(self):
        self.verify_illegal_move_is_not_made(Pieces.King, 'e1', 'd1')
        self.verify_illegal_move_is_not_made(Pieces.King, 'e1', 'd2')
        self.verify_illegal_move_is_not_made(Pieces.King, 'e1', 'e2')
        self.verify_illegal_move_is_not_made(Pieces.King, 'e1', 'f2')
        self.verify_illegal_move_is_not_made(Pieces.King, 'e1', 'f1')
        self.board.execute_move('e2', 'e4')
        self.verify_illegal_move_is_not_made(Pieces.King, 'e1', 'e3')
        self.board.execute_move('e1', 'e2')
        self.verify_illegal_move_is_not_made(Pieces.King, 'e2', 'c4')

    def test_legal_pawn_moves(self):
        self.verify_legal_move(Pieces.Pawn, 'a2', 'a4')
        self.verify_legal_move(Pieces.Pawn, 'b2', 'b4')
        self.verify_legal_move(Pieces.Pawn, 'c2', 'c4')
        self.verify_legal_move(Pieces.Pawn, 'd2', 'd4')
        self.verify_legal_move(Pieces.Pawn, 'e2', 'e3')
        self.verify_legal_move(Pieces.Pawn, 'f2', 'f3')
        self.verify_legal_move(Pieces.Pawn, 'g2', 'g3')
        self.verify_legal_move(Pieces.Pawn, 'h2', 'h4')
        self.verify_legal_move(Pieces.Pawn, 'a4', 'a5')
        self.verify_legal_move(Pieces.Pawn, 'a5', 'a6')
        self.verify_legal_move(Pieces.Pawn, 'a6', 'b7')  # capture
        self.verify_legal_move(Pieces.Pawn, 'b7', 'a8')
        self.verify_legal_move(Pieces.Pawn, 'b4', 'b5')
        self.verify_legal_move(Pieces.Pawn, 'a7', 'a5')  # prepare en passant square
        self.verify_legal_move(Pieces.Pawn, 'b5', 'a6')
        self.assertTrue(self.board.is_square_empty('a5'),
                        "An en passant capture should remove the pawn that created the en passant target square")
        self.verify_legal_move(Pieces.Pawn, 'h4', 'h5')
        self.verify_legal_move(Pieces.Pawn, 'h5', 'h6')
        self.verify_legal_move(Pieces.Pawn, 'g7', 'g5')
        self.verify_legal_move(Pieces.Pawn, 'g5', 'g4')
        self.verify_legal_move(Pieces.Pawn, 'g4', 'f3')
        self.verify_legal_move(Pieces.Pawn, 'c7', 'c5')
        self.verify_legal_move(Pieces.Pawn, 'c5', 'd4')
        self.verify_legal_move(Pieces.Pawn, 'd4', 'e3')
        self.verify_legal_move(Pieces.Pawn, 'e3', 'e2')

    def test_illegal_pawn_moves(self):
        self.verify_illegal_move_is_not_made(Pieces.Pawn, 'b2', 'b5')
        self.verify_illegal_move_is_not_made(Pieces.Pawn, 'b2', 'b6')
        self.verify_illegal_move_is_not_made(Pieces.Pawn, 'b2', 'b1')
        self.verify_illegal_move_is_not_made(Pieces.Pawn, 'b2', 'a2')
        self.verify_illegal_move_is_not_made(Pieces.Pawn, 'b2', 'a3')
        self.verify_illegal_move_is_not_made(Pieces.Pawn, 'b2', 'c3')
        self.verify_illegal_move_is_not_made(Pieces.Pawn, 'b2', 'c4')
        self.verify_illegal_move_is_not_made(Pieces.Pawn, 'b2', 'a4')
        self.board.execute_move('a2', 'a4')
        self.board.execute_move('b2', 'b4')
        self.board.execute_move('c2', 'c3')
        self.board.execute_move('d2', 'd4')
        self.board.execute_move('e2', 'e4')
        self.board.execute_move('e4', 'e5')
        self.board.execute_move('e5', 'e6')
        self.board.execute_move('f2', 'f4')
        self.board.execute_move('g2', 'g3')
        self.board.execute_move('f4', 'f5')

        self.verify_illegal_move_is_not_made(Pieces.Pawn, 'e7', 'e5')  # can't jump over opponents piece to empty square
        self.verify_illegal_move_is_not_made(Pieces.Pawn, 'e7', 'f6')
        self.verify_illegal_move_is_not_made(Pieces.Pawn, 'e7', 'e6')
        self.board.execute_move('d7', 'd5')
        self.verify_illegal_move_is_not_made(Pieces.Pawn, 'e6', 'd7')
        self.verify_illegal_move_is_not_made(Pieces.Pawn, 'd5', 'd4')
        self.board.execute_move('c3', 'c4')
        self.board.execute_move('c4', 'c5')
        self.verify_illegal_move_is_not_made(Pieces.Pawn, 'd5', 'c4')
        self.verify_illegal_move_is_not_made(Pieces.Pawn, 'd5', 'c5')
        self.verify_illegal_move_is_not_made(Pieces.Pawn, 'd5', 'e6')
        self.verify_illegal_move_is_not_made(Pieces.Pawn, 'd5', 'd6')
        self.verify_illegal_move_is_not_made(Pieces.Pawn, 'd5', 'd7')

        self.board.execute_move('b7', 'b5')  # create en passant square
        self.board.execute_move('c5', 'c6')
        self.verify_illegal_move_is_not_made(Pieces.Pawn, 'a7', 'b6')  # cannot use your own en passant square
        self.verify_illegal_move_is_not_made(Pieces.Pawn, 'f5', 'e6')
        self.verify_illegal_move_is_not_made(Pieces.Pawn, 'g3', 'h2')
        self.verify_illegal_move_is_not_made(Pieces.Pawn, 'h2', 'g3')

    def test_invalid_move_when_origin_and_destination_are_equal(self):
        self.assertFalse(self.board.is_valid_move('e2', 'e2'))

    def test_en_passant_rules(self):
        self.assertEquals('', self.board.enPassantTargetSquare)
        self.board.execute_move('e2', 'e4')
        self.assertEquals('e3', self.board.enPassantTargetSquare)
        self.board.execute_move('e7', 'e5')
        self.assertEquals('e6', self.board.enPassantTargetSquare)
        self.board.execute_move('d2', 'd3')
        self.assertEquals('', self.board.enPassantTargetSquare)

    def test_legal_castling_moves(self):
        # short
        white_short_castle_rook = self.board.get_contents_of_square('h1')
        self.board.execute_move('e2', 'e4')
        self.board.execute_move('f1', 'e2')
        self.board.execute_move('g1', 'f3')
        self.verify_legal_move(Pieces.King, 'e1', 'g1')
        self.assertEqual(white_short_castle_rook, self.board.get_contents_of_square('f1'))
        self.assertTrue(self.board.is_square_empty('h1'))
        # long
        black_long_castle_rook = self.board.get_contents_of_square('a8')
        self.board.execute_move('d7', 'd6')
        self.board.execute_move('c8', 'e6')
        self.board.execute_move('d8', 'd7')
        self.board.execute_move('b8', 'c6')
        self.verify_legal_move(Pieces.King, 'e8', 'c8')
        self.assertEqual(black_long_castle_rook, self.board.get_contents_of_square('d8'))
        self.assertTrue(self.board.is_square_empty('a8'))

    def test_illegal_castling_moves(self):
        self.board.execute_move('e2', 'e4')
        self.board.execute_move('f1', 'a6')
        self.verify_illegal_move_is_not_made(Pieces.King, 'e1', 'g1')
        self.board.execute_move('g1', 'f3')
        # now legal
        self.board.execute_move('b7', 'b6')
        self.board.execute_move('c8', 'a6')
        # king would have to pass through in check
        self.verify_illegal_move_is_not_made(Pieces.King, 'e1', 'g1')

        self.board.execute_move('d2', 'd3')
        self.board.execute_move('e7', 'e6')
        self.board.execute_move('f8', 'b4')
        # king in check
        self.verify_illegal_move_is_not_made(Pieces.King, 'e1', 'g1')

        self.board.execute_move('c2', 'c3')
        self.board.execute_move('g8', 'f6')
        self.board.execute_move('f6', 'h5')
        self.board.execute_move('h5', 'f4')
        self.board.execute_move('f4', 'h3')
        self.board.execute_move('a2', 'a3')
        # king would land in check
        self.verify_illegal_move_is_not_made(Pieces.King, 'e1', 'g1')

        self.board.execute_move('a3', 'a4')
        self.board.execute_move('h3', 'f4')
        # make sure castling is still available
        self.assertTrue(self.board.get_contents_of_square('e1').is_legal_move(self.board, 'g1'))
        self.board.execute_move('c3', 'c4')
        self.verify_illegal_move_is_not_made(Pieces.King, 'e1', 'e2')  # this would be into check
        self.board.execute_move('f4', 'h5')
        self.board.execute_move('e1', 'e2')
        self.verify_illegal_move_is_not_made(Pieces.King, 'e2', 'g1')
        self.board.execute_move('e2', 'e1')
        # king already moved
        self.verify_illegal_move_is_not_made(Pieces.King, 'e1', 'g1')

        # make sure castling is still available
        self.assertTrue(self.board.get_contents_of_square('e8').is_legal_move(self.board, 'g8'))
        self.board.execute_move('h8', 'g8')
        self.board.execute_move('g8', 'h8')
        # rook already moved
        self.verify_illegal_move_is_not_made(Pieces.King, 'e8', 'g8')

    def test_pawn_promotion(self):
        self.board.execute_move('a2', 'a4')
        self.board.execute_move('a4', 'a5')
        self.board.execute_move('a5', 'a6')
        self.board.execute_move('a6', 'b7')
        old_pawn = self.board.get_contents_of_square('b7')
        captured_piece = self.board.get_contents_of_square('a8')
        self.assertTrue(captured_piece in self.board.black_pieces_on_the_board)
        self.board.simulate_get_move('b7', 'a8')  # check default with no third parameter promotes to queen
        newly_minted_piece = self.board.get_contents_of_square('a8')
        self.assertTrue(newly_minted_piece.is_white_piece())
        self.assertTrue(newly_minted_piece in self.board.white_pieces_on_the_board)
        self.assertFalse(old_pawn in self.board.white_pieces_on_the_board)
        self.assertTrue(old_pawn in self.board.pieces_off_the_board)
        self.assertFalse(captured_piece in self.board.black_pieces_on_the_board)
        self.assertTrue(captured_piece in self.board.pieces_off_the_board)
        self.verify_legal_move(Pieces.Queen, 'a8', 'f3')

        self.board.execute_move('b2', 'b4')
        self.board.execute_move('b4', 'b5')
        self.board.execute_move('b5', 'b6')
        self.board.execute_move('b6', 'a7')
        old_pawn = self.board.get_contents_of_square('a7')
        captured_piece = self.board.get_contents_of_square('b8')
        self.assertTrue(captured_piece in self.board.black_pieces_on_the_board)
        self.board.simulate_get_move('a7', 'b8', 'r')
        newly_minted_piece = self.board.get_contents_of_square('b8')
        self.assertTrue(newly_minted_piece.is_white_piece())
        self.assertTrue(newly_minted_piece in self.board.white_pieces_on_the_board)
        self.assertFalse(old_pawn in self.board.white_pieces_on_the_board)
        self.assertTrue(old_pawn in self.board.pieces_off_the_board)
        self.assertFalse(captured_piece in self.board.black_pieces_on_the_board)
        self.assertTrue(captured_piece in self.board.pieces_off_the_board)
        self.verify_legal_move(Pieces.Rook, 'b8', 'b3')

        self.board.execute_move('h7', 'h5')
        self.board.execute_move('h5', 'h4')
        self.board.execute_move('h4', 'h3')
        self.board.execute_move('h3', 'g2')
        old_pawn = self.board.get_contents_of_square('g2')
        captured_piece = self.board.get_contents_of_square('h1')
        self.assertTrue(captured_piece in self.board.white_pieces_on_the_board)
        self.board.simulate_get_move('g2', 'h1', 'n')
        newly_minted_piece = self.board.get_contents_of_square('h1')
        self.assertTrue(newly_minted_piece.is_black_piece())
        self.assertTrue(newly_minted_piece in self.board.black_pieces_on_the_board)
        self.assertFalse(old_pawn in self.board.black_pieces_on_the_board)
        self.assertTrue(old_pawn in self.board.pieces_off_the_board)
        self.assertFalse(captured_piece in self.board.white_pieces_on_the_board)
        self.assertTrue(captured_piece in self.board.pieces_off_the_board)
        self.verify_legal_move(Pieces.Knight, 'h1', 'f2')

        self.board.execute_move('g7', 'g5')
        self.board.execute_move('g5', 'g4')
        self.board.execute_move('g4', 'g3')
        self.board.execute_move('g3', 'h2')
        old_pawn = self.board.get_contents_of_square('h2')
        captured_piece = self.board.get_contents_of_square('g1')
        self.assertTrue(captured_piece in self.board.white_pieces_on_the_board)
        self.board.simulate_get_move('h2', 'g1', 'b')
        newly_minted_piece = self.board.get_contents_of_square('g1')
        self.assertTrue(newly_minted_piece.is_black_piece())
        self.assertTrue(newly_minted_piece in self.board.black_pieces_on_the_board)
        self.assertFalse(old_pawn in self.board.black_pieces_on_the_board)
        self.assertTrue(old_pawn in self.board.pieces_off_the_board)
        self.assertFalse(captured_piece in self.board.white_pieces_on_the_board)
        self.assertTrue(captured_piece in self.board.pieces_off_the_board)
        self.verify_legal_move(Pieces.Bishop, 'g1', 'h2')
        self.verify_legal_move(Pieces.Bishop, 'h2', 'd6')

    def test_illegal_king_moves_dealing_with_check(self):
        self.board.execute_move('e2', 'e4')
        self.board.execute_move('b7', 'b6')
        self.board.execute_move('c8', 'a6')
        self.board.execute_move('a2', 'a3')
        self.verify_illegal_move_is_not_made(Pieces.King, 'e1', 'e2')
        self.board.execute_move('d2', 'd3')
        self.verify_legal_move(Pieces.King, 'e1', 'e2')
        self.board.execute_move('f2', 'f3')
        self.board.execute_move('g8', 'f6')
        self.board.execute_move('h2', 'h3')
        self.board.execute_move('h3', 'h4')
        self.board.execute_move('f6', 'g4')
        self.board.execute_move('a3', 'a4')
        self.verify_illegal_move_is_not_made(Pieces.King, 'e2', 'f2')
        self.board.execute_move('f3', 'g4')
        self.verify_legal_move(Pieces.King, 'e2', 'f3')

    def test_illegal_moves_that_leave_the_king_in_check(self):
        self.board.execute_move('e2', 'e4')
        self.board.execute_move('b7', 'b6')
        self.board.execute_move('c8', 'a6')
        self.board.execute_move('d2', 'd3')
        self.verify_legal_move(Pieces.King, 'e1', 'e2')
        self.board.execute_move('a2', 'a3')
        self.verify_illegal_move_is_not_made(Pieces.Pawn, 'd3', 'd4')

        self.board.execute_move('d7', 'd6')
        self.board.execute_move('d8', 'd7')
        self.board.execute_move('d7', 'e6')
        self.board.execute_move('e4', 'e5')
        self.verify_illegal_move_is_not_made(Pieces.Pawn, 'e5', 'd6')


class FullGameTests(Tests):
    def test_smother_mate(self):
        self.board.execute_move('h2', 'h4')
        self.board.execute_move('a7', 'a6')
        self.board.execute_move('h1', 'h3')
        self.board.execute_move('a6', 'a5')
        self.board.execute_move('h3', 'e3')
        self.board.execute_move('a5', 'a4')
        self.board.execute_move('g1', 'f3')
        self.board.execute_move('c7', 'c6')
        self.board.execute_move('f3', 'd4')
        self.board.execute_move('a4', 'a3')
        self.board.execute_move('d4', 'f5')
        self.board.execute_move('a3', 'b2')
        self.board.execute_move('f5', 'd6')
        self.assertTrue(self.board.is_game_over)
        self.assertEquals("Checkmate!! White Wins", self.board.outcome)

    def test_two_move_mate(self):
        self.board.execute_move('f2', 'f3')
        self.board.execute_move('e7', 'e5')
        self.board.execute_move('g2', 'g4')
        self.board.execute_move('d8', 'h4')
        self.assertTrue(self.board.is_game_over)
        self.assertEquals("Checkmate!! Black Wins", self.board.outcome)

    def test_four_move_mate(self):
        self.board.execute_move('e2', 'e4')
        self.board.execute_move('e7', 'e5')
        self.board.execute_move('f1', 'c4')
        self.board.execute_move('a7', 'a6')
        self.board.execute_move('d1', 'f3')
        self.board.execute_move('a6', 'a5')
        self.board.execute_move('f3', 'f7')
        self.assertTrue(self.board.is_game_over)
        self.assertEquals("Checkmate!! White Wins", self.board.outcome)

    def test_defense_against_four_move_mate(self):
        self.board.execute_move('e2', 'e4')
        self.board.execute_move('e7', 'e5')
        self.board.execute_move('f1', 'c4')
        self.board.execute_move('a7', 'a6')
        self.board.execute_move('d1', 'f3')
        self.board.execute_move('g8', 'h6')
        self.board.execute_move('f3', 'f7')
        self.assertFalse(self.board.is_game_over)
        self.assertNotEqual("Checkmate!! White Wins", self.board.outcome)

    def test_three_move_mate(self):
        self.board.execute_move('e2', 'e4')
        self.board.execute_move('f7', 'f6')
        self.board.execute_move('d2', 'd4')
        self.board.execute_move('g7', 'g5')
        self.board.execute_move('d1', 'h5')
        self.assertTrue(self.board.is_game_over)
        self.assertEquals("Checkmate!! White Wins", self.board.outcome)

    def test_queen_and_bishop_mate(self):
        self.board.execute_move('e2', 'e4')
        self.board.execute_move('e7', 'e5')
        self.board.execute_move('f2', 'f4')
        self.board.execute_move('f8', 'c5')
        self.board.execute_move('f4', 'e5')
        self.board.execute_move('d8', 'h4')
        self.board.execute_move('e1', 'e2')
        self.board.execute_move('h4', 'e4')
        self.assertTrue(self.board.is_game_over)
        self.assertEquals("Checkmate!! Black Wins", self.board.outcome)

    def test_knights_and_bishop_mate(self):
        self.board.execute_move('e2', 'e4')
        self.board.execute_move('e7', 'e5')
        self.board.execute_move('g1', 'f3')
        self.board.execute_move('d7', 'd6')
        self.board.execute_move('f1', 'c4')
        self.board.execute_move('h7', 'h6')
        self.board.execute_move('b1', 'c3')
        self.board.execute_move('c8', 'g4')
        self.board.execute_move('f3', 'e5')
        self.board.execute_move('g4', 'd1')
        self.board.execute_move('c4', 'f7')
        self.board.execute_move('e8', 'e7')
        self.board.execute_move('c3', 'd5')
        self.assertTrue(self.board.is_game_over)
        self.assertEquals("Checkmate!! White Wins", self.board.outcome)

    def test_black_smother_mate(self):
        self.board.execute_move('e2', 'e4')
        self.board.execute_move('b8', 'c6')
        self.board.execute_move('g2', 'g4')
        self.board.execute_move('c6', 'd4')
        self.board.execute_move('g1', 'e2')
        self.board.execute_move('d4', 'f3')
        self.assertTrue(self.board.is_game_over)
        self.assertEquals("Checkmate!! Black Wins", self.board.outcome)

    def test_queen_mate(self):
        self.board.execute_move('e2', 'e4')
        self.board.execute_move('e7', 'e5')
        self.board.execute_move('d1', 'h5')
        self.board.execute_move('e8', 'e7')
        self.board.execute_move('h5', 'e5')
        self.assertTrue(self.board.is_game_over)
        self.assertEquals("Checkmate!! White Wins", self.board.outcome)

    def test_bishop_and_rook_mate(self):
        self.board.execute_move('g2', 'g4')
        self.board.execute_move('h7', 'h5')
        self.board.execute_move('f1', 'g2')
        self.board.execute_move('h5', 'g4')
        self.board.execute_move('g2', 'b7')
        self.board.execute_move('h8', 'h2')
        self.board.execute_move('g1', 'h3')
        self.board.execute_move('c8', 'b7')
        self.board.execute_move('e1', 'g1')  # castle
        self.board.execute_move('h2', 'h1')
        self.assertTrue(self.board.is_game_over)
        self.assertEquals("Checkmate!! Black Wins", self.board.outcome)

    def test_mate_delivered_by_castling(self):
        self.verify_legal_move(Pieces.Pawn, 'd2', 'd4')
        self.verify_legal_move(Pieces.Pawn, 'f7', 'f5')
        self.verify_legal_move(Pieces.Knight, 'b1', 'c3')
        self.verify_legal_move(Pieces.Knight, 'g8', 'f6')
        self.verify_legal_move(Pieces.Knight, 'g1', 'f3')
        self.verify_legal_move(Pieces.Pawn, 'e7', 'e6')
        self.verify_legal_move(Pieces.Bishop, 'c1', 'g5')
        self.verify_legal_move(Pieces.Bishop, 'f8', 'e7')
        self.verify_legal_move(Pieces.Bishop, 'g5', 'f6')
        self.verify_legal_move(Pieces.Bishop, 'e7', 'f6')
        self.verify_legal_move(Pieces.Pawn, 'e2', 'e4')
        self.verify_legal_move(Pieces.Pawn, 'f5', 'e4')
        self.verify_legal_move(Pieces.Knight, 'c3', 'e4')
        self.verify_legal_move(Pieces.Pawn, 'b7', 'b6')
        self.verify_legal_move(Pieces.Knight, 'f3', 'e5')
        self.verify_legal_move(Pieces.King, 'e8', 'g8')
        self.verify_legal_move(Pieces.Bishop, 'f1', 'd3')
        self.verify_legal_move(Pieces.Bishop, 'c8', 'b7')
        self.verify_legal_move(Pieces.Queen, 'd1', 'h5')
        self.verify_legal_move(Pieces.Queen, 'd8', 'e7')  # now mate in 8!
        self.verify_legal_move(Pieces.Queen, 'h5', 'h7')
        self.verify_legal_move(Pieces.King, 'g8', 'h7')
        self.verify_legal_move(Pieces.Knight, 'e4', 'f6')  # double check
        self.verify_legal_move(Pieces.King, 'h7', 'h6')
        self.verify_legal_move(Pieces.Knight, 'e5', 'g4')
        self.verify_legal_move(Pieces.King, 'h6', 'g5')
        self.verify_legal_move(Pieces.Pawn, 'h2', 'h4')
        self.verify_legal_move(Pieces.King, 'g5', 'f4')
        self.verify_legal_move(Pieces.Pawn, 'g2', 'g3')
        self.verify_legal_move(Pieces.King, 'f4', 'f3')
        self.verify_legal_move(Pieces.Bishop, 'd3', 'e2')
        self.verify_legal_move(Pieces.King, 'f3', 'g2')
        self.verify_legal_move(Pieces.Rook, 'h1', 'h2')
        self.verify_legal_move(Pieces.King, 'g2', 'g1')
        self.verify_legal_move(Pieces.King, 'e1', 'c1')  # castle long, Mate!
        self.assertTrue(self.board.is_game_over)
        self.assertEquals("Checkmate!! White Wins", self.board.outcome)

    def test_stalemate_game(self):
        self.board.execute_move('h2', 'h4')
        self.board.execute_move('h7', 'h5')
        self.board.execute_move('g2', 'g3')
        self.board.execute_move('g7', 'g5')
        self.board.execute_move('f2', 'f4')
        self.board.execute_move('g5', 'g4')
        self.board.execute_move('e2', 'e4')
        self.board.execute_move('f7', 'f5')
        self.board.execute_move('e4', 'e5')
        self.board.execute_move('e7', 'e6')
        self.board.execute_move('d2', 'd4')
        self.board.execute_move('d7', 'd5')
        self.board.execute_move('c2', 'c4')
        self.board.execute_move('c7', 'c6')
        self.board.execute_move('c4', 'c5')
        self.board.execute_move('b7', 'b5')
        self.board.execute_move('b2', 'b4')
        self.board.execute_move('a7', 'a5')
        self.board.execute_move('a2', 'a3')
        self.board.execute_move('a5', 'a4')
        self.board.execute_move('g1', 'f3')
        self.board.execute_move('h8', 'h7')
        self.board.execute_move('f3', 'g5')
        self.board.execute_move('a8', 'a7')
        self.board.execute_move('g5', 'h7')
        self.board.execute_move('a7', 'b7')
        self.board.execute_move('h7', 'f8')
        self.board.execute_move('b7', 'd7')
        self.board.execute_move('f8', 'd7')
        self.board.execute_move('c8', 'b7')
        self.board.execute_move('d7', 'b8')
        self.board.execute_move('b7', 'a6')
        self.board.execute_move('b8', 'a6')
        self.board.execute_move('d8', 'b8')
        self.board.execute_move('a6', 'b8')
        self.board.execute_move('g8', 'f6')
        self.board.execute_move('b8', 'd7')
        self.board.execute_move('e8', 'f7')
        self.board.execute_move('d7', 'f6')
        self.board.execute_move('f7', 'g7')
        self.board.execute_move('b1', 'd2')
        self.board.execute_move('g7', 'h8')
        self.board.execute_move('d2', 'f3')
        self.board.execute_move('h8', 'g7')
        self.board.execute_move('f3', 'g5')
        self.board.execute_move('g7', 'h8')
        self.board.execute_move('g5', 'e6')
        self.assertTrue(self.board.is_game_over)
        self.assertEquals("Stalemate! Draw", self.board.outcome)

    def test_fastest_stalemate_with_all_pieces_on_board(self):
        # composed by Sam Loyd early 1900s
        self.board.execute_move('d2', 'd4')
        self.board.execute_move('d7', 'd6')
        self.board.execute_move('d1', 'd2')
        self.board.execute_move('e7', 'e5')
        self.board.execute_move('a2', 'a4')
        self.board.execute_move('e5', 'e4')
        self.board.execute_move('d2', 'f4')
        self.board.execute_move('f7', 'f5')
        self.board.execute_move('h2', 'h3')
        self.board.execute_move('f8', 'e7')
        self.board.execute_move('f4', 'h2')
        self.board.execute_move('c8', 'e6')
        self.board.execute_move('a1', 'a3')
        self.board.execute_move('c7', 'c5')
        self.board.execute_move('a3', 'g3')
        self.board.execute_move('d8', 'a5')
        self.board.execute_move('b1', 'd2')
        self.board.execute_move('e7', 'h4')
        self.board.execute_move('f2', 'f3')
        self.board.execute_move('e6', 'b3')
        self.board.execute_move('d4', 'd5')
        self.board.execute_move('e4', 'e3')
        self.board.execute_move('c2', 'c4')
        self.board.execute_move('f5', 'f4')
        self.assertTrue(self.board.is_game_over)
        self.assertEquals("Stalemate! Draw", self.board.outcome)

    def test_fastest_stalemate(self):
        # composed by Sam Loyd early 1900s
        self.board.execute_move('c2', 'c4')
        self.board.execute_move('h7', 'h5')
        self.board.execute_move('h2', 'h4')
        self.board.execute_move('a7', 'a5')
        self.board.execute_move('d1', 'a4')
        self.board.execute_move('a8', 'a6')
        self.board.execute_move('a4', 'a5')
        self.board.execute_move('a6', 'h6')
        self.board.execute_move('a5', 'c7')
        self.board.execute_move('f7', 'f6')
        self.board.execute_move('c7', 'd7')
        self.board.execute_move('e8', 'f7')
        self.board.execute_move('d7', 'b7')
        self.board.execute_move('d8', 'd3')
        self.board.execute_move('b7', 'b8')
        self.board.execute_move('d3', 'h7')
        self.board.execute_move('b8', 'c8')
        self.board.execute_move('f7', 'g6')
        self.board.execute_move('c8', 'e6')
        self.assertTrue(self.board.is_game_over)
        self.assertEquals("Stalemate! Draw", self.board.outcome)

    def test_morphy_night_at_the_opera_game(self):
        # Morphy vs Duke Karl, 1858 Paris
        self.board.execute_move('e2', 'e4')
        self.board.execute_move('e7', 'e5')
        self.board.execute_move('g1', 'f3')
        self.board.execute_move('d7', 'd6')
        self.board.execute_move('d2', 'd4')
        self.board.execute_move('c8', 'g4')
        self.board.execute_move('d4', 'e5')
        self.board.execute_move('g4', 'f3')
        self.board.execute_move('d1', 'f3')
        self.board.execute_move('d6', 'e5')
        self.board.execute_move('f1', 'c4')
        self.board.execute_move('g8', 'f6')
        self.board.execute_move('f3', 'b3')
        self.board.execute_move('d8', 'e7')
        self.board.execute_move('b1', 'c3')
        self.board.execute_move('c7', 'c6')
        self.board.execute_move('c1', 'g5')
        self.board.execute_move('b7', 'b5')
        self.board.execute_move('c3', 'b5')
        self.board.execute_move('c6', 'b5')
        self.board.execute_move('c4', 'b5')
        self.board.execute_move('b8', 'd7')
        self.board.execute_move('e1', 'c1')
        self.board.execute_move('a8', 'd8')
        self.board.execute_move('d1', 'd7')
        self.board.execute_move('d8', 'd7')
        self.board.execute_move('h1', 'd1')
        self.board.execute_move('e7', 'e6')
        self.board.execute_move('b5', 'd7')
        self.board.execute_move('f6', 'd7')
        self.board.execute_move('b3', 'b8')
        self.board.execute_move('d7', 'b8')
        self.board.execute_move('d1', 'd8')
        self.assertTrue(self.board.is_game_over)
        self.assertEquals("Checkmate!! White Wins", self.board.outcome)
