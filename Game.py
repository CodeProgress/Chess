import Board


class Game:
    def __init__(self):
        self.board = Board.ChessBoard()
        pass

    def play_game(self):
        while not self.is_game_over():
            self.play_move()
            print self.board
        print "Game Over!"

    def is_game_over(self):
        return self.board.is_ending_condition()

    def play_move(self):
        move = raw_input("Enter move: (example: e2e4): ")
        self.board.attempt_to_make_move(move)

g = Game()

g.play_game()
