BOARD_SIZE = 5

class GomokuPos:
    def __init__(self, x=-1, y=-1):
        self.x = x
        self.y = y

    def valid_pos(self):
        return 0 <= self.x < BOARD_SIZE and 0 <= self.y < BOARD_SIZE
    
    def __eq__(self, other):
        return isinstance(other, GomokuPos) and self.x == other.x and self.y == other.y

class Gomoku:
    """
    Two player Gomoku Game\n
    Default active turn is X
    """
    def __init__(self, other=None):
        
        if other is None:
            self.board = [['N' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
            self.active_turn = 'X'  # Start with player 'X'
        else:
            self.board = [row[:] for row in other.board]
            self.active_turn = other.active_turn

    def win(self):
        """
        Check if there's a winner or if the game is tied.\n
        Returns:
            'X' or 'O' if a player has won\n
            'T' if the game is tied\n
            'N' if the game is ongoing\n
        """
        def check_sequence(seq):
            """ Helper function to check for a sequence of five identical pieces. """
            for i in range(len(seq) - 4):
                if seq[i:i+5] == ['X'] * 5:
                    return 'X'
                elif seq[i:i+5] == ['O'] * 5:
                    return 'O'
            return None

        # Check rows and columns
        for i in range(BOARD_SIZE):
            # Check rows
            row_winner = check_sequence(self.board[i])
            if row_winner:
                return row_winner
            
            # Check columns
            column = [self.board[j][i] for j in range(BOARD_SIZE)]
            column_winner = check_sequence(column)
            if column_winner:
                return column_winner

        # Check diagonals
        for i in range(BOARD_SIZE - 4):
            for j in range(BOARD_SIZE):
                # Main diagonal (top-left to bottom-right)
                if j <= BOARD_SIZE - 5:
                    diag1 = [self.board[i+k][j+k] for k in range(5)]
                    diag1_winner = check_sequence(diag1)
                    if diag1_winner:
                        return diag1_winner
                
                # Anti-diagonal (top-right to bottom-left)
                if j >= 4:
                    diag2 = [self.board[i+k][j-k] for k in range(5)]
                    diag2_winner = check_sequence(diag2)
                    if diag2_winner:
                        return diag2_winner

        # Check for tie
        if all(cell != 'N' for row in self.board for cell in row):
            return 'T'

        # No winner yet
        return 'N'

    def over(self):
        """ Check if the game is over (win or tie). """
        return self.win() != 'N'

    def move(self, pos):
        """ Place the stone of the active player at the specified position. """
        if self.board[pos.x][pos.y] == 'N':
            self.board[pos.x][pos.y] = self.active_turn
            # Toggle active player
            self.active_turn = 'O' if self.active_turn == 'X' else 'X'
        else:
            raise ValueError("Invalid move: position already occupied or out of bounds.")
        
    def get_valid_moves(self):
        moves = []
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self.board[i][j] == 'N':
                    moves.append(GomokuPos(i, j))
        return moves
    
    def get_new_state(self, pos):
        new_state = Gomoku(self)
        new_state.move(pos)
        return new_state
    
    def get_valid_states(self):
        states = []
        for pos in self.get_valid_moves():
            states.append(self.get_new_state(pos))
        return states

    def show_board(self):
        """ Display the current game board. """
        for row in self.board:
            print(' '.join(row))
        print()



class GomokuBot:
    """
    This BOT can return the best move from a given Gomoku board game\n
    Use take_turn method and then get the choice property to get the best move
    """
    def __init__(self, gmk_game):
        self.gmk_game = gmk_game
        self.name = gmk_game.active_turn
        self.opponent = 'O' if self.name == 'X' else 'X'
        self.choice = None

    @staticmethod
    def score(state, depth, me, opponent):
        winner = state.win()
        if winner == me:
            return 10 - depth
        elif winner == opponent:
            return depth - 10
        else:
            return 0
    
    def minimax(self, state, depth, alpha, beta):
        if state.over():
            return GomokuBot.score(state, depth, self.name, self.opponent)
        
        if state.active_turn == self.name:  # Maximize for self
            max_score = -999
            for move in state.get_valid_moves():
                possible_game = state.get_new_state(move)
                score = self.minimax(possible_game, depth + 1, alpha, beta)
                if depth == 0 and score > max_score:
                    self.choice = move
                max_score = max(max_score, score)
                alpha = max(alpha, max_score)
                if beta <= alpha:
                    # print(f"hi{depth}")
                    break  # Beta cut-off
            return max_score
        
        else:  # Minimize for opponent
            min_score = 999
            for move in state.get_valid_moves():
                possible_game = state.get_new_state(move)
                score = self.minimax(possible_game, depth + 1, alpha, beta)
                min_score = min(min_score, score)
                beta = min(beta, min_score)
                if beta <= alpha:
                    # print(f"hi{depth}")
                    break  # Alpha cut-off
            return min_score
    

        
    def take_turn(self):
        """
        Return the best choice
        """
        self.minimax(self.gmk_game, 0, -999, 999)
        return self.choice



if __name__ == "__main__":
    # Create a new Gomoku game
    game = Gomoku()

    game.board = [
        ['N', 'X', 'N', 'N', 'N'],
        ['O', 'N', 'O', 'O', 'N'],
        ['X', 'X', 'X', 'N', 'N'],
        ['N', 'O', 'X', 'N', 'O'],
        ['O', 'N', 'N', 'X', 'N']
    ]

    # Create a bot instance to play against
    bot = GomokuBot(game)
    game.show_board()
    print("Bot is thinking...")
    bot_turn = bot.take_turn()
    game.move(bot_turn)
    print("Bot think done")
    game.show_board()
    if game.over():
        print("Game over")
        
    """
    while True:
        print("Bot is thinking...")
        bot_turn = bot.take_turn()
        game.move(bot_turn)
        print("Bot think done")
        game.show_board()
        if game.over():
            print("Game over")
            break
        
        print("Your turn...")
        game.move(GomokuPos(int(input("x=")), int("y=")))
        game.show_board()
        if game.over():
            print("Game over")
            break

    """



