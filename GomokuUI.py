import tkinter as tk
from tkinter import ttk, messagebox
from gomoku import Gomoku, GomokuBot, GomokuPos, BOARD_SIZE


# TODO: Thêm chức năng expand tự động để các nước đi lúc nào cũng ở trung tâm của bàn cờ

class GomokuGUI(tk.Toplevel):
    first_active_turn = ""
    def __init__(self, parent, user_rule = 'O', who_go_first = 'BOT'):
        super().__init__(parent)
        self.title("Gomoku")
        self.geometry("600x600")

        self.game = Gomoku()
        self.game.active_turn = ''
        if who_go_first == "YOU":
            self.game.active_turn = user_rule
        else:
            self.game.active_turn = 'O' if user_rule == 'X' else 'X'

        self.bot = GomokuBot(self.game)
        self.who_go_first = who_go_first

        self.first_active_turn = self.game.active_turn

        self.create_widgets()
        self.place_widgets()

        if self.who_go_first == "BOT":
            self.bot_move()


    def create_widgets(self):
        self.fra_blanks = ttk.Frame(self)
        self.buttons = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                self.buttons[i][j] = tk.Button(self.fra_blanks, width=2, text='')
                self.buttons[i][j].grid(row=i, column=j, sticky='nsew')
                self.buttons[i][j].bind('<Button-1>', lambda e, row=i, col=j: self.make_move(row, col))
    
    def place_widgets(self):
        self.fra_blanks.grid(row=0, column=0)


    def bot_move(self):
        '''
        Move and update the board game
        '''
        print("Bot is thinking...")
        self.bot.take_turn_alpha_beta()
        print("Bot think done.")

        self.game.move(self.bot.choice)
        self.update_board()

    def human_move(self, row, col):
        '''
        Get the move from the user, move and then update the board game
        '''
        self.game.move(GomokuPos(row, col))
        self.update_board()

        

    def make_move(self, row, col):
        if self.game.board[row][col] == 'N' and not self.game.over():
            self.human_move(row, col)
            if self.game.over():
                self.show_result()
            else:
                self.bot_move()
                if self.game.over():
                    self.show_result()
            

    def update_board(self):
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self.game.board[i][j] != 'N':
                    self.buttons[i][j]['text'] = self.game.board[i][j]
                else:
                    self.buttons[i][j]['text'] = ''


    def show_result(self):
        result = self.game.win()
        if result == 'T':
            messagebox.showinfo("Game Over", "It's a tie!")
        else:
            winner = "Player X" if result == 'X' else "Player O"
            messagebox.showinfo("Game Over", f"{winner} wins!")

        # Reset the game after showing the result
        self.game = Gomoku()
        self.game.active_turn = self.first_active_turn
        self.bot = GomokuBot(self.game)
        self.update_board()
        if self.who_go_first == "BOT":
            self.bot_move()

class GomokuSelector(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gomoku Welcome")

        self.create_widgets()
        self.place_widgets()
        self.associate_events()



    def create_widgets(self):
        self.fra_user_options = tk.Frame(self)
        self.lbl_user_rule = ttk.Label(self.fra_user_options, text="Your rule:")
        self.cb_user_rule = ttk.Combobox(self.fra_user_options, values=('X', 'O'), state='readonly')
        self.cb_user_rule.set('O')

        self.lbl_who_go_first = ttk.Label(self.fra_user_options, text="Who go first:")
        self.cb_who_go_first = ttk.Combobox(self.fra_user_options, values=('YOU', 'BOT'), state='readonly')
        self.cb_who_go_first.set('BOT')

        self.btn_play = ttk.Button(self.fra_user_options, text="Play")


    def place_widgets(self):
        self.lbl_user_rule.grid(row=0, column=0)
        self.cb_user_rule.grid(row=1, column=0)
        self.lbl_who_go_first.grid(row=2, column=0)
        self.cb_who_go_first.grid(row=3, column=0)
        self.btn_play.grid(row=4, column=0)
        self.fra_user_options.grid(row=1, column=0)

    def associate_events(self):
        self.btn_play.bind("<Button-1>", lambda e: self.btn_play_Button_1())

    def btn_play_Button_1(self):
        tic_tac_toe_gui = GomokuGUI(self, self.cb_user_rule.get(), self.cb_who_go_first.get())
        tic_tac_toe_gui.grab_set()




if __name__ == "__main__":
    app = GomokuSelector()
    app.mainloop()



