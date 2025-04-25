import tkinter as tk
from tkinter import simpledialog, messagebox, ttk, filedialog
import sqlite3
import hashlib
import os
from cryptography.fernet import Fernet
import pyperclip
import json
import time
import threading
import string
import secrets

# === SETUP ===
DB_FILE = 'vault.db'
KEY_FILE = 'key.key'
INACTIVITY_TIMEOUT = 300  # 5 minutes

# === ENCRYPTION ===
def load_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as f:
            f.write(key)
    else:
        with open(KEY_FILE, 'rb') as f:
            key = f.read()
    return Fernet(key)

def hash_master_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# === DATABASE SETUP ===
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS master (hash TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS vault (site TEXT, username TEXT, password TEXT)''')
    conn.commit()
    conn.close()

# === GUI ===
class PasswordManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Manager")
        self.fernet = load_key()
        self.last_activity = time.time()
        self.activity_thread = threading.Thread(target=self.check_inactivity)
        self.activity_thread.daemon = True
        self.activity_thread.start()
        self.root.bind_all('<Any-KeyPress>', self.update_activity)
        self.root.bind_all('<Any-Button>', self.update_activity)

        self.init_login()

    def update_activity(self, event=None):
        self.last_activity = time.time()

    def check_inactivity(self):
        while True:
            if time.time() - self.last_activity > INACTIVITY_TIMEOUT:
                messagebox.showinfo("Locked", "Session locked due to inactivity.")
                self.root.quit()
            time.sleep(10)

    def init_login(self):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT * FROM master")
        result = c.fetchone()
        conn.close()

        if result is None:
            self.set_master_password()
        else:
            self.ask_master_password(result[0])

    def set_master_password(self):
        pwd = simpledialog.askstring("Set Master Password", "Enter a new master password:", show='*')
        if pwd:
            hashed = hash_master_password(pwd)
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("INSERT INTO master VALUES (?)", (hashed,))
            conn.commit()
            conn.close()
            self.show_main_window()

    def ask_master_password(self, correct_hash):
        pwd = simpledialog.askstring("Master Password", "Enter your master password:", show='*')
        if hash_master_password(pwd) == correct_hash:
            self.show_main_window()
        else:
            messagebox.showerror("Error", "Incorrect master password")
            self.root.destroy()

    def show_main_window(self):
        self.frame = tk.Frame(self.root)
        self.frame.pack(padx=10, pady=10)

        tk.Label(self.frame, text="Site:").grid(row=0, column=0)
        tk.Label(self.frame, text="Username:").grid(row=1, column=0)
        tk.Label(self.frame, text="Password:").grid(row=2, column=0)

        self.site_entry = tk.Entry(self.frame)
        self.username_entry = tk.Entry(self.frame)
        self.password_entry = tk.Entry(self.frame)

        self.site_entry.grid(row=0, column=1)
        self.username_entry.grid(row=1, column=1)
        self.password_entry.grid(row=2, column=1)

        tk.Button(self.frame, text="Generate", command=self.generate_password).grid(row=2, column=2)
        tk.Button(self.frame, text="Save", command=self.save_password).grid(row=3, column=0)
        tk.Button(self.frame, text="Export", command=self.export_vault).grid(row=3, column=1)
        tk.Button(self.frame, text="Import", command=self.import_vault).grid(row=3, column=2)

        self.search_entry = tk.Entry(self.frame)
        self.search_entry.grid(row=4, column=0, columnspan=2)
        self.search_entry.bind("<KeyRelease>", self.search_passwords)
        tk.Label(self.frame, text="Search").grid(row=4, column=2)

        self.tree = ttk.Treeview(self.frame, columns=("Site", "Username", "Password"), show='headings')
        self.tree.heading("Site", text="Site")
        self.tree.heading("Username", text="Username")
        self.tree.heading("Password", text="Password")
        self.tree.grid(row=5, column=0, columnspan=3, pady=10)

        self.tree.bind("<Double-1>", self.copy_selected_password)

        self.load_passwords()

    def save_password(self):
        site = self.site_entry.get()
        username = self.username_entry.get()
        password = self.fernet.encrypt(self.password_entry.get().encode()).decode()

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO vault VALUES (?, ?, ?)", (site, username, password))
        conn.commit()
        conn.close()
        messagebox.showinfo("Saved", "Password saved!")
        self.load_passwords()

    def load_passwords(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT * FROM vault")
        self.all_data = c.fetchall()
        for site, username, encrypted in self.all_data:
            decrypted = self.fernet.decrypt(encrypted.encode()).decode()
            self.tree.insert('', 'end', values=(site, username, decrypted))
        conn.close()

    def search_passwords(self, event):
        query = self.search_entry.get().lower()
        for row in self.tree.get_children():
            self.tree.delete(row)
        for site, username, encrypted in self.all_data:
            decrypted = self.fernet.decrypt(encrypted.encode()).decode()
            if query in site.lower() or query in username.lower():
                self.tree.insert('', 'end', values=(site, username, decrypted))

    def copy_selected_password(self, event):
        selected = self.tree.selection()
        if selected:
            password = self.tree.item(selected[0])['values'][2]
            pyperclip.copy(password)
            messagebox.showinfo("Copied", "Password copied to clipboard!")

    def generate_password(self):
        chars = string.ascii_letters + string.digits + string.punctuation
        generated = ''.join(secrets.choice(chars) for _ in range(16))
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, generated)

    def export_vault(self):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT * FROM vault")
        data = [(site, username, self.fernet.encrypt(self.fernet.decrypt(pw.encode())).decode()) for site, username, pw in c.fetchall()]
        conn.close()

        file = filedialog.asksaveasfilename(defaultextension=".json")
        if file:
            with open(file, 'w') as f:
                json.dump(data, f)
            messagebox.showinfo("Exported", "Vault exported successfully.")

    def import_vault(self):
        file = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file:
            with open(file, 'r') as f:
                data = json.load(f)
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.executemany("INSERT INTO vault VALUES (?, ?, ?)", data)
            conn.commit()
            conn.close()
            messagebox.showinfo("Imported", "Vault imported successfully.")
            self.load_passwords()

if __name__ == '__main__':
    init_db()
    root = tk.Tk()
    app = PasswordManager(root)
    root.mainloop()
