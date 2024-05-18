import random
import json

BOARD_SIZE = 20
MINIMAX_INFINITY = 999
MAX_DEPTH = 6


class GomokuPos:
    '''Được thiết kế dành riêng cho lớp Gomoku'''
    def __init__(self, x=-1, y=-1, threatening=0):
        self.x = x
        self.y = y
        self.threatening = threatening

    def serialize(self):
        return json.dumps({'x': self.x, 'y': self.y, 'threatening': self.threatening})

    @classmethod
    def deserialize(cls, data):
        data = json.loads(data)
        return cls(x=data['x'], y=data['y'], threatening=data['threatening'])

    def valid_pos(self):
        return 0 <= self.x < BOARD_SIZE and 0 <= self.y < BOARD_SIZE
    
    @staticmethod
    def distance_between(pos_a, pos_b):
        x1, y1 = pos_a.x, pos_a.y
        x2, y2 = pos_b.x, pos_b.y
        distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        return distance
    
    def to_standard_pos(self):
        '''Convert to 1->20 row and A->Z column possition, return 2 variable'''
        return self.x + 1, chr(65 + self.y)
    
    @staticmethod
    def to_gomoku_pos(row_number, col_letter):
        return GomokuPos(row_number - 1, ord(col_letter) - ord('A'))

    def __eq__(self, other):
        '''Don't check if is is an instance'''
        return (self.x, self.y) == (other.x, other.y)
    
    def __str__(self) -> str:
        return f"gmkp({self.x}, {self.y})"

    def __hash__(self):
        return hash((self.x, self.y))



class Gomoku:
    """
    Bàn cờ Caro với 2 người chơi\n
    Tọa độ của bàn cờ được quy định giống như một ma trận cấp 2 với các cột(dòng) 0 -> N từ trên xuống dưới(từ trái qua phải)\n
    Sử dụng lớp GomokuPos\n
    Mặc định nước đi đầu tiên là X
    """
    def __init__(self, other=None):
        if other is None:
            # Một vị trí trong board có thể có 3 giá trị X, O hoặc N (vị trí chưa có nước đi)
            self.board = [['N' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
            # active turn là nước đi tiếp theo của bàn cờ, mặc định nước đi đầu tiên là X
            self.active_turn = 'X'
        else:
            self.board = [row[:] for row in other.board]
            self.active_turn = other.active_turn
    
    # Use for Streamlit Web Application
    def serialize(self):
        """Convert the object state to a JSON string."""
        return json.dumps({
            'board': self.board,
            'active_turn': self.active_turn,
        })

    @classmethod
    def deserialize(cls, json_str):
        """Create an object instance from a JSON string."""
        data = json.loads(json_str)
        instance = cls()
        instance.board = data['board']
        instance.active_turn = data['active_turn']
        return instance
    
        
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
        ''' Trả về True nếu vị trí hiện tại bị chiếm bởi X hoặc O'''
        return self.board[pos.x][pos.y] != 'N'

    
    def get_new_state(self, pos):
        ''' Trả về một Gomoku mới là trạng thái của bàn cờ sau khi di chuyển nước đi pos'''
        new_state = Gomoku(self)
        new_state.move(pos)
        return new_state
    
    def get_threatening_positions(self, opponent):
        '''
        Trả về một danh sách các GomokuPos là các vị trí mà opponent khả năng cao sẽ đi nhất (những vị trí mà opponent tạo được nhiều điểm hăm dọa nhất)\n
        Và điểm hăm dọa cao nhất
        '''
        # me là nước đi có vai trò chặn opponent
        me = 'X' if opponent == 'O' else 'O'

        # Danh sách những mẫu/chuỗi trường hợp hăm dọa thường thấy
        # Ví dụ "{1}{0}{0}{0}{0}N".format(opponent, me)
        # Chuỗi này có nghĩa là opponent đã đi được 4 nước liên tiếp, bị chặn 1 đầu và đầu còn lại chưa được đi
        threatening_patterns = ["{1}{0}{0}{0}{0}N".format(opponent, me), "N{0}{0}{0}{0}{1}".format(opponent, me), "{0}{0}{0}{0}N".format(opponent, me), "N{0}{0}{0}{0}".format(opponent, me), "{0}{0}{0}N{0}".format(opponent), "{0}N{0}{0}{0}".format(opponent), "{0}{0}N{0}{0}".format(opponent), \
                    "N{0}N{0}{0}N".format(opponent), "N{0}{0}N{0}N".format(opponent), "N{0}{0}{0}N".format(opponent), "{1}N{0}{0}{0}NN".format(opponent, me), "NN{0}{0}{0}N{1}".format(opponent, me), "{1}{0}{0}{0}NN".format(opponent, me), "NN{0}{0}{0}{1}".format(opponent, me), "{0}N{0}N{0}".format(opponent),\
                        "N{0}{0}NN".format(opponent), "NN{0}{0}N".format(opponent), "N{0}N{0}N".format(opponent)]
        
        # điểm hăm dọa dùng cộng thêm nếu như xuất hiện 2 hay nhiều nước hăm dọa được dồn vào cùng 1 vị trí
        EXTRA_THREATENING_POINT = 0.5

        # danh sách kết quả các nước hăm dọa
        threatening_positions = []

        for pattern in threatening_patterns: # với mỗi mẫu hăm dọa, bảng sẽ được duyệt toàn bộ 1 lần
            # điểm hăm dọa của mẫu sẽ được gán cho vị trí hăm dọa (nếu có tồn tại)
            threatening_point = pattern.count('{0}'.format(opponent)) 

            for i, row in enumerate(self.board):  # duyệt từng dòng
                # tại dòng được xét, duyệt từ trái qua phải xem có tồn tại mẫu hăm dọa trong đó hay không
                for j in range(BOARD_SIZE - len(pattern) + 1):
                    if ''.join(row[j:j+len(pattern)]) == pattern: # nếu có chuỗi hăm dọa tại vị trí j
                        # tạo một biến k để tìm vị trí chưa đánh trong phạm vi chuỗi hăm dọa tìm được (đó cũng chính là vị trí hăm dọa)
                        for k, char in enumerate(pattern):
                            # có 2 trường hợp, điểm hăm dọa của nó là 3, 4,.., hoặc 3.5, 4.5,... 
                            # Việc có nhiều hơn 2 cộng dồn hăm dọa của 3 cũng không thể làm đểm hăm dọa của nó thành 4 bởi vì 1 đường 4 vẫn hơn nhiều đường 3
                            if char == 'N' and 0 <= j+k < BOARD_SIZE:
                                pos = GomokuPos(i, j+k)
                                # nếu vị trí hăm dọa tìm được là mới và chưa tồn tại từ trước tới giờ
                                if pos not in threatening_positions:
                                    pos.threatening = threatening_point
                                    threatening_positions.append(pos)
                                # điểm hăm dọa của vị trí được cộng dồn sẽ tăng
                                else: 
                                    id = threatening_positions.index(pos)
                                    old_threatening_point = threatening_positions[id].threatening
                                    if old_threatening_point == 3 or old_threatening_point == 4:
                                        threatening_positions[id].threatening = max(old_threatening_point, threatening_point) + EXTRA_THREATENING_POINT
                                    else:
                                        old_threatening_point -= EXTRA_THREATENING_POINT
                                        threatening_positions[id].threatening = max(old_threatening_point, threatening_point) + EXTRA_THREATENING_POINT
            for j in range(BOARD_SIZE): # duyệt theo cột. Cách duyệt của nó cũng tương tự với duyệt theo dòng
                for i in range(BOARD_SIZE - len(pattern) + 1):
                    if ''.join(self.board[i+k][j] for k in range(len(pattern))) == pattern:
                        for k, char in enumerate(pattern):
                            if char == 'N' and 0 <= i+k < BOARD_SIZE:
                                pos = GomokuPos(i+k, j)
                                if pos not in threatening_positions:
                                    pos.threatening = threatening_point
                                    threatening_positions.append(pos)
                                else: 
                                    id = threatening_positions.index(pos)
                                    old_threatening_point = threatening_positions[id].threatening
                                    if old_threatening_point == 3 or old_threatening_point == 4:
                                        threatening_positions[id].threatening = max(old_threatening_point, threatening_point) + EXTRA_THREATENING_POINT
                                    else:
                                        old_threatening_point -= EXTRA_THREATENING_POINT
                                        threatening_positions[id].threatening = max(old_threatening_point, threatening_point) + EXTRA_THREATENING_POINT
            # duyệt đường chéo chính và đường chéo phụ
            # Ví dụ nếu BOARD_SIZE là 5 ta sẽ cho di chạy đoạn [4,-4] tương ứng có 9 CẶP đường chéo chính đường chéo phụ
            # di là biến chạy dùng để lặp qua 9 cặp này, tương ứng với duyệt lần lượt toàn bộ đường chéo từ dưới lên
            for di in range(BOARD_SIZE-1, -BOARD_SIZE, -1): 
                # 2 danh sách các tọa độ của đường chéo chính và đường chéo phụ đang được xét
                major_diagonal = [(i, i - di) for i in range(max(0, di), min(BOARD_SIZE, di + BOARD_SIZE))]
                minor_diagonal = [(i, BOARD_SIZE - 1 - (i - di)) for i in range(max(0, di), min(BOARD_SIZE, di + BOARD_SIZE))]
                for diagonal in [major_diagonal, minor_diagonal]:
                    # kiểm tra xem đường chéo được xét có chứa đe dọa hay không
                    # nếu có thì biến i sẽ là tọa độ bắt đầu của nó
                    for i in range(len(diagonal) - len(pattern) + 1): 
                        # nếu tại vị trí i của đường chéo xuất hiện mẫu hăm dọa
                        if ''.join(self.board[x][y] for x, y in diagonal[i:i+len(pattern)]) == pattern:
                            for k, char in enumerate(pattern):
                                if char == 'N':
                                    x, y = diagonal[i+k] # lấy tọa độ của điểm hăm dọa (là điểm N, chưa được đánh)
                                    pos = GomokuPos(x, y)
                                    if pos not in threatening_positions:
                                        pos.threatening = threatening_point
                                        threatening_positions.append(pos)
                                    else:
                                        id = threatening_positions.index(pos)
                                        old_threatening_point = threatening_positions[id].threatening
                                        if old_threatening_point == 3 or old_threatening_point == 4:
                                            threatening_positions[id].threatening = max(old_threatening_point, threatening_point) + EXTRA_THREATENING_POINT
                                        else:
                                            old_threatening_point -= EXTRA_THREATENING_POINT
                                            threatening_positions[id].threatening = max(old_threatening_point, threatening_point) + EXTRA_THREATENING_POINT

        if not threatening_positions:
            return [], 0
        
        max_threatening_point = max(pos.threatening for pos in threatening_positions)
        return threatening_positions, max_threatening_point

    def get_best_moves(self):
        '''
        Trả về các nước nên đi nhất hiện tại dựa trên hàm get_threatening_positions
        '''
        me = self.active_turn
        op = 'X' if me == 'O' else 'O'
        # tìm nước đi tốt nhất của 2 bên
        op_threatening_moves, op_threatening_point = self.get_threatening_positions(op) # defense moves
        me_threatening_moves, me_threatening_point = self.get_threatening_positions(me) # attack moves
        # sau khi có nước đi tốt nhất của 2 bên, cần quyết định xem nên tấn công hay phòng thủ 
        # người chơi me sẽ chỉ phòng thủ nếu như nước đi của địch nhiều hăm dọa hơn
        if me_threatening_point >= op_threatening_point:
            # look if the player me has any attack moves
            if me_threatening_moves: 
                return [move for move in me_threatening_moves if move.threatening == me_threatening_point], me_threatening_point
            return [random.choice(self.get_lite_best_moves(me))], me_threatening_point
        elif op_threatening_point >= 4:
            # only need to return one move because that move is eventually played
            return [[move for move in op_threatening_moves if move.threatening == op_threatening_point][0]], op_threatening_point
        return [move for move in op_threatening_moves if move.threatening == op_threatening_point], op_threatening_point

    def get_lite_best_moves(self, me):
        '''
        Return lite-best moves of the me player\n
        Nước đi được đánh giá tốt hơn nếu như có nhiều nước giống nó hơn
        '''
        best_moves = []
        max_allies = -1
        MOVE_LIMITED = 4
        # tìm 8 hướng xung quanh để đếm số lượng nước giống
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
        
        if len(best_moves) < MOVE_LIMITED:
            return best_moves
        else:
            '''
            Lọc tiêu chí phụ, ví dụ ở đây là gần trung tâm hơn
            '''
            center_point = GomokuPos(BOARD_SIZE//2, BOARD_SIZE//2)
            best_moves.sort(key=lambda x: GomokuPos.distance_between(center_point, x))
            return best_moves[0:MOVE_LIMITED]

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

    def show_board(self):
        """ Display the current game board. """
        print("   ", end="")
        for i in range(BOARD_SIZE):
            print(f"{i%10}", end=" ")
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
    Usage:\n
    Use take_turn_alpha_beta method and then get the choice property to get the best move
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

        best_moves, threatening_point = state.get_best_moves()

        if state.active_turn == self.name:
            if depth == 0 and threatening_point >= 4:
                self.choice = best_moves[0]
                print("GET 1 QUICK SOLUTION!!!")
                return
            
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
        Changes the self.choice and then return the best move it can move from its current board game\n
        This function does not change the given board game
        """
        self.minimax_alpha_beta(self.gmk_game, 0, -MINIMAX_INFINITY, MINIMAX_INFINITY)
        print(f"solution:({self.choice.x}, {self.choice.y})")
        return self.choice


'''
if __name__ == "__main__":
    # Create a new Gomoku game
    game = Gomoku()
    bot = GomokuBot(game)

    
    game.board = [
        ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N'],
        ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N'],
        ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N'],
        ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N'],
        ['N', 'N', 'N', 'N', 'X', 'N', 'N', 'O', 'N', 'N'],
        ['N', 'N', 'N', 'X', 'O', 'N', 'O', 'N', 'N', 'N'],
        ['N', 'N', 'N', 'X', 'O', 'O', 'N', 'N', 'N', 'N'],
        ['N', 'N', 'X', 'N', 'O', 'N', 'N', 'N', 'N', 'N'],
        ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N'],
        ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N']]

    # FOR CHECK BOT'S MOVE
    # show before move
    print(game.count_moves())
    game.show_board()
    game.active_turn = 'O'
    bot.name = 'O'
    

    print("Bot is thinking...")
    bot_turn = bot.take_turn_alpha_beta()
    print("Bot moves:")
    game.move(bot_turn)
    
    # show after move
    game.show_board()
    
    
    
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
'''
    


