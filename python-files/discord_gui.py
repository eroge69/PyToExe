
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

def run_command():
    exe = os.path.join(os.getcwd(), "winws.exe")
    hosts = os.path.join(os.getcwd(), "list-discord.txt")
    ips = os.path.join(os.getcwd(), "ipset-discord.txt")

    if not os.path.exists(exe) or not os.path.exists(hosts) or not os.path.exists(ips):
        messagebox.showerror("Ошибка", "Файлы winws.exe, list-discord.txt или ipset-discord.txt не найдены.")
        return

    command = [
        exe,
        "--wf-tcp=443", "--wf-udp=443,50000-50100",
        f"--hostlist={hosts}",
        f"--ipset={ips}",
        "--dpi-desync=fake",
        "--dpi-desync-repeats=6",
        "--dpi-desync-any-protocol",
        "--new"
    ]

    try:
        subprocess.Popen(command)
        messagebox.showinfo("Успех", "Процесс winws.exe запущен.")
    except Exception as e:
        messagebox.showerror("Ошибка запуска", str(e))

app = tk.Tk()
app.title("Запрет Discord GUI")
app.geometry("400x150")

tk.Label(app, text="Нажмите кнопку ниже для запуска фильтрации Discord").pack(pady=10)
tk.Button(app, text="Запустить winws", command=run_command, height=2, width=25).pack()
app.mainloop()
