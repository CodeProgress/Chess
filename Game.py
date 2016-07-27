import Board


class Game:
    def __init__(self):
        self.board = Board.ChessBoard()
        pass

    def play_game(self, verbose=False):
        while not self.is_game_over():
            self.play_move()
            if verbose:
                print self.board

        print "Game Over! {}".format(self.board.outcome)

    def is_game_over(self):
        return self.board.is_game_over

    def play_move(self):
        move = raw_input("Enter move: (example: e2e4): ")
        if not self.board.attempt_to_make_move(move):
            print "\n Invalid Move! \n"

g = Game()

g.play_game(True)
