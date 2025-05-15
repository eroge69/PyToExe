
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime, timedelta

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Moja Offline Baza Podataka")
        self.root.geometry("600x400")
        self.data = load_data()

        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 12), padding=6)
        self.style.configure("TLabel", font=("Arial", 11), background="#e0f7fa")
        self.style.configure("TEntry", padding=6)

        self.build_ui()
        self.refresh_list()

    def build_ui(self):
        frame = ttk.Frame(self.root)
        frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(frame, text="Naziv artikla:").pack(anchor="w")
        self.entry_name = ttk.Entry(frame)
        self.entry_name.pack(fill="x")

        ttk.Label(frame, text="Opis / detalji:").pack(anchor="w")
        self.entry_desc = ttk.Entry(frame)
        self.entry_desc.pack(fill="x")

        ttk.Label(frame, text="Datum isteka (YYYY-MM-DD):").pack(anchor="w")
        self.entry_date = ttk.Entry(frame)
        self.entry_date.pack(fill="x")

        ttk.Button(frame, text="Dodaj zapis", command=self.add_record).pack(pady=5)

        self.tree = ttk.Treeview(self.root, columns=("name", "desc", "date"), show="headings")
        self.tree.heading("name", text="Naziv")
        self.tree.heading("desc", text="Opis")
        self.tree.heading("date", text="Ističe")
        self.tree.pack(expand=True, fill="both", padx=10)

        ttk.Button(self.root, text="Provjeri isteke", command=self.check_reminders).pack(pady=5)

    def add_record(self):
        name = self.entry_name.get()
        desc = self.entry_desc.get()
        date_str = self.entry_date.get()

        if not name or not date_str:
            messagebox.showwarning("Greška", "Naziv i datum su obavezni.")
            return

        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Format greška", "Unesi datum u formatu YYYY-MM-DD.")
            return

        self.data.append({"name": name, "desc": desc, "date": date_str})
        save_data(self.data)
        self.refresh_list()

    def refresh_list(self):
        self.tree.delete(*self.tree.get_children())
        for item in self.data:
            self.tree.insert("", "end", values=(item["name"], item["desc"], item["date"]))

    def check_reminders(self):
        today = datetime.today().date()
        expired = [item for item in self.data if datetime.strptime(item["date"], "%Y-%m-%d").date() < today]
        if expired:
            msg = "\n".join([f"{item['name']} (istekao {item['date']})" for item in expired])
            messagebox.showinfo("Obavijest", f"Sljedeći zapisi su istekli:\n{msg}")
        else:
            messagebox.showinfo("Super!", "Nema isteklih zapisa.")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
