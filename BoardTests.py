import unittest
import Board
import Pieces


class Tests(unittest.TestCase):
    def setUp(self):
        self.board = Board.ChessBoard()
        self.longMessage = True

    def tearDown(self):
        self.board = None

    def test_converting_algebraic_notation_to_numerical_coordinates(self):
        cols = 'abcdefgh'
        for row in range(8):
            for col in cols:
                algebraic_notation = col + str(row + 1)
                expected_coordinates = (row, cols.index(col))
                actual_coordinates = self.board.get_numerical_coordinates_from_algebratic_notation(algebraic_notation)
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
        self.assertEquals(expected_board_printout, actual_board_printout, "Initial board and piece setup printing incorrectly")

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
        self.assertEquals(expected_board_printout, actual_board_printout, "Board position printout does not properly reflect executed moves")

    def test_squares_contain_correct_piece_types_after_first_four_moves(self):
        self.board.execute_move('d2', 'd4')    # White Pawn
        self.board.execute_move('b7', 'b5')    # Black Pawn
        self.board.execute_move('d1', 'd3')    # White Queen
        self.board.execute_move('c8', 'b7')    # Black Bishop

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
        # A knight has 8 possible target squares it can jump to:
        #     Forward two then left or right one
        #     Left two then forward or backward one
        #     Right two then forward or backward one
        #     Backward two then left or right one
        # The knight may only jump to the above target squares if:
        #     The target square is on the board
        #     The target square is empty
        #     The target square contains an opponants piece
        pass

    def test_origin_square_is_different_than_destination_square(self):
        pass

