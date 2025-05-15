
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime

DB_PATH = "collab_manager.db"

class CollabManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Collab Manager – By Shiladri Ghosh")
        self.root.geometry("800x600")

        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.theme = self.get_theme()

        self.setup_styles()
        self.create_login_screen()

    def get_theme(self):
        self.cursor.execute("SELECT theme FROM settings WHERE id=1")
        row = self.cursor.fetchone()
        return row[0] if row else 'light'

    def setup_styles(self):
        style = ttk.Style()
        if self.theme == 'dark':
            self.root.configure(bg="#2e2e2e")
            style.configure("TLabel", background="#2e2e2e", foreground="white")
            style.configure("TButton", background="#444", foreground="white")
        else:
            self.root.configure(bg="white")
            style.configure("TLabel", background="white", foreground="black")
            style.configure("TButton", background="#ddd", foreground="black")

    def create_login_screen(self):
        self.clear_window()
        ttk.Label(self.root, text="Enter Password to Access").pack(pady=20)
        self.password_entry = ttk.Entry(self.root, show="*")
        self.password_entry.pack()
        ttk.Button(self.root, text="Login", command=self.check_password).pack(pady=10)

    def check_password(self):
        pwd = self.password_entry.get()
        self.cursor.execute("SELECT password FROM settings WHERE id=1")
        row = self.cursor.fetchone()
        saved_pwd = row[0] if row else None

        if not saved_pwd:
            self.cursor.execute("INSERT INTO settings (id, password) VALUES (1, ?)", (pwd,))
            self.conn.commit()
            self.show_main_ui()
        elif pwd == saved_pwd:
            self.show_main_ui()
        else:
            messagebox.showerror("Access Denied", "Incorrect Password")

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_main_ui(self):
        self.clear_window()
        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(expand=1, fill="both")

        self.home_tab = ttk.Frame(self.tabs)
        self.daily_tab = ttk.Frame(self.tabs)
        self.friends_tab = ttk.Frame(self.tabs)
        self.brand_tab = ttk.Frame(self.tabs)
        self.status_tab = ttk.Frame(self.tabs)
        self.report_tab = ttk.Frame(self.tabs)
        self.settings_tab = ttk.Frame(self.tabs)

        self.tabs.add(self.home_tab, text="Home")
        self.tabs.add(self.daily_tab, text="Daily Plan")
        self.tabs.add(self.friends_tab, text="Friends Collab")
        self.tabs.add(self.brand_tab, text="Brand Collab")
        self.tabs.add(self.status_tab, text="Live Status")
        self.tabs.add(self.report_tab, text="Daily Report")
        self.tabs.add(self.settings_tab, text="Settings")

        ttk.Label(self.home_tab, text="Welcome, Shiladri Ghosh!").pack(pady=20)
        ttk.Label(self.home_tab, text="This is your influencer collab manager dashboard.").pack(pady=10)

        ttk.Label(self.settings_tab, text="Dark Mode:").pack(pady=5)
        ttk.Button(self.settings_tab, text="Switch Theme", command=self.toggle_theme).pack(pady=5)

    def toggle_theme(self):
        new_theme = 'dark' if self.theme == 'light' else 'light'
        self.cursor.execute("UPDATE settings SET theme=? WHERE id=1", (new_theme,))
        self.conn.commit()
        messagebox.showinfo("Theme Changed", f"Switched to {new_theme.title()} Mode. Restart app to apply.")
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = CollabManagerApp(root)
    root.mainloop()
