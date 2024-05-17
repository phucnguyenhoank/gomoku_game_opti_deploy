import tkinter as tk
from tkinter import ttk, messagebox
from gomoku import Gomoku, GomokuBot, GomokuPos, BOARD_SIZE

class GomokuGUI(tk.Tk):
    def __init__(self, who_go_first='BOT'):
        super().__init__()
        self.title("Welcome To Gomoku")
        self.geometry("700x700")

        self.game = Gomoku()
        self.bot = GomokuBot(self.game)
        self.who_go_first = who_go_first

        self.create_widgets()
        self.place_widgets()

        if self.who_go_first == "BOT":
            self.bot_move()
        else:
            self.bot.name = 'O'

    def create_widgets(self):
        self.fra_blanks = ttk.Frame(self)
        self.labels = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                self.labels[i][j] = tk.Label(self.fra_blanks, width=2, height=1, text='', relief=tk.RAISED, bg='white', font=("Helvetica", 16))
                self.labels[i][j].grid(row=i, column=j, sticky='nsew')
                self.labels[i][j].bind('<Button-1>', lambda e, row=i, col=j: self.make_move(row, col))

        self.status_label = ttk.Label(self, text="", font=("Helvetica", 16))
        
    def place_widgets(self):
        self.fra_blanks.grid(row=0, column=0)
        self.status_label.grid(row=BOARD_SIZE, columnspan=10)

    def bot_move(self):
        self.status_label.config(text="Bot is thinking... be patient...")
        self.update()
        print("Bot is thinking...")
        self.bot.take_turn_alpha_beta()
        print("Bot done thinking.")
        self.status_label.config(text="Bot done thinking.")
        self.game.move(self.bot.choice)
        self.update_board(self.bot.choice)
        self.update()

    def human_move(self, row, col):
        self.game.move(GomokuPos(row, col))
        self.update_board(GomokuPos(row, col))
        self.update()

    def make_move(self, row, col):
        self.human_move(row, col)
        if self.game.over():
            self.show_result()
        else:
            self.bot_move()
            if self.game.over():
                self.show_result()

    def update_board(self, pos=None):
        if pos is not None:
            x = pos.x
            y = pos.y
            self.labels[x][y]['text'] = self.game.board[x][y]
            color = ''
            move_name = self.game.board[x][y]
            if move_name == 'X':
                color = 'blue'
            else:
                color = 'red'
            self.labels[x][y].config(text=move_name, fg=color)
        else:
            for i in range(BOARD_SIZE):
                for j in range(BOARD_SIZE):
                    self.labels[i][j]['text'] = ''

    def show_result(self):
        result = self.game.win()
        if result == 'T':
            messagebox.showinfo("Game Over", "It's a tie!")
        else:
            winner = "Player X" if result == 'X' else "Player O"
            messagebox.showinfo("Game Over", f"{winner} wins!")

        self.game = Gomoku()
        self.bot = GomokuBot(self.game)
        self.update_board()
        self.update()
        if self.who_go_first == "BOT":
            self.bot_move()
        else:
            self.bot.name = 'O'


if __name__ == "__main__":
    app = GomokuGUI()
    app.mainloop()

