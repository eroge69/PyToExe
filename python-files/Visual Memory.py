import tkinter as tk
import random

class MemoryGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Grid Memory Game")
        self.show_start_menu()

    def show_start_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Grid size (m x m):").pack()
        self.m_entry = tk.Entry(self.root)
        self.m_entry.pack()

        tk.Label(self.root, text="Highlighted squares per grid (n):").pack()
        self.n_entry = tk.Entry(self.root)
        self.n_entry.pack()

        tk.Label(self.root, text="Number of grids (k):").pack()
        self.k_entry = tk.Entry(self.root)
        self.k_entry.pack()

        start_button = tk.Button(self.root, text="Start Game", command=self.get_input_and_start)
        start_button.pack(pady=10)

    def get_input_and_start(self):
        try:
            self.m = int(self.m_entry.get())
            self.n = int(self.n_entry.get())
            self.k = int(self.k_entry.get())
        except ValueError:
            return  # invalid input, do nothing
        self.start_game()

    def start_game(self):
        self.current_display_index = 0
        self.current_guess_index = 0
        self.stored_grids = []
        self.guess_grid = set()
        self.phase = 'showing'
        self.buttons = []
        self.create_grid()
        self.show_next_grid()

    def create_grid(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.buttons = []
        for i in range(self.m):
            row = []
            for j in range(self.m):
                btn = tk.Button(self.root, width=6, height=3,
                                command=lambda x=i, y=j: self.select_square(x, y))
                btn.grid(row=i, column=j)
                row.append(btn)
            self.buttons.append(row)

        if self.phase == 'guessing':
            submit = tk.Button(self.root, text="Submit", command=self.check_guess)
            submit.grid(row=self.m, column=0, columnspan=self.m)

    def show_next_grid(self):
        if self.current_display_index >= self.k:
            self.phase = 'guessing'
            self.current_guess_index = 0
            self.create_grid()
            return

        self.create_grid()
        grid = self.generate_grid()
        self.stored_grids.append(grid)

        for x, y in grid:
            self.buttons[x][y].config(bg='blue')

        self.root.update()
        self.root.after(2000, self.hide_grid)

    def hide_grid(self):
        for i in range(self.m):
            for j in range(self.m):
                self.buttons[i][j].config(bg='SystemButtonFace')
        self.current_display_index += 1
        self.root.after(500, self.show_next_grid)

    def generate_grid(self):
        all_positions = [(i, j) for i in range(self.m) for j in range(self.m)]
        return set(random.sample(all_positions, self.n))

    def select_square(self, i, j):
        if self.phase != 'guessing':
            return
        if (i, j) in self.guess_grid:
            self.buttons[i][j].config(relief='raised')
            self.guess_grid.remove((i, j))
        else:
            self.buttons[i][j].config(relief='sunken')
            self.guess_grid.add((i, j))

    def check_guess(self):
        correct_grid = self.stored_grids[self.current_guess_index]

        for i in range(self.m):
            for j in range(self.m):
                if (i, j) in correct_grid and (i, j) in self.guess_grid:
                    self.buttons[i][j].config(bg='green')
                elif (i, j) in correct_grid:
                    self.buttons[i][j].config(bg='yellow')
                elif (i, j) in self.guess_grid:
                    self.buttons[i][j].config(bg='red')

        self.root.update()
        self.current_guess_index += 1
        self.guess_grid = set()

        if self.current_guess_index < self.k:
            self.root.after(2000, self.create_grid)
        else:
            self.root.after(2000, self.restart_game)

    def restart_game(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        label = tk.Label(self.root, text="Game Over! Restarting...")
        label.pack(pady=20)
        self.root.update()
        self.root.after(2000, self.start_game)

if __name__ == "__main__":
    root = tk.Tk()
    game = MemoryGame(root)
    root.mainloop()
