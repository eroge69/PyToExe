from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
import json
import os
from tkinter import PhotoImage
class Note:
    def __init__(self, content, due_date=None, completed=False, created_at=None):
        self.content = content
        self.due_date = due_date
        self.completed = completed
        self.created_at = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S") if created_at else datetime.now()

    def mark_as_completed(self):
        self.completed = True

    def to_dict(self):
        return {
            "content": self.content,
            "due_date": self.due_date,
            "completed": self.completed,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

    def __str__(self):
        status = "✔" if self.completed else "⏳"
        created = self.created_at.strftime("%Y-%m-%d %H:%M")
        due = f" | До: {self.due_date}" if self.due_date else ""
        return f"{status} {self.content} ({created}{due})"

class NoteManager:
    def __init__(self, filepath="notes.json"):
        self.notes = []
        self.filepath = filepath
        self.load_notes()

    def add_note(self, content, due_date=None):
        note = Note(content, due_date)
        self.notes.append(note)

    def mark_note_as_completed(self, index):
        if 0 <= index < len(self.notes):
            self.notes[index].mark_as_completed()

    def delete_note(self, index):
        if 0 <= index < len(self.notes):
            del self.notes[index]

    def show_notes(self):
        return [str(note) for note in self.notes]

    def save_notes(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump([note.to_dict() for note in self.notes], f, ensure_ascii=False, indent=4)

    def load_notes(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.notes = [Note(**note) for note in data]

class NoteApp:
    def __init__(self, root):
        self.note_manager = NoteManager()
        self.root = root
        self.root.title("🌙 Заметки")
        self.root.geometry("850x520")
        self.root.configure(bg="#1e1e2f")
        self.icon = PhotoImage(file="C:/Users/student/PycharmProjects/Курбатов/.venv/Вложенные списки/note_icon.ico.png")  # Замените "icon.png" на путь к вашему файлу иконки
        self.root.iconphoto(True, self.icon)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.font = ("Segoe UI", 11)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton",
                        font=self.font,
                        padding=10,
                        background="#2d2d44",
                        foreground="#f0f0f0",
                        relief="flat")
        style.map("TButton",
                  background=[("active", "#3b82f6")],
                  foreground=[("active", "white")])
        style.configure("TLabel", font=self.font, background="#1e1e2f", foreground="#f0f0f0")
        style.configure("TFrame", background="#1e1e2f")

        ttk.Label(root, text="📋 Ваши Заметки", font=("Segoe UI", 16, "bold")).pack(pady=(20, 10))

        self.listbox = tk.Listbox(root, width=100, height=15,
                                  font=("Segoe UI", 10),
                                  bg="#2d2d44", fg="#f0f0f0",
                                  selectbackground="#38b2ac",
                                  selectforeground="black",
                                  bd=0, highlightthickness=1,
                                  highlightbackground="#3b3b5f", relief="flat")
        self.listbox.pack(padx=20, pady=10)

        button_frame = ttk.Frame(root)
        button_frame.pack(pady=10)

        self.add_button = ttk.Button(button_frame, text="➕ Добавить", command=self.open_note_input_window)
        self.add_button.grid(row=0, column=0, padx=10)

        self.complete_button = ttk.Button(button_frame, text="✅ Завершить", command=self.complete_note)
        self.complete_button.grid(row=0, column=1, padx=10)

        self.delete_button = ttk.Button(button_frame, text="🗑️ Удалить", command=self.delete_note)
        self.delete_button.grid(row=0, column=2, padx=10)

        self.display_notes()

    def open_note_input_window(self):
        input_window = tk.Toplevel(self.root)
        input_window.title("📝 Новая Заметка")
        input_window.geometry("400x300")
        input_window.configure(bg="#1e1e2f")

        ttk.Label(input_window, text="Текст заметки:").pack(pady=10)
        text_entry = tk.Text(input_window, height=5, width=40,
                             font=self.font, bg="#2d2d44", fg="#f0f0f0",
                             insertbackground="#f0f0f0", relief="flat")
        text_entry.pack(pady=5)

        ttk.Label(input_window, text="Дата (опционально):").pack(pady=5)
        date_entry = DateEntry(input_window, width=20, background='#38b2ac',
                               foreground='white', borderwidth=0,
                               date_pattern='yyyy-mm-dd')
        date_entry.pack(pady=5)

        def submit_note():
            content = text_entry.get("1.0", tk.END).strip()
            due_date = date_entry.get()
            if content:
                self.note_manager.add_note(content, due_date)
                self.display_notes()
                input_window.destroy()

        ttk.Button(input_window, text="💾 Сохранить", command=submit_note).pack(pady=15)

    def complete_note(self):
        try:
            index = self.listbox.curselection()[0]
            self.note_manager.mark_note_as_completed(index)
            self.display_notes()
        except IndexError:
            messagebox.showwarning("Ошибка", "Выберите заметку для завершения.")

    def delete_note(self):
        try:
            index = self.listbox.curselection()[0]
            self.note_manager.delete_note(index)
            self.display_notes()
        except IndexError:
            messagebox.showwarning("Ошибка", "Выберите заметку для удаления.")

    def display_notes(self):
        self.listbox.delete(0, tk.END)
        notes = self.note_manager.show_notes()
        for note in notes:
            self.listbox.insert(tk.END, note)

    def on_closing(self):
        self.note_manager.save_notes()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = NoteApp(root)
    root.mainloop()
