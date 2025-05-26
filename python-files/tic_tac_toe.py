import tkinter as tk
from tkinter import messagebox
import random

vs_computer = False  # False für 2 Spieler, True für 1 Spieler vs Computer

def check_win():
    for i in range(3):
        if buttons[i][0]["text"] == buttons[i][1]["text"] == buttons[i][2]["text"] != "":
            return True
        if buttons[0][i]["text"] == buttons[1][i]["text"] == buttons[2][i]["text"] != "":
            return True
    if buttons[0][0]["text"] == buttons[1][1]["text"] == buttons[2][2]["text"] != "":
        return True
    if buttons[0][2]["text"] == buttons[1][1]["text"] == buttons[2][0]["text"] != "":
        return True
    return False

def check_draw():
    for row in buttons:
        for button in row:
            if button["text"] == "":
                return False
    return True

def on_click(row, col):
    if buttons[row][col]["text"] == "":
        buttons[row][col]["text"] = current_player.get()
        if check_win():
            messagebox.showinfo("Game Over", current_player.get() + " wins!")
            reset_game()
        elif check_draw():
            messagebox.showinfo("Draw", "The game is a draw!")
            reset_game()
        else:
            if vs_computer and current_player.get() == "ก":
                root.after(300, computer_move)  
            else:
                current_player.set("ข" if current_player.get() == "ก" else "ก")

def computer_move():
    def can_win(player):
        for r in range(3):
            for c in range(3):
                if buttons[r][c]['text'] == "":
                    buttons[r][c]['text'] = player
                    if check_win():
                        buttons[r][c]['text'] = ""
                        return r, c
                    buttons[r][c]['text'] = ""
        return None

    move = can_win("ข")  # Computer gewinnt?
    if not move:
        move = can_win("ก")  # Spieler blocken
    if not move and buttons[1][1]['text'] == "":
        move = (1, 1)  # Mitte nehmen
    if not move:
        for r, c in [(0, 0), (0, 2), (2, 0), (2, 2)]:  # Ecken
            if buttons[r][c]['text'] == "":
                move = (r, c)
                break
    if not move:
        for r, c in [(0,1), (1,0), (1,2), (2,1)]:  # Kanten
            if buttons[r][c]['text'] == "":
                move = (r, c)
                break

    if move:
        r, c = move
        buttons[r][c]['text'] = "ข"
        if check_win():
            messagebox.showinfo("Game Over", "Computer gewinnt!")
            reset_game()
        elif check_draw():
            messagebox.showinfo("Draw", "Unentschieden!")
            reset_game()
        else:
            current_player.set("ก")



def reset_game():
    for row in buttons:
        for button in row:
            button["text"] = ""
    current_player.set("ก")

root = tk.Tk()
root.title("Tic Tac Toe")

current_player = tk.StringVar(value="ก")
buttons = []

for row in range(3):
    row_buttons = []
    for col in range(3):
        button = tk.Button(root, text="", width=6, height=3, font=("Arial", 24),
                           command=lambda r=row, c=col: on_click(r, c))
        button.grid(row=row, column=col)
        row_buttons.append(button)
    buttons.append(row_buttons)

root.mainloop()
