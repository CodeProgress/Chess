# Game
# Interfaces:
#   play_game

class Game:
    def __init__(self):
        pass

    def play_game(self):
        while not self.is_game_over():
            self.play_move()
        print "Game Over!"

    def is_game_over(self):
        # TO FINISH
        return True

    def play_move(self):
        move = self.get_move()
        if self.is_valid_move(move):
            self.update_position(move)
        else:
            print "Invalid Move.  Please try again"

    def get_move(self):
        move = raw_input("Enter move: (example: e2e4) ")
        return move

    def is_valid_move(self, move):
        # TO FINISH
        return True

    def update_position(self, move):
        # TO FINISH
        pass
