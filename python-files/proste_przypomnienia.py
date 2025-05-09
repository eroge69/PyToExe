
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
import json
import os

reminders = []

def save_reminders():
    with open("reminders.json", "w") as f:
        json.dump(reminders, f)

def add_reminder():
    title = title_entry.get()
    date = date_entry.get()
    time = time_entry.get()
    repeat = repeat_combobox.get()

    if not title or not date or not time:
        messagebox.showerror("Błąd", "Wszystkie pola muszą być wypełnione.")
        return

    reminder = {
        "title": title,
        "date": date,
        "time": time,
        "repeat": repeat
    }
    reminders.append(reminder)
    save_reminders()
    update_reminder_list()
    clear_inputs()

def clear_inputs():
    title_entry.delete(0, tk.END)
    date_entry.delete(0, tk.END)
    time_entry.delete(0, tk.END)
    repeat_combobox.set("Brak")

def update_reminder_list():
    reminder_listbox.delete(0, tk.END)
    for r in reminders:
        reminder_listbox.insert(tk.END, f"{r['title']} - {r['date']} {r['time']} ({r['repeat']})")

root = tk.Tk()
root.title("Proste Przypomnienia")
root.geometry("400x400")

tk.Label(root, text="Tytuł przypomnienia").pack()
title_entry = tk.Entry(root, width=40)
title_entry.pack()

tk.Label(root, text="Data (RRRR-MM-DD)").pack()
date_entry = tk.Entry(root, width=40)
date_entry.pack()

tk.Label(root, text="Godzina (GG:MM)").pack()
time_entry = tk.Entry(root, width=40)
time_entry.pack()

tk.Label(root, text="Powtarzaj").pack()
repeat_combobox = ttk.Combobox(root, values=["Brak", "Codziennie", "Co poniedziałek", "Co wtorek", "Co środa", "Co czwartek", "Co piątek", "Co sobotę", "Co niedzielę"])
repeat_combobox.set("Brak")
repeat_combobox.pack()

tk.Button(root, text="Dodaj przypomnienie", command=add_reminder).pack(pady=10)

reminder_listbox = tk.Listbox(root, width=50)
reminder_listbox.pack(pady=10)

if os.path.exists("reminders.json"):
    with open("reminders.json", "r") as f:
        reminders = json.load(f)
        update_reminder_list()

root.mainloop()
