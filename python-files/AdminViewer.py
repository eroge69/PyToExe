
# Програма 1: AdminViewer (для запуску на ПК адміністратора)
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Функція для парсингу лог-файлу
def parse_log_file(filepath):
    data = {
        'HOSTNAME': '', 'CPU': '', 'OS': '', 'MAC': '',
        'ESET UPDATE': '', 'ESET VERS': '',
        'MS OFFICE': '', 'LIBREOFFICE': '', 'GOOGLE CHROME': '',
        'PEAZIP': '', '7ZIP': '',
        'LAST_SEEN_ONLINE': '', 'LOG_TIME': '',
        'DATA 1': ''
    }
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            for key in data.keys():
                if line.startswith(key + ":"):
                    data[key] = line.strip().split(": ", 1)[-1]
    return data

# Виведення таблиці з логів
def load_logs():
    global log_dir
    log_dir = filedialog.askdirectory(title="Оберіть папку з логами")
    if not log_dir:
        return
    tree.delete(*tree.get_children())
    for filename in os.listdir(log_dir):
        if filename.endswith('.txt'):
            data = parse_log_file(os.path.join(log_dir, filename))
            tree.insert('', 'end', iid=filename, values=(
                data['HOSTNAME'], data['CPU'], data['OS'],
                data['MAC'], data['LAST_SEEN_ONLINE'], data['LOG_TIME'], data['DATA 1']
            ))

# Виведення деталей обраного ПК
def view_details():
    selected = tree.selection()
    if not selected:
        return
    filename = selected[0]
    values = tree.item(filename)['values']
    filepath = os.path.join(log_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    detail_win = tk.Toplevel(root)
    detail_win.title(f"Деталі: {values[0]}")
    txt = tk.Text(detail_win, wrap='word')
    txt.insert('1.0', content)
    txt.pack(expand=True, fill='both')

# Основне вікно
root = tk.Tk()
root.title("AdminViewer")
root.geometry('1200x600')

cols = ('HOSTNAME', 'CPU', 'OS', 'MAC', 'LAST_SEEN_ONLINE', 'LOG_TIME', 'Примітка')
tree = ttk.Treeview(root, columns=cols, show='headings')
for col in cols:
    tree.heading(col, text=col)
    tree.column(col, width=150)
tree.pack(expand=True, fill='both')

# Кнопки
btn_frame = tk.Frame(root)
btn_frame.pack(fill='x')
tk.Button(btn_frame, text="Завантажити логи", command=load_logs).pack(side='left')
tk.Button(btn_frame, text="Переглянути деталі", command=view_details).pack(side='left')

log_dir = os.getcwd()
root.mainloop()
