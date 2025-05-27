import tkinter as tk
from tkinter import messagebox
import random
import time
class Cell:
   def __init__(self, x, y, button):
       self.x = x
       self.y = y
       self.button = button
       self.is_mine = False
       self.is_revealed = False
       self.is_flagged = False
       self.neighbor_mines = 0
class Minesweeper:
   def __init__(self, master):
       self.master = master
       self.master.title("Minesweeper by Ome")
       self.master.configure(bg="#f0f0f0")
       self.levels = {
           "ง่าย": (8, 8, 10),
           "ปานกลาง": (12, 12, 20),
           "ยาก": (16, 16, 40)
       }
       self.create_menu()
   def create_menu(self):
       self.clear_window()
       tk.Label(self.master, text="เลือกความยาก", font=("Arial", 18, "bold"), bg="#f0f0f0").pack(pady=15)
       for level in self.levels:
           tk.Button(
               self.master,
               text=level,
               font=("Arial", 14),
               width=15,
               bg="#d9e4f5",
               relief=tk.RAISED,
               command=lambda l=level: self.start_game(*self.levels[l])
           ).pack(pady=7)
   def clear_window(self):
       for widget in self.master.winfo_children():
           widget.destroy()
   def start_game(self, rows, cols, mines):
       self.clear_window()
       self.rows, self.cols, self.mines = rows, cols, mines
       self.cells = []
       self.flags_left = self.mines
       self.start_time = None
       self.game_over_flag = False
       self.info_frame = tk.Frame(self.master, bg="#f0f0f0")
       self.info_frame.pack(pady=5)
       self.timer_label = tk.Label(self.info_frame, text="เวลา: 0 วินาที", font=("Arial", 12), bg="#f0f0f0")
       self.timer_label.pack(side=tk.LEFT, padx=10)
       self.flags_label = tk.Label(self.info_frame, text=f"ธงที่เหลือ: {self.flags_left}", font=("Arial", 12), bg="#f0f0f0")
       self.flags_label.pack(side=tk.LEFT, padx=10)
       self.reset_button = tk.Button(self.info_frame, text="เริ่มใหม่", font=("Arial", 12), command=lambda: self.start_game(rows, cols, mines))
       self.reset_button.pack(side=tk.RIGHT, padx=10)
       self.board_frame = tk.Frame(self.master, bg="#b0c4de", bd=2, relief=tk.SUNKEN)
       self.board_frame.pack(pady=10)
       for x in range(self.rows):
           row = []
           for y in range(self.cols):
               btn = tk.Button(self.board_frame, width=3, height=1,
                               font=("Arial", 14),
                               bg="#e6e6e6",
                               command=lambda x=x, y=y: self.reveal_cell(x, y))
               btn.bind("<Button-3>", lambda e, x=x, y=y: self.toggle_flag(x, y))
               btn.grid(row=x, column=y, padx=1, pady=1)
               row.append(Cell(x, y, btn))
           self.cells.append(row)
       self.place_mines()
       self.count_neighbor_mines()
       self.update_timer()
   def place_mines(self):
       positions = random.sample([(x, y) for x in range(self.rows) for y in range(self.cols)], self.mines)
       for x, y in positions:
           self.cells[x][y].is_mine = True
   def count_neighbor_mines(self):
       for x in range(self.rows):
           for y in range(self.cols):
               if self.cells[x][y].is_mine:
                   continue
               count = 0
               for dx in [-1, 0, 1]:
                   for dy in [-1, 0, 1]:
                       nx, ny = x + dx, y + dy
                       if 0 <= nx < self.rows and 0 <= ny < self.cols and self.cells[nx][ny].is_mine:
                           count += 1
               self.cells[x][y].neighbor_mines = count
   def reveal_cell(self, x, y):
       if self.game_over_flag:
           return
       cell = self.cells[x][y]
       if not self.start_time:
           self.start_time = time.time()
       if cell.is_flagged or cell.is_revealed:
           return
       cell.is_revealed = True
       if cell.is_mine:
           cell.button.config(text="💣", bg="#ff6666")
           self.end_game(False)
           return
       cell.button.config(relief=tk.SUNKEN, bg="#d0d0d0")
       if cell.neighbor_mines > 0:
           cell.button.config(text=str(cell.neighbor_mines), fg="blue")
       else:
           for dx in [-1, 0, 1]:
               for dy in [-1, 0, 1]:
                   nx, ny = x + dx, y + dy
                   if 0 <= nx < self.rows and 0 <= ny < self.cols:
                       self.reveal_cell(nx, ny)
       self.check_win()
   def toggle_flag(self, x, y):
       if self.game_over_flag:
           return
       cell = self.cells[x][y]
       if cell.is_revealed:
           return
       if cell.is_flagged:
           cell.is_flagged = False
           cell.button.config(text="", fg="black")
           self.flags_left += 1
       else:
           if self.flags_left == 0:
               return
           cell.is_flagged = True
           cell.button.config(text="⛳️", fg="green")
           self.flags_left -= 1
       self.flags_label.config(text=f"ธงที่เหลือ: {self.flags_left}")
   def check_win(self):
       for row in self.cells:
           for cell in row:
               if not cell.is_mine and not cell.is_revealed:
                   return
       self.end_game(True)
   def end_game(self, won):
       self.game_over_flag = True
       for row in self.cells:
           for cell in row:
               if cell.is_mine:
                   cell.button.config(text="💣", bg="#ff9999")
       time_taken = int(time.time() - self.start_time) if self.start_time else 0
       if won:
           messagebox.showinfo("ชนะ!", f"คุณชนะ! ใช้เวลา {time_taken} วินาที")
       else:
           messagebox.showerror("แพ้!", "คุณแพ้! เจอระเบิดเข้าแล้ว")
   def update_timer(self):
       if self.start_time and not self.game_over_flag:
           elapsed = int(time.time() - self.start_time)
           self.timer_label.config(text=f"เวลา: {elapsed} วินาที")
       self.master.after(1000, self.update_timer)
if __name__ == "__main__":
   root = tk.Tk()
   game = Minesweeper(root)
   root.mainloop()