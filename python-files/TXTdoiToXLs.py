import requests
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import re
from tkinter import font

def classify_publication_type(title: str, pub_type: str) -> str:
    title = title.lower()
    if pub_type in ['journal-article', 'proceedings-article']:
        if 'review' in title or 'обзор' in title:
            return 'Обзор'
        return 'Оригинальное исследование'
    elif 'editorial' in pub_type:
        return 'Заметка редактора'
    elif 'book-chapter' in pub_type:
        return 'Глава книги'
    return 'Другое'

def clean_abstract(text: str) -> str:
    return re.sub('<[^<]+?>', '', text).strip()

def fetch_metadata(doi):
    url = f"https://api.crossref.org/works/{doi}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise error for bad responses
        data = response.json().get('message', {})
        title = data.get('title', ['Не найдено'])[0]
        abstract = clean_abstract(data.get('abstract', ''))
        pub_type = data.get('type', '')
        category = classify_publication_type(title, pub_type)
        return {
            'DOI': doi,
            'Название': title,
            'Аннотация': abstract,
            'Тип публикации': pub_type,
            'Категория': category
        }
    except Exception as e:
        return {
            'DOI': doi,
            'Название': 'Не найдено',
            'Аннотация': '',
            'Тип публикации': '',
            'Категория': f'Ошибка: {e}'
        }

class DOIFetcherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Загрузка метаданных по DOI")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        self.root.config(bg="#f0f0f0")

        # Set a custom font for the app
        self.font = font.nametofont("TkDefaultFont")
        self.font.actual()

        self.frame = tk.Frame(root, padx=15, pady=15, bg="#f0f0f0")
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Title label with larger font
        self.label = tk.Label(self.frame, text="Выберите TXT-файл с DOI (по одному на строку):", font=("Arial", 14, "bold"), bg="#f0f0f0")
        self.label.pack()

        self.btn_select_file = tk.Button(self.frame, text="Выбрать файл", command=self.select_file, font=("Arial", 12), relief="raised", bg="#4CAF50", fg="white", activebackground="#45a049", activeforeground="white", padx=20, pady=10)
        self.btn_select_file.pack(pady=10)

        self.progress = ttk.Progressbar(self.frame, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=15)

        self.log = tk.Text(self.frame, height=12, wrap=tk.WORD, state='disabled', font=("Courier New", 10), bg="#f4f4f4", fg="#333333", padx=10, pady=10, relief="sunken")
        self.log.pack(pady=5, fill=tk.BOTH, expand=True)

        self.selected_file = ""
        self.save_path = ""

    def log_message(self, message):
        self.log.config(state='normal')
        self.log.insert(tk.END, message + "\n")
        self.log.see(tk.END)
        self.log.config(state='disabled')
        self.root.update()

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Выберите TXT-файл с DOI",
            filetypes=[("Text files", "*.txt")]
        )
        if not file_path:
            return

        self.selected_file = file_path
        self.save_path = filedialog.asksaveasfilename(
            title="Сохранить как Excel-файл",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        if not self.save_path:
            return

        self.log_message(f"Файл с DOI: {self.selected_file}")
        self.log_message(f"Файл для сохранения: {self.save_path}")
        self.start_processing()

    def start_processing(self):
        self.process_file()

    def process_file(self):
        with open(self.selected_file, 'r', encoding='utf-8') as f:
            dois = [line.strip() for line in f if line.strip()]

        if not dois:
            messagebox.showwarning("Пусто", "Файл не содержит DOI.")
            return

        self.progress["maximum"] = len(dois)
        self.progress["value"] = 0

        results = []

        for i, doi in enumerate(dois):
            metadata = fetch_metadata(doi)
            results.append(metadata)
            self.update_ui(i, doi)

        if results:
            df = pd.DataFrame(results)
            df.to_excel(self.save_path, index=False)
            self.log_message("✅ Готово! Файл успешно сохранён.")
            messagebox.showinfo("Готово", f"Файл успешно сохранён:\n{self.save_path}")
        else:
            messagebox.showwarning("Ошибка", "Нет данных для сохранения.")

    def update_ui(self, index, doi):
        self.log_message(f"[{index + 1}] ✅ DOI: {doi}")
        self.progress["value"] += 1

if __name__ == "__main__":
    root = tk.Tk()
    app = DOIFetcherApp(root)
    root.mainloop()
