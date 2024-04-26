import random

BOARD_SIZE = 20
MINIMAX_INFINITY = 999
MAX_DEPTH = 9

class GomokuPos:
    def __init__(self, x=-1, y=-1):
        self.x = x
        self.y = y

    def valid_pos(self):
        return 0 <= self.x < BOARD_SIZE and 0 <= self.y < BOARD_SIZE
    
    @staticmethod
    def distance_between(pos_a, pos_b):
        x1, y1 = pos_a.x, pos_a.y
        x2, y2 = pos_b.x, pos_b.y
        distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        return distance

    def __eq__(self, other):
        return isinstance(other, GomokuPos) and self.x == other.x and self.y == other.y
    
    def __str__(self) -> str:
        return f"gmkp({self.x}, {self.y})"

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
        
    def get_threating_positions(self, opponent):
        me = 'X' if opponent == 'O' else 'O'
        # đường OO tạo thành OOO
        patterns = ["{1}{0}{0}{0}{0}N".format(opponent, me), "N{0}{0}{0}{0}{1}".format(opponent, me), "{0}{0}{0}{0}N".format(opponent, me), "N{0}{0}{0}{0}".format(opponent, me),"N{0}{0}{0}{0}N".format(opponent), "{0}{0}{0}N{0}".format(opponent), "{0}N{0}{0}{0}".format(opponent), "{0}{0}N{0}{0}".format(opponent), \
                    "N{0}N{0}{0}N".format(opponent), "N{0}{0}N{0}N".format(opponent), "N{0}{0}{0}N".format(opponent), "{1}N{0}{0}{0}NN".format(opponent, me), "NN{0}{0}{0}N{1}".format(opponent, me), "{1}{0}{0}{0}N".format(opponent, me), "N{0}{0}{0}{1}".format(opponent, me),\
                        "N{0}{0}N".format(opponent)]
        positions = []
        max_threating_point = 0
        for pattern in patterns:
            have_threat = False
            for i, row in enumerate(self.board):
                for j in range(BOARD_SIZE - len(pattern) + 1):
                    if ''.join(row[j:j+len(pattern)]) == pattern:
                        have_threat = True
                        positions.extend(GomokuPos(i, j+k) for k, char in enumerate(pattern) if char == 'N' and 0 <= j+k < BOARD_SIZE)
            for j in range(BOARD_SIZE):
                for i in range(BOARD_SIZE - len(pattern) + 1):
                    if ''.join(self.board[i+k][j] for k in range(len(pattern))) == pattern:
                        have_threat = True
                        positions.extend(GomokuPos(i+k, j) for k, char in enumerate(pattern) if char == 'N' and 0 <= i+k < BOARD_SIZE)
            for di in range(-BOARD_SIZE + 1, BOARD_SIZE):
                major_diagonal = [(i, i + di) for i in range(max(0, -di), min(BOARD_SIZE, BOARD_SIZE - di)) if 0 <= i + di < BOARD_SIZE]
                minor_diagonal = [(i, BOARD_SIZE - 1 - i - di) for i in range(max(0, -di), min(BOARD_SIZE, BOARD_SIZE - di)) if 0 <= BOARD_SIZE - 1 - i - di < BOARD_SIZE]
                for diagonal in [major_diagonal, minor_diagonal]:
                    for i in range(len(diagonal) - len(pattern) + 1):
                        if ''.join(self.board[x][y] for x, y in diagonal[i:i+len(pattern)]) == pattern:
                            have_threat = True
                            positions.extend(GomokuPos(x, y) for (x, y), char in zip(diagonal[i:i+len(pattern)], pattern) if char == 'N')
            
            if have_threat:
                threating_point = 0
                if pattern == "{1}{0}{0}{0}{0}N".format(opponent, me) or pattern == "N{0}{0}{0}{0}{1}".format(opponent, me) or pattern == "N{0}{0}{0}{0}N".format(opponent) or "{0}{0}{0}N{0}".format(opponent) or "{0}N{0}{0}{0}".format(opponent) or "{0}{0}N{0}{0}".format(opponent) or \
                    pattern == "{0}{0}{0}{0}N".format(opponent, me) or pattern == "N{0}{0}{0}{0}".format(opponent, me):
                   threating_point = 4
                elif pattern == "N{0}{0}N".format(opponent):
                    threating_point = 2
                else:
                    threating_point = 3
                max_threating_point = max(max_threating_point, threating_point) 
        # thêm điểm nếu các vị trí đe dọa được lặp lại
        for i in range(len(positions)):
            for j in range(i+1, len(positions)):
                if positions[i] == positions[j]:
                    max_threating_point += 0.5


        return positions, max_threating_point

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
    
    def have_occupied(self, pos):
        return self.board[pos.x][pos.y] != 'N'

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
    
    ###
    def get_best_moves(self):
        me = self.active_turn
        op = 'X' if me == 'O' else 'O'
        op_threating_moves, op_threating_point = self.get_threating_positions(op) # defense moves
        me_threating_moves, me_threating_point = self.get_threating_positions(me) # attack moves

        if me_threating_point >= op_threating_point:
            # look if the player me has any attack moves
            if me_threating_moves: 
                return me_threating_moves
            return [random.choice(self.get_lite_best_moves(me))]
        return op_threating_moves


    def get_lite_best_moves(self, me):
        '''
        Return lite-best moves of the me player
        '''
        best_moves = []
        max_allies = -1
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self.board[i][j] == 'N':
                    num_allies = 0
                    for dx, dy in directions:
                        x, y = i + dx, j + dy
                        if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE and self.board[x][y] == me:
                            num_allies += 1
                    if num_allies > max_allies:
                        best_moves.clear()
                        best_moves.append(GomokuPos(i, j))
                        max_allies = num_allies
                    elif num_allies == max_allies:
                        best_moves.append(GomokuPos(i, j))
        
        if len(best_moves) < MAX_DEPTH:
            return best_moves
        else:
            '''
            Lọc tiêu chí phụ, ví dụ gần trung tâm hơn
            '''
            center_point = GomokuPos(BOARD_SIZE//2, BOARD_SIZE//2)
            best_moves.sort(key=lambda x: GomokuPos.distance_between(center_point, x))
            return best_moves[0:4]
        
    
    # ----------------------


    def get_valid_states(self):
        states = []
        for pos in self.get_valid_moves():
            states.append(self.get_new_state(pos))
        return states

    def get_ordered_moves(self, heuristic_func, player_name):
        '''List of tuple, (move, score)'''
        # Get all valid moves
        valid_moves = self.get_valid_moves()

        # Use the heuristic function to score each move
        scored_moves = [(move, heuristic_func(self.get_new_state(move), player_name)) for move in valid_moves]

        # Sort the moves in descending order of their scores
        scored_moves.sort(key=lambda x: x[1], reverse=True)

        return scored_moves
    
    def get_ordered_states(self, heuristic_func):
        ''' Under the view of current active turn\n
        Getting neighbor states as a list of tuple (state, score) in decreasing order of heuristic score'''

        # Use the heuristic function to score each new state
        scored_states = [(self.get_new_state(move), heuristic_func(self.get_new_state(move), self.active_turn)) for move in self.get_valid_moves()]

        # Sort the states in descending order of their scores
        scored_states.sort(key=lambda x: x[1], reverse=True)

        # Return the ordered states
        return scored_states
    
    def get_best_states(self, heuristic_func, max_element=5):
        ''' Under the view of current active turn\n
        Getting neighbor states as a list of tuple (state, score) with the highest heuristic score'''

        # Use the heuristic function to score each new state
        scored_states = [(self.get_new_state(move), heuristic_func(self.get_new_state(move), self.active_turn)) for move in self.get_valid_moves()]

        # Sort the states in descending order of their scores
        scored_states.sort(key=lambda x: x[1], reverse=True)

        # Get the highest score
        highest_score = scored_states[0][1]

        # Return only the states with the highest score
        best_states = [state for state in scored_states if state[1] == highest_score]

        return best_states[:max_element]

    def have_worse(self, other_states):
        '''
        Under the view of the active_turn\n
        Return True if there is any better state in the other_states list'''
        this_score = GomokuBot.heuristic(self, self.active_turn)
        for state in other_states:
            if GomokuBot.heuristic(state, self.active_turn) > this_score:
                return True
        return False

    def count_moves(self):
        '''
        Returns (number X, number O, number blank) have moved on the current table
        '''
        cx = co = cn = 0
        for cl in self.board:
            for c in cl:
                if c == 'X':
                    cx += 1
                elif c == 'O':
                    co += 1
                elif c == 'N':
                    cn += 1
        return cx, co, cn
    '''
    def show_board(self):
        """ Display the current game board. """
        print(end="  ")
        for i in range(BOARD_SIZE):
            print(i,end=" ")
        print()
        j = 0
        for row in self.board:
            print(j, end=' ')
            j += 1
            print(' '.join(['.' if cell == 'N' else cell for cell in row]))
        print()
    '''
    8
    def show_board(self):
        """ Display the current game board. """
        print("   ", end="")
        for i in range(BOARD_SIZE):
            print(f"{i:2}", end=" ")
        print()
        j = 0
        for row in self.board:
            print(f"{j:2}", end=" ")
            j += 1
            print(' '.join(['.' if cell == 'N' else cell for cell in row]))
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
        self.best_state = None

    # ----------------------------------------------
    # Alpha-Beta Pruning searching
    def score_alpha_beta(self, winner, depth):
        '''
        Trả về điểm có được của một game ĐÃ KẾT THÚC
        Số điểm cao nhất là 20
        '''

        if winner == self.name:
            return 20 - depth
        elif winner == self.opponent:
            return -20 + depth
        return 0

    def minimax_alpha_beta(self, state, depth, alpha, beta):
        winner = state.win()
        if winner != 'N':
            final_score = self.score_alpha_beta(winner, depth)
            return final_score
        elif depth > MAX_DEPTH:
            return 0

        best_moves = state.get_best_moves()

        if state.active_turn == self.name:
            max_score = -MINIMAX_INFINITY
            for move in best_moves:
                possible_game = state.get_new_state(move)
                score = self.minimax_alpha_beta(possible_game, depth + 1, alpha, beta)
                # get the best move
                if depth == 0 and score > max_score:
                    self.choice = move
                    print("GET 1 SOLUTION!!!")
                # -----
                max_score = max(max_score, score)
                alpha = max(alpha, max_score)
                if alpha >= beta:
                    break
            return max_score
        else:
            min_score = MINIMAX_INFINITY
            for move in best_moves:
                possible_game = state.get_new_state(move)
                score = self.minimax_alpha_beta(possible_game, depth + 1, alpha, beta)
                min_score = min(min_score, score)
                beta = min(beta, min_score)
                if alpha >= beta:
                    break
            return min_score

    def take_turn_alpha_beta(self):
        """
        Return the best move it can do from its current board game
        TODO:
        Optimize, it turn slow when the number of blanks goes to 13 blanks
        """
        self.minimax_alpha_beta(self.gmk_game, 0, -MINIMAX_INFINITY, MINIMAX_INFINITY)
        return self.choice



if __name__ == "__main__":
    # Create a new Gomoku game
    game = Gomoku()
    bot = GomokuBot(game)

    '''
    game.board = [
        ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N'],
        ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'X', 'N'],
        ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'O', 'N', 'N'],
        ['N', 'N', 'N', 'N', 'N', 'N', 'O', 'N', 'N', 'N'],
        ['N', 'N', 'X', 'N', 'N', 'N', 'N', 'N', 'N', 'N'],
        ['N', 'N', 'X', 'N', 'O', 'N', 'N', 'N', 'N', 'N'],
        ['N', 'N', 'X', 'O', 'N', 'N', 'N', 'N', 'N', 'N'],
        ['N', 'N', 'O', 'N', 'N', 'N', 'N', 'N', 'N', 'N'],
        ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N'],
        ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N']]
    
            


    
    # FOR CHECK BOT'S MOVE
    # show before move
    print(game.count_moves())
    game.show_board()

    print("Bot is thinking...")
    bot_turn = bot.take_turn_alpha_beta()
    print("Bot moves:")
    game.move(bot_turn) # ??? nước đi này nhìn có vẻ ngu
    
    # show after move
    game.show_board()
    '''
    
    # FOR PLAY GAME
    game.show_board()
    while True:
        # get Bot's turn
        print("Bot is thinking...")
        bot_turn = bot.take_turn_alpha_beta()

        # Bot moves
        print("Bot moves:")
        game.move(bot_turn)
        game.show_board()

        # check result
        winner = game.win()
        if winner != 'N':
            if winner == 'X':
                print('X wins!')
            elif winner == 'O':
                print('O wins!')
            else:
                print('Tie!')
            break

        # get user's move and move
        game.move(GomokuPos(int(input('x=')), int(input('y='))))
        game.show_board()

        # check result
        winner = game.win()
        if winner != 'N':
            if winner == 'X':
                print('X wins!')
            elif winner == 'O':
                print('O wins!')
            else:
                print('Tie!')
            break
    
    


