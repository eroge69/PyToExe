import tkinter as tk
import random

class Cell:
    def __init__(self, x, y, btn):
        self.x = x
        self.y = y
        self.button = btn
        self.is_mine = False
        self.is_open = False
        self.is_flagged = False
        self.neighbor_mines = 0

class Minesweeper:
    def __init__(self, root, rows=10, cols=10, mines=10):
        self.root = root
        self.rows = rows
        self.cols = cols
        self.total_mines = mines
        self.flags_left = mines
        self.cells = []

        self.frame = tk.Frame(self.root, bg="#2c3e50")
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.header = tk.Frame(self.frame, bg="#2c3e50")
        self.header.pack(fill=tk.X)

        self.info_label = tk.Label(self.header, text=f"🚩 Flags left: {self.flags_left}", font=("Arial", 14),
                                   fg="white", bg="#2c3e50")
        self.info_label.pack(side=tk.LEFT, padx=5)

        self.restart_button = tk.Button(self.header, text="🔄 Restart", font=("Arial", 12),
                                        command=self.restart_game, bg="#1abc9c", fg="white")
        self.restart_button.pack(side=tk.RIGHT, padx=5)

        self.board_frame = tk.Frame(self.frame, bg="#34495e")
        self.board_frame.pack(fill=tk.BOTH, expand=True)

        self.create_widgets()
        self.place_mines()
        self.count_neighbor_mines()

        self.root.bind("<Configure>", self.resize_cells)

    def create_widgets(self):
        for x in range(self.rows):
            row = []
            for y in range(self.cols):
                btn = tk.Button(self.board_frame,
                                font=("Arial", 10, "bold"),
                                bg="#bdc3c7", relief="raised",
                                command=lambda x=x, y=y: self.on_click(x, y))
                btn.bind("<Button-3>", lambda event, x=x, y=y: self.toggle_flag(x, y))
                btn.grid(row=x, column=y, padx=1, pady=1, sticky="nsew")
                row.append(Cell(x, y, btn))
            self.cells.append(row)

        for x in range(self.rows):
            self.board_frame.grid_rowconfigure(x, weight=1)
        for y in range(self.cols):
            self.board_frame.grid_columnconfigure(y, weight=1)

    def resize_cells(self, event=None):
        total_width = self.board_frame.winfo_width()
        total_height = self.board_frame.winfo_height()

        cell_width = total_width // self.cols
        cell_height = total_height // self.rows

        size = min(cell_width, cell_height)

        font_size = max(6, size // 2)

        for x in range(self.rows):
            for y in range(self.cols):
                btn = self.cells[x][y].button
                btn.config(width=1, height=1,
                           font=("Arial", font_size, "bold"),
                           padx=0, pady=0)

    def place_mines(self):
        count = 0
        while count < self.total_mines:
            x = random.randint(0, self.rows - 1)
            y = random.randint(0, self.cols - 1)
            if not self.cells[x][y].is_mine:
                self.cells[x][y].is_mine = True
                count += 1

    def count_neighbor_mines(self):
        for x in range(self.rows):
            for y in range(self.cols):
                if self.cells[x][y].is_mine:
                    continue
                count = 0
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.rows and 0 <= ny < self.cols:
                            if self.cells[nx][ny].is_mine:
                                count += 1
                self.cells[x][y].neighbor_mines = count

    def on_click(self, x, y):
        cell = self.cells[x][y]
        if cell.is_open or cell.is_flagged:
            return
        if cell.is_mine:
            cell.button.config(text='💣', bg="#e74c3c", disabledforeground="black")
            self.game_over()
        else:
            self.reveal(x, y)

    def reveal(self, x, y):
        cell = self.cells[x][y]
        if cell.is_open or cell.is_flagged:
            return
        cell.is_open = True
        cell.button.config(relief="sunken", bg="#ecf0f1", state="disabled")

        colors = ['blue', 'green', 'red', 'purple', 'maroon', 'turquoise', 'black', 'gray']
        if cell.neighbor_mines > 0:
            color = colors[cell.neighbor_mines - 1]
            cell.button.config(text=str(cell.neighbor_mines), fg=color)
        else:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.rows and 0 <= ny < self.cols:
                        self.reveal(nx, ny)

    def toggle_flag(self, x, y):
        cell = self.cells[x][y]
        if cell.is_open:
            return
        if cell.is_flagged:
            cell.button.config(text='', bg="#bdc3c7")
            cell.is_flagged = False
            self.flags_left += 1
        else:
            if self.flags_left <= 0:
                return
            cell.button.config(text='🚩', fg="red", bg="#f39c12")
            cell.is_flagged = True
            self.flags_left -= 1
        self.info_label.config(text=f"🚩 Flags left: {self.flags_left}")

    def game_over(self):
        for row in self.cells:
            for cell in row:
                if cell.is_mine:
                    cell.button.config(text='💣', bg="#e74c3c", fg="black")
                cell.button.config(state="disabled")
        self.info_label.config(text="💥 Game Over!")

    def restart_game(self):
        self.frame.destroy()
        create_menu(self.root)

# ---------- Главное меню ----------
def create_menu(root):
    for widget in root.winfo_children():
        widget.destroy()

    root.configure(bg="#34495e")
    menu_frame = tk.Frame(root, bg="#34495e")
    menu_frame.pack(expand=True)

    title = tk.Label(menu_frame, text="🎮 Сапёр", font=("Arial", 24, "bold"),
                     bg="#34495e", fg="white")
    title.pack(pady=20)

    def start_game(rows, cols, mines):
        menu_frame.destroy()
        Minesweeper(root, rows, cols, mines)

    tk.Button(menu_frame, text="😊 Лёгкий (8x8, 10 мин)", width=25, font=("Arial", 14),
              command=lambda: start_game(8, 8, 10), bg="#27ae60", fg="white").pack(pady=10)

    tk.Button(menu_frame, text="😎 Средний (12x12, 20 мин)", width=25, font=("Arial", 14),
              command=lambda: start_game(12, 12, 20), bg="#2980b9", fg="white").pack(pady=10)

    tk.Button(menu_frame, text="😱 Сложный (16x16, 40 мин)", width=25, font=("Arial", 14),
              command=lambda: start_game(16, 16, 40), bg="#c0392b", fg="white").pack(pady=10)


# ---------- Запуск ----------
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Сапёр")
    root.geometry("600x700")
    root.minsize(400, 400)
    root.resizable(True, True)
    create_menu(root)
    root.mainloop()
