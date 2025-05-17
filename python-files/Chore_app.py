import tkinter as tk
from tkinter import messagebox, ttk
import datetime
import json
import os

class ChoreApp:
    DATA_FILE = "chores.json"

    def __init__(self, root):
        self.root = root
        self.root.title("Chore Tracker")
        self.root.geometry("600x600")
        self.dark_mode = False

        # Colors
        self.light_bg = "#f5f5f5"
        self.dark_bg = "#121212"
        self.light_fg = "black"
        self.dark_fg = "white"

        self.root.configure(bg=self.light_bg)

        # Initialize chore lists before using them
        self.chore_list = []
        self.completed_chores = set()

        # Frames for layout
        entry_frame = tk.Frame(root, bg=self.light_bg)
        entry_frame.pack(pady=5)

        list_frame = tk.Frame(root, bg=self.light_bg)
        list_frame.pack(pady=5, fill=tk.BOTH, expand=True)

        button_frame = tk.Frame(root, bg=self.light_bg)
        button_frame.pack(pady=5)

        today_frame = tk.Frame(root, bg=self.light_bg)
        today_frame.pack(pady=5)

        # Chore entry
        tk.Label(entry_frame, text="Enter a chore:", font=("Arial", 12), bg=self.light_bg).grid(row=0, column=0, padx=5)
        self.chore_entry = tk.Entry(entry_frame, width=40)
        self.chore_entry.grid(row=0, column=1, padx=5)

        # Schedule listbox with scrollbar (made bigger)
        tk.Label(entry_frame, text="Schedule Chore:", font=("Arial", 12), bg=self.light_bg).grid(row=1, column=0, pady=5)

        self.schedule_options = ["Once", "Every 1 Day", "Every 2 Days", "Every 3 Days", "Every 7 Days",
                                 "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        self.schedule_listbox = tk.Listbox(entry_frame, selectmode=tk.MULTIPLE, height=10, width=50)  # Increased size
        scrollbar = tk.Scrollbar(entry_frame, command=self.schedule_listbox.yview)
        self.schedule_listbox.config(yscrollcommand=scrollbar.set)

        for option in self.schedule_options:
            self.schedule_listbox.insert(tk.END, option)

        self.schedule_listbox.grid(row=2, column=0, columnspan=2, padx=5)
        scrollbar.grid(row=2, column=2, sticky="ns")

        # Chore List
        tk.Label(list_frame, text="Chores (Schedule | Task):", font=("Arial", 12), bg=self.light_bg).pack(pady=5)
        self.chore_listbox = tk.Listbox(list_frame, width=50, height=7)
        self.chore_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        list_scrollbar = tk.Scrollbar(list_frame, command=self.chore_listbox.yview)
        self.chore_listbox.config(yscrollcommand=list_scrollbar.set)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Today's Chores Section
        tk.Label(today_frame, text="Today's Chores:", font=("Arial", 12, "bold"), bg=self.light_bg).pack(pady=5)
        self.today_listbox = tk.Listbox(today_frame, width=50, height=5)
        self.today_listbox.pack(fill=tk.BOTH, expand=True)

        self.refresh_today_button = tk.Button(today_frame, text="Refresh Today’s Chores", command=self.refresh_today_chores)
        self.refresh_today_button.pack(pady=5)

        # Buttons (arranged horizontally)
        self.add_button = tk.Button(button_frame, text="Add Chore", command=self.add_chore)
        self.delete_button = tk.Button(button_frame, text="Delete Chore", command=self.delete_chore)
        self.dark_mode_button = tk.Button(button_frame, text="Toggle Dark Mode", command=self.toggle_dark_mode)
        self.complete_button = tk.Button(button_frame, text="Complete Chore", command=self.complete_chore)

        self.add_button.grid(row=0, column=0, padx=5)
        self.delete_button.grid(row=0, column=1, padx=5)
        self.dark_mode_button.grid(row=0, column=2, padx=5)
        self.complete_button.grid(row=0, column=3, padx=5)

        # Load Data
        self.load_data()
        self.refresh_today_chores()

    def refresh_today_chores(self):
        """Refresh the list of chores scheduled for today."""
        self.today_listbox.delete(0, tk.END)
        today = datetime.datetime.today().strftime("%A")

        for schedule, chore in self.chore_list:
            if today in schedule or "Every 1 Day" in schedule or "Once" in schedule:
                if chore not in self.completed_chores:
                    self.today_listbox.insert(tk.END, chore)

        if self.today_listbox.size() == 0:
            self.today_listbox.insert(tk.END, "(No chores scheduled for today)")

        self.root.after(30000, self.refresh_today_chores)  # Auto-refresh every 30 seconds

    def add_chore(self):
        chore = self.chore_entry.get()
        selected_options = [self.schedule_listbox.get(i) for i in self.schedule_listbox.curselection()]

        if "Once" in selected_options and len(selected_options) > 1:
            messagebox.showwarning("Warning", "The 'Once' option cannot be combined with others.")
            return

        if chore and selected_options:
            schedule_combined = ", ".join(selected_options)
            formatted_entry = f"{schedule_combined} | {chore}"

            self.chore_list.append((schedule_combined, chore))
            self.chore_listbox.insert(tk.END, formatted_entry)

            self.save_data()
            self.chore_entry.delete(0, tk.END)
            self.refresh_today_chores()

    def delete_chore(self):
        selected_index = self.chore_listbox.curselection()
        if selected_index:
            confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this chore?")
            if confirm:
                del self.chore_list[selected_index[0]]
                self.chore_listbox.delete(selected_index[0])
                self.save_data()
                self.refresh_today_chores()
        else:
            messagebox.showwarning("Warning", "Please select a chore to delete.")

    def complete_chore(self):
        selected_index = self.today_listbox.curselection()
        if selected_index:
            selected_chore = self.today_listbox.get(selected_index[0])
            self.completed_chores.add(selected_chore)
            self.today_listbox.delete(selected_index[0])
            self.save_data()
        else:
            messagebox.showwarning("Warning", "Select a chore to mark as complete.")

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        bg_color = self.dark_bg if self.dark_mode else self.light_bg
        fg_color = self.dark_fg if self.dark_mode else self.light_fg

        self.root.configure(bg=bg_color)
        for widget in self.root.winfo_children():
            if isinstance(widget, (tk.Frame, tk.Label, tk.Button, tk.Listbox)):
                widget.configure(bg=bg_color, fg=fg_color)
            elif isinstance(widget, tk.Entry):
                widget.configure(bg=bg_color, fg=fg_color, insertbackground=fg_color)

        messagebox.showinfo("Dark Mode", "Dark mode activated!" if self.dark_mode else "Light mode activated!")

    def save_data(self):
        data = {"general_chores": self.chore_list, "completed_chores": list(self.completed_chores)}
        with open(self.DATA_FILE, "w") as file:
            json.dump(data, file, indent=4)

    def load_data(self):
        if os.path.exists(self.DATA_FILE):
            with open(self.DATA_FILE, "r") as file:
                data = json.load(file)
                self.chore_list = data.get("general_chores", [])
                self.completed_chores = set(data.get("completed_chores", []))

            self.refresh_today_chores()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChoreApp(root)
    root.mainloop()