import streamlit as st
import pandas as pd
import string
from gomoku import Gomoku, GomokuBot, GomokuPos, BOARD_SIZE
import time


BOT_MOVE_LETTER = 'X'
HUMAN_MOVE_LETTER = 'O'
row_names = list(range(1, BOARD_SIZE + 1))
column_names = list(string.ascii_uppercase)[:BOARD_SIZE] # ['A', ..., 'T']

row = st.selectbox('Select row', options=row_names)
col = st.selectbox('Select column', options=column_names)

def draw_to_UI(number_row, letter_column, moved_letter):
    st.session_state.data.loc[number_row, letter_column] = moved_letter
    st.session_state.last_changed_cell = (number_row, letter_column)


status_bar = st.empty()
status_bar.markdown(f"**Your turn...**", unsafe_allow_html=True)


def bot_make_move():
    status_bar.markdown(f"**Bot is thinking, please be patient... ^^**", unsafe_allow_html=True)
    game = Gomoku.deserialize(st.session_state.game)
    bot = GomokuBot(game)
    bot_turn = bot.take_turn_alpha_beta()
    bot_number_row, bot_letter_column = bot_turn.to_standard_pos()
    game.move(bot_turn)
    draw_to_UI(bot_number_row, bot_letter_column, BOT_MOVE_LETTER)
    status_bar.markdown("**Bot moved!**", unsafe_allow_html=True)
    st.session_state.game = game.serialize()
    st.session_state.winner = Gomoku.deserialize(st.session_state.game).win()
    st.session_state.current_is_human_move = True
    st.rerun()

def show_winner(winner):
    if winner == 'X':
        st.success('Bot (X) wins!')
    elif winner == 'O':
        st.success('Human (O) wins!')
    else:
        st.info('Tie!')


if st.button('Move'):
    if st.session_state.winner == 'N':
        game = Gomoku.deserialize(st.session_state.game)
        gomoku_pos = GomokuPos.to_gomoku_pos(row, col)
        if not game.have_occupied(gomoku_pos):
            draw_to_UI(row, col, HUMAN_MOVE_LETTER)
            game.move(GomokuPos.to_gomoku_pos(row, col))
            st.session_state.game = game.serialize()
            st.session_state.winner = Gomoku.deserialize(st.session_state.game).win()
            st.session_state.current_is_human_move = False
            st.rerun()
        else:
            status_bar.markdown(f"*Sorry, {row}{col} has been occupied!*")


if st.button('Replay'):
    # Reset the game state
    st.session_state.game = Gomoku().serialize()
    # Reset the DataFrame
    data = pd.DataFrame([[' ' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)])
    data.columns = column_names
    data.index = row_names
    st.session_state.data = data
    st.session_state.last_changed_cell = None
    st.session_state.have_not_any_move_yet = True
    st.session_state.current_is_human_move = False

    status_bar.markdown(f"**Game reset! Let's play again... ^^**", unsafe_allow_html=True)
    

if 'game' not in st.session_state:
    st.session_state.game = Gomoku().serialize()
    data = pd.DataFrame([[' ' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)])
    data.columns = column_names
    data.index = row_names
    st.session_state.data = data
    st.session_state.last_changed_cell = None
    st.session_state.have_not_any_move_yet = True
    st.session_state.current_is_human_move = False
    st.session_state.winner = 'N'
elif st.session_state.winner != 'N':
    show_winner(st.session_state.winner)

    
# Display the DataFrame as a custom HTML table with cell text color
html_table = "<table>"
html_table += "<tr>"
html_table += "<th></th>"  # Empty header for top-left corner
for col in column_names:
    html_table += f'<th style="text-align: center;">{col}</th>'
html_table += "</tr>"
for i, (index, row) in enumerate(st.session_state.data.iterrows(), 1):
    html_table += "<tr>"
    html_table += f'<th style="text-align: center;">{index}</th>'  # Row name
    for j, cell in enumerate(row):
        text_color = "red" if cell == 'O' else "blue" if cell == 'X' else "black"  # Change text color based on value
        cell_style = 'background-color: yellow;' if st.session_state.last_changed_cell == (i, column_names[j]) else ''  # Highlight last changed cell
        html_table += f'<td style="text-align: center; color: {text_color}; {cell_style}">{cell}</td>'
    html_table += "</tr>"
html_table += "</table>"
st.write(html_table, unsafe_allow_html=True)



if not st.session_state.current_is_human_move or st.session_state.have_not_any_move_yet:
    st.session_state.have_not_any_move_yet = False
    bot_make_move()
    
