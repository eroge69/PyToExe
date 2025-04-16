# ApnaGhar.pk CRM v1.0
# Main File: main.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
import datetime
import openpyxl
import threading
import time

DB_FILE = 'apnaghar_crm.db'

# ------------------ DB Setup ------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, phone TEXT, whatsapp TEXT, city TEXT, area TEXT,
        inquiry_type TEXT, budget TEXT, urgency TEXT,
        source TEXT, status TEXT, notes TEXT,
        assigned_to TEXT, follow_up TEXT, requirements TEXT, created_at TEXT
    )''')
    conn.commit()
    conn.close()

# ------------------ Splash Screen ------------------
def show_splash_screen(root, on_continue):
    splash = tk.Toplevel(root)
    splash.geometry("800x600")
    splash.overrideredirect(True)
    splash.configure(bg='black')

    label = tk.Label(splash, text="Welcome to ApnaGhar.pk", font=("Helvetica", 32, "bold"), fg="white", bg="black")
    label.pack(expand=True)

    def animate_text():
        for i in range(3):
            label.config(fg="gray")
            splash.update()
            time.sleep(0.3)
            label.config(fg="white")
            splash.update()
            time.sleep(0.3)

    threading.Thread(target=animate_text).start()
    root.after(3000, lambda: (splash.destroy(), on_continue()))

# ------------------ Login Screen ------------------
def show_login_screen(root, on_success):
    def login():
        if user_entry.get() == "Apnaghar.pk1" and pass_entry.get() == "Apnapindi1122":
            login_frame.destroy()
            on_success()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials")

    login_frame = tk.Frame(root, bg="black")
    login_frame.pack(expand=True)

    tk.Label(login_frame, text="Login to ApnaGhar.pk CRM", font=("Arial", 20, "bold"), fg="white", bg="black").pack(pady=20)
    tk.Label(login_frame, text="Username", fg="white", bg="black", font=("Arial", 12)).pack()
    user_entry = tk.Entry(login_frame, font=("Arial", 12))
    user_entry.pack(pady=5)
    tk.Label(login_frame, text="Password", fg="white", bg="black", font=("Arial", 12)).pack()
    pass_entry = tk.Entry(login_frame, show='*', font=("Arial", 12))
    pass_entry.pack(pady=5)
    tk.Button(login_frame, text="Login", font=("Arial", 12), command=login, bg="gray20", fg="white").pack(pady=20)

# ------------------ Main App ------------------
def show_dashboard(root):
    root.title("ApnaGhar.pk – Real Estate CRM")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview",
                    background="black",
                    foreground="white",
                    rowheight=30,
                    fieldbackground="black",
                    font=("Arial", 11))
    style.configure("Treeview.Heading", background="gray20", foreground="white", font=("Arial", 12, "bold"))

    frame = tk.Frame(root, bg="black")
    frame.pack(fill='both', expand=True)

    tree = ttk.Treeview(frame, columns=("Name", "Phone", "City", "Status", "Assigned"), show='headings')
    for col in tree["columns"]:
        tree.heading(col, text=col)
    tree.pack(fill='both', expand=True, padx=10, pady=10)

    def load_clients():
        for i in tree.get_children():
            tree.delete(i)
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT name, phone, city, status, assigned_to FROM clients")
        for row in c.fetchall():
            tree.insert('', 'end', values=row)
        conn.close()

    def add_client():
        top = tk.Toplevel(root)
        top.title("Add Client")
        top.configure(bg="black")

        fields = ["Name", "Phone", "WhatsApp", "City", "Area", "Inquiry Type",
                  "Budget", "Urgency", "Source", "Status", "Notes", "Assigned To", "Follow Up Date", "Requirements"]
        entries = {}
        for field in fields:
            tk.Label(top, text=field, fg="white", bg="black", font=("Arial", 10)).pack()
            entry = tk.Entry(top, font=("Arial", 10))
            entry.pack(padx=5, pady=2)
            entries[field] = entry

        def save():
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("""
                INSERT INTO clients (name, phone, whatsapp, city, area, inquiry_type,
                budget, urgency, source, status, notes, assigned_to, follow_up, requirements, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tuple(entries[field].get() for field in fields) + (datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),))
            conn.commit()
            conn.close()
            top.destroy()
            load_clients()

        tk.Button(top, text="Save", command=save, font=("Arial", 10), bg="gray20", fg="white").pack(pady=10)

    def check_reminders():
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        today = datetime.date.today().strftime('%Y-%m-%d')
        c.execute("SELECT name, phone, follow_up FROM clients WHERE follow_up = ?", (today,))
        reminders = c.fetchall()
        conn.close()
        if reminders:
            reminder_text = "\n".join([f"{name} ({phone}) - Follow Up Today" for name, phone, date in reminders])
            messagebox.showinfo("Today's Reminders", reminder_text)

    btn_frame = tk.Frame(frame, bg="black")
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Add Client", command=add_client, font=("Arial", 10), bg="gray20", fg="white").grid(row=0, column=0, padx=5)
    tk.Button(btn_frame, text="Refresh", command=load_clients, font=("Arial", 10), bg="gray20", fg="white").grid(row=0, column=1, padx=5)
    tk.Button(btn_frame, text="Reminders", command=check_reminders, font=("Arial", 10), bg="gray20", fg="white").grid(row=0, column=2, padx=5)

    load_clients()
    check_reminders()

# ------------------ Run App ------------------
if __name__ == '__main__':
    init_db()
    root = tk.Tk()
    root.geometry("900x650")
    root.configure(bg='black')
    root.title("ApnaGhar.pk CRM")

    # Splash, then login, then dashboard
    show_splash_screen(root, lambda: show_login_screen(root, lambda: show_dashboard(root)))

    root.mainloop()
