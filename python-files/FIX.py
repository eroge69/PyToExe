import tkinter as tk
from tkinter import filedialog, messagebox
import os
def select_gta5_path():
    path = filedialog.askdirectory(title="Выберите папку GTA 5")
    gta5_path_var.set(path)
def select_archiev_fix_folder():
    path = filedialog.askdirectory(title="Выберите папку Archiev Fix")
    archiev_fix_folder_var.set(path)
def find_archiev_fix_exe(folder):
    for file in os.listdir(folder):
        if file.lower().endswith(".exe"):
            return os.path.join(folder, file)
    return None
def open_update_rpf():
    gta5_path = gta5_path_var.get()
    archiev_fix_folder = archiev_fix_folder_var.get()
    if not os.path.exists(gta5_path):
        messagebox.showerror("Ошибка", "Папка GTA 5 не найдена!")
        return
    archiev_fix_path = find_archiev_fix_exe(archiev_fix_folder)
    if not archiev_fix_path:
        messagebox.showerror("Ошибка", "Не найден исполняемый файл (.exe) в указанной папке Archiev Fix!")
        return
    update_folder = os.path.join(gta5_path, "update")
    update_rpf = os.path.join(update_folder, "update.rpf")
    if not os.path.exists(update_rpf):
        messagebox.showerror("Ошибка", "Файл update.rpf не найден!")
        return
    os.startfile(update_folder)
    os.startfile(archiev_fix_path)
    os.startfile(update_rpf)
    messagebox.showinfo("Успех", "Файл update.rpf открыт в Archiev Fix!")
root = tk.Tk()
root.title("Выбор пути GTA 5 и Archiev Fix")
root.geometry("500x200")
gta5_path_var = tk.StringVar()
archiev_fix_folder_var = tk.StringVar()
frame = tk.Frame(root, padx=10, pady=10)
frame.pack(fill=tk.BOTH, expand=True)
tk.Label(frame, text="Путь к GTA 5:").grid(row=0, column=0, sticky="w")
tk.Entry(frame, textvariable=gta5_path_var, width=50).grid(row=0, column=1)
tk.Button(frame, text="Обзор", command=select_gta5_path).grid(row=0, column=2)
tk.Label(frame, text="Папка Archiev Fix:").grid(row=1, column=0, sticky="w")
tk.Entry(frame, textvariable=archiev_fix_folder_var, width=50).grid(row=1, column=1)
tk.Button(frame, text="Обзор", command=select_archiev_fix_folder).grid(row=1, column=2)
tk.Button(frame, text="Открыть update.rpf", command=open_update_rpf).grid(row=2, column=1, pady=10)
root.mainloop()
