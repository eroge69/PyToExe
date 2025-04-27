import tkinter as tk
from tkinter import messagebox, filedialog
import os
from PIL import Image, ImageTk
import json

class WindowsSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Windows Simulator")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#00A1D6')  # Цвет фона рабочего стола Windows

        # Хранилище позиций иконок
        self.icons = {}
        self.load_icon_positions()

        # Панель задач
        self.taskbar = tk.Frame(self.root, bg='#2D2D2D', height=40)
        self.taskbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Кнопка "Пуск"
        self.start_button = tk.Button(self.taskbar, text="Start", bg='#2D2D2D', fg='white', command=self.show_start_menu)
        self.start_button.pack(side=tk.LEFT, padx=5)

        # Часы
        self.clock_label = tk.Label(self.taskbar, text="08:31", bg='#2D2D2D', fg='white')
        self.clock_label.pack(side=tk.RIGHT, padx=5)
        self.update_clock()

        # Создание иконок на рабочем столе
        self.create_desktop_icons()

        # Привязка правого клика для контекстного меню
        self.root.bind("<Button-3>", self.show_context_menu)

    def load_icon_positions(self):
        # Загрузка позиций иконок из файла (если он есть)
        try:
            with open("icon_positions.json", "r") as f:
                self.icons = json.load(f)
        except FileNotFoundError:
            self.icons = {
                "Notepad": {"x": 50, "y": 50, "command": self.open_notepad},
                "File Explorer": {"x": 150, "y": 50, "command": self.open_file_explorer},
                "Recycle Bin": {"x": 250, "y": 50, "command": self.open_recycle_bin}
            }

    def save_icon_positions(self):
        # Сохранение позиций иконок в файл
        with open("icon_positions.json", "w") as f:
            json.dump(self.icons, f)

    def create_desktop_icons(self):
        for name, info in self.icons.items():
            # Создание иконки
            label = tk.Label(self.root, text=name, bg='#00A1D6', fg='white', font=("Arial", 10))
            label.place(x=info["x"], y=info["y"])
            label.bind("<B1-Motion>", lambda event, n=name: self.move_icon(event, n))
            label.bind("<Button-1>", lambda event, cmd=info["command"]: cmd())

    def move_icon(self, event, name):
        # Перемещение иконки
        new_x = event.widget.winfo_x() + event.x - 20
        new_y = event.widget.winfo_y() + event.y - 20
        event.widget.place(x=new_x, y=new_y)
        self.icons[name]["x"] = new_x
        self.icons[name]["y"] = new_y
        self.save_icon_positions()

    def update_clock(self):
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M")
        self.clock_label.config(text=current_time)
        self.root.after(60000, self.update_clock)  # Обновление каждую минуту

    def show_start_menu(self):
        start_menu = tk.Toplevel(self.root)
        start_menu.title("Start Menu")
        start_menu.geometry("200x300+0+500")
        start_menu.configure(bg='#2D2D2D')

        apps = ["Notepad", "File Explorer", "Shutdown"]
        for app in apps:
            btn = tk.Button(start_menu, text=app, bg='#2D2D2D', fg='white', width=20,
                            command=lambda a=app: self.start_menu_action(a))
            btn.pack(pady=5)

    def start_menu_action(self, app):
        if app == "Notepad":
            self.open_notepad()
        elif app == "File Explorer":
            self.open_file_explorer()
        elif app == "Shutdown":
            self.root.quit()

    def show_context_menu(self, event):
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="New Folder", command=self.create_new_folder)
        context_menu.add_command(label="Refresh", command=self.refresh_desktop)
        context_menu.add_separator()
        context_menu.add_command(label="Properties", command=self.show_properties)
        context_menu.tk_popup(event.x_root, event.y_root)

    def create_new_folder(self):
        folder_name = "New Folder"
        self.icons[folder_name] = {"x": 50, "y": 50, "command": lambda: messagebox.showinfo("Info", "New Folder Opened")}
        self.refresh_desktop()

    def refresh_desktop(self):
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Label):
                widget.destroy()
        self.create_desktop_icons()

    def show_properties(self):
        messagebox.showinfo("Properties", "Windows Simulator\nVersion: 1.0\nCreated by: xAI")

    def open_notepad(self):
        notepad = tk.Toplevel(self.root)
        notepad.title("Notepad")
        notepad.geometry("400x300")
        text_area = tk.Text(notepad)
        text_area.pack(expand=True, fill="both")

    def open_file_explorer(self):
        messagebox.showinfo("File Explorer", "Opening File Explorer (simulated).")
        # Здесь можно добавить функционал для имитации проводника

    def open_recycle_bin(self):
        messagebox.showinfo("Recycle Bin", "Opening Recycle Bin (simulated).")

if __name__ == "__main__":
    root = tk.Tk()
    app = WindowsSimulator(root)
    root.mainloop()