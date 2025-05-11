import tkinter as tk
from tkinter import messagebox, ttk
import json
from datetime import datetime, timedelta
import threading
import os
import ctypes
import sys

DATA_FILE = "badges.json"

def load_badges():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_badges(badges):
    with open(DATA_FILE, "w") as f:
        json.dump(badges, f, indent=4)

def days_until(date_str):
    date = datetime.strptime(date_str, "%Y-%m-%d").date()
    return (date - datetime.today().date()).days

def check_expiring_badges():
    badges = load_badges()
    expiring = [b for b in badges if 0 <= days_until(b['expiry']) <= 15]
    if expiring:
        message = "\n".join([f"{b['name']} expires in {days_until(b['expiry'])]} days" for b in expiring])
        show_notification("Badge Expiry Reminder", message)

def show_notification(title, message):
    ctypes.windll.user32.MessageBoxW(0, message, title, 0x40 | 0x1)

class BadgeReminderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Badge Reminder")
        self.root.geometry("500x400")
        self.badges = load_badges()
        
        self.tree = ttk.Treeview(root, columns=("ID", "Name", "Expiry"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Expiry", text="Expiry Date")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.frame = tk.Frame(root)
        self.frame.pack(pady=10)

        self.id_entry = tk.Entry(self.frame)
        self.id_entry.grid(row=0, column=0)
        self.name_entry = tk.Entry(self.frame)
        self.name_entry.grid(row=0, column=1)
        self.date_entry = tk.Entry(self.frame)
        self.date_entry.grid(row=0, column=2)
        
        tk.Button(self.frame, text="Add", command=self.add_badge).grid(row=1, column=0)
        tk.Button(self.frame, text="Edit", command=self.edit_badge).grid(row=1, column=1)
        tk.Button(self.frame, text="Delete", command=self.delete_badge).grid(row=1, column=2)

        self.refresh_tree()

        # Background check in a thread
        threading.Thread(target=check_expiring_badges, daemon=True).start()

    def refresh_tree(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for b in self.badges:
            self.tree.insert("", tk.END, values=(b["id"], b["name"], b["expiry"]))

    def add_badge(self):
        new_badge = {
            "id": self.id_entry.get(),
            "name": self.name_entry.get(),
            "expiry": self.date_entry.get()
        }
        self.badges.append(new_badge)
        save_badges(self.badges)
        self.refresh_tree()

    def edit_badge(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        self.badges[index] = {
            "id": self.id_entry.get(),
            "name": self.name_entry.get(),
            "expiry": self.date_entry.get()
        }
        save_badges(self.badges)
        self.refresh_tree()

    def delete_badge(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        del self.badges[index]
        save_badges(self.badges)
        self.refresh_tree()

if __name__ == "__main__":
    root = tk.Tk()
    app = BadgeReminderApp(root)
    root.mainloop()
