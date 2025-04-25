
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime, timedelta
import threading
import time
import subprocess
import json
import os

DATA_FILE = "geplante_tasks.json"

scheduled_tasks = []

def browse_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        entry_path.delete(0, tk.END)
        entry_path.insert(0, file_path)

def add_task():
    path = entry_path.get()
    dt_string = entry_datetime.get()
    repeat_daily = var_repeat.get()

    try:
        target_time = datetime.strptime(dt_string, "%Y-%m-%d %H:%M")
    except ValueError:
        messagebox.showerror("Fehler", "Bitte gib das Datum im Format JJJJ-MM-TT HH:MM ein.")
        return

    if not path:
        messagebox.showerror("Fehler", "Bitte wähle eine Datei aus.")
        return

    scheduled_tasks.append({
        "time": target_time.strftime("%Y-%m-%d %H:%M"),
        "path": path,
        "repeat": repeat_daily
    })
    save_tasks()
    update_task_list()

def update_task_list():
    for row in task_table.get_children():
        task_table.delete(row)
    for i, task in enumerate(scheduled_tasks):
        task_table.insert("", "end", iid=str(i), values=(task["time"], task["path"], "Ja" if task["repeat"] else "Nein"))

def delete_task():
    selected = task_table.selection()
    for item in selected:
        index = int(item)
        if 0 <= index < len(scheduled_tasks):
            del scheduled_tasks[index]
    save_tasks()
    update_task_list()

def start_scheduler():
    def task_runner():
        already_run = set()
        while True:
            now = datetime.now()
            for i, task in enumerate(scheduled_tasks):
                run_time = datetime.strptime(task["time"], "%Y-%m-%d %H:%M")
                if i in already_run and not task["repeat"]:
                    continue
                if now >= run_time:
                    try:
                        subprocess.Popen([task["path"]])
                        if task["repeat"]:
                            next_day = run_time + timedelta(days=1)
                            task["time"] = next_day.strftime("%Y-%m-%d %H:%M")
                            save_tasks()
                        else:
                            already_run.add(i)
                    except Exception as e:
                        print(f"Fehler beim Starten von {task['path']}: {e}")
            update_task_list()
            time.sleep(30)

    threading.Thread(target=task_runner, daemon=True).start()
    messagebox.showinfo("Läuft", "Die geplanten Programme werden nun gestartet, sobald ihre Zeit kommt.")

def save_tasks():
    with open(DATA_FILE, "w") as f:
        json.dump(scheduled_tasks, f, indent=2)

def load_tasks():
    global scheduled_tasks
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            scheduled_tasks = json.load(f)
        update_task_list()

# GUI
root = tk.Tk()
root.title("Mehrfach-Zeitstarter mit Wiederholung")

tk.Label(root, text="Pfad zur Datei:").grid(row=0, column=0, sticky="e")
entry_path = tk.Entry(root, width=40)
entry_path.grid(row=0, column=1)
tk.Button(root, text="Durchsuchen", command=browse_file).grid(row=0, column=2)

tk.Label(root, text="Datum & Uhrzeit (JJJJ-MM-TT HH:MM):").grid(row=1, column=0, columnspan=2, sticky="e")
entry_datetime = tk.Entry(root, width=20)
entry_datetime.grid(row=1, column=2)

var_repeat = tk.BooleanVar()
chk_repeat = tk.Checkbutton(root, text="Täglich wiederholen", variable=var_repeat)
chk_repeat.grid(row=2, column=1)

tk.Button(root, text="Hinzufügen", command=add_task).grid(row=3, column=1, pady=10)

task_table = ttk.Treeview(root, columns=("Zeit", "Programm", "Täglich"), show="headings")
task_table.heading("Zeit", text="Geplante Zeit")
task_table.heading("Programm", text="Programm")
task_table.heading("Täglich", text="Täglich?")
task_table.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

tk.Button(root, text="Ausgewählte löschen", command=delete_task).grid(row=5, column=0)
tk.Button(root, text="Starten", command=start_scheduler).grid(row=5, column=2)

# Lade Aufgaben beim Start
load_tasks()

root.mainloop()
