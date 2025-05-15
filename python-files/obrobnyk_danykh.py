import re
import tkinter as tk
from tkinter import ttk, messagebox
import os

SAVE_FILE = "saved_data.txt"

def format_text(text):
    parts = text.split()
    if len(parts) == 1:
        pattern = re.compile(
            r'(Mrs|Ms|Mr|Miss|Dr)\s?\(?(Female|Male)?\)?\s?'
            r'([A-Z][a-z]+)\s?([A-Z][a-z]+)\s?'
            r'(\d{1,2})\s?(\d{1,2})\s?(\d{4})\s?'
            r'(.+?)\s?([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})\s?:?\s?(\S+)'
        )
        match = pattern.match(text)
        if match:
            title, gender, first, last, day, month, year, address, email, password = match.groups()
            day = day.zfill(2)
            month = month.zfill(2)

            address_parts = address.strip().split()
            if len(address_parts) >= 2 and re.match(r"[A-Z]{1,2}\d{1,2}", address_parts[-2]) and re.match(r"\d?[A-Z]{2}", address_parts[-1]):
                postcode = address_parts[-2] + address_parts[-1]
                address_cleaned = ' '.join(address_parts[:-2] + [postcode])
            else:
                address_cleaned = address.strip()

            return f"{title} ({gender}) {first} {last} {day}/{month}/{year} {address_cleaned} {email} : {password}"
        else:
            return "❌ Не вдалося розпізнати формат."
    else:
        try:
            day, month, year = parts[4:7]
            parts[4] = f"{day.zfill(2)}/{month.zfill(2)}/{year}"
            del parts[5:7]
        except:
            return "❌ Помилка форматування дати."

        if len(parts) >= 2 and re.match(r"[A-Z]{1,2}\d{1,2}", parts[-2]) and re.match(r"\d?[A-Z]{2}", parts[-1]):
            parts[-2] = parts[-2] + parts[-1]
            del parts[-1]

        for i, part in enumerate(parts):
            if ':' in part and not part.endswith(':'):
                email, pwd = part.split(':')
                parts[i] = f"{email} : {pwd}"

        return ' '.join(parts)

def update_output(event=None):
    raw = format_input.get("1.0", "end-1c").strip()
    result = format_text(raw)
    format_output.config(state="normal")
    format_output.delete("1.0", "end")
    format_output.insert("1.0", result)
    format_output.config(state="disabled")

def save_data():
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            f.write("== Вхідний текст ==\n")
            f.write(format_input.get("1.0", "end-1c"))
            f.write("\n\n== Готовий результат ==\n")
            f.write(format_output.get("1.0", "end-1c"))
            f.write("\n\n== Блокнот ==\n")
            f.write(notepad.get("1.0", "end-1c"))
    except Exception as e:
        messagebox.showerror("Помилка", f"Не вдалося зберегти файл:\n{e}")

def load_data():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                content = f.read()
            sections = content.split("== ")
            for section in sections:
                if section.startswith("Вхідний текст =="):
                    data = section.split("\n", 1)[1]
                    format_input.delete("1.0", "end")
                    format_input.insert("1.0", data.strip())
                elif section.startswith("Готовий результат =="):
                    data = section.split("\n", 1)[1]
                    format_output.config(state="normal")
                    format_output.delete("1.0", "end")
                    format_output.insert("1.0", data.strip())
                    format_output.config(state="disabled")
                elif section.startswith("Блокнот =="):
                    data = section.split("\n", 1)[1]
                    notepad.delete("1.0", "end")
                    notepad.insert("1.0", data.strip())
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося завантажити файл:\n{e}")

def on_closing():
    save_data()
    root.destroy()

def copy_all_result():
    text = format_output.get("1.0", "end-1c")
    root.clipboard_clear()
    root.clipboard_append(text)
    messagebox.showinfo("Скопійовано", "Весь текст результату скопійовано у буфер обміну.")

# === Головне вікно ===
root = tk.Tk()
root.title("Обробник даних")
root.geometry("500x770")
root.resizable(True, True)

# Додаємо іконку (переконайся, що файл ico поруч із скриптом)
try:
    root.iconbitmap("free-icon-ico-15670465.ico")
except Exception as e:
    print(f"Іконка не завантажена: {e}")

style = ttk.Style()
style.configure("TLabel", font=("Arial", 11, "bold"))

ttk.Label(root, text="📥 Вхідний текст:").pack(pady=(10, 0))
format_input = tk.Text(root, height=6, wrap=tk.WORD, font=("Arial", 10))
format_input.pack(padx=12, pady=5, fill=tk.BOTH)
format_input.bind("<KeyRelease>", update_output)

ttk.Label(root, text="✅ Готовий результат:").pack(pady=(10, 0))

result_frame = ttk.Frame(root)
result_frame.pack(padx=12, pady=(5, 10), fill=tk.BOTH)

format_output = tk.Text(result_frame, height=4, wrap=tk.WORD, font=("Arial", 10), bg="#f0f0f0", state="disabled")
format_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

copy_button = ttk.Button(result_frame, text="📋 Скопіювати все", command=copy_all_result)
copy_button.pack(side=tk.LEFT, padx=5, pady=5)

ttk.Label(root, text="📒 Блокнот:").pack(pady=(10, 0))
notepad = tk.Text(root, height=10, wrap=tk.WORD, font=("Arial", 10))
notepad.pack(padx=12, pady=(5, 10), fill=tk.BOTH, expand=True)

save_button = ttk.Button(root, text="💾 Зберегти", command=save_data)
save_button.pack(pady=10)

load_data()

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
