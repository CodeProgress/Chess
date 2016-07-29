from Board import ChessBoard
from Engine import Engine


class Game:
    def __init__(self):
        self.board = ChessBoard()
        self.engine = Engine()
        pass

    def play_game(self, withAI=False, verbose=False):
        while not self.is_game_over():
            if verbose:
                print self.board
            if withAI:
                if self.board.is_whites_turn():
                    self.play_move()
                else:
                    self.play_ai_move()
            else:
                self.play_move()

        print str(self.board) + "\n" + "Game Over! {}".format(self.board.outcome)

    def is_game_over(self):
        return self.board.is_game_over

    def play_move(self):
        move = raw_input("Enter move: (example: e2e4): ")
        if not self.board.attempt_to_make_move(move):
            print "\n Invalid Move! \n"

    def play_ai_move(self):
        origin, destination = self.engine.get_one_ply_materialistic_move(self.board)
        self.board.execute_move(origin, destination)
        print "Computer plays: {}{}".format(origin, destination)


g = Game()

g.play_game(True, True)
