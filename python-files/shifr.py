import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import string

# ------------------ Виженер ------------------
def vigenere_cipher(text, key, lang='en', decrypt=False):
    if lang == 'en':
        alphabet = string.ascii_uppercase
    elif lang == 'ru':
        alphabet = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
    elif lang == 'tk':
        alphabet = 'AÃ‚BCÇDEÉFGHIÎJKLMNOÖPRSŞTUÜWVYZ'
    else:
        raise ValueError("Unsupported language")

    text = text.upper()
    key = key.upper()
    result = ''
    key_index = 0

    for char in text:
        if char in alphabet:
            text_idx = alphabet.index(char)
            key_char = key[key_index % len(key)]
            key_idx = alphabet.index(key_char)
            if decrypt:
                res_idx = (text_idx - key_idx) % len(alphabet)
            else:
                res_idx = (text_idx + key_idx) % len(alphabet)
            result += alphabet[res_idx]
            key_index += 1
        else:
            result += char
    return result

# ------------------ GUI ------------------
class VigenereApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Виженер Шифратор")
        self.root.geometry("600x600")
        self.root.resizable(False, False)

        self.lang = tk.StringVar(value='en')

        self.create_widgets()

    def create_widgets(self):
        # Ввод текста
        ttk.Label(self.root, text="Введите текст:").pack(pady=5)
        self.input_text = tk.Text(self.root, height=6, wrap='word')
        self.input_text.pack(fill='x', padx=10)

        # Ключ
        ttk.Label(self.root, text="Ключ:").pack(pady=5)
        self.key_entry = ttk.Entry(self.root)
        self.key_entry.pack(fill='x', padx=10)

        # Выбор языка
        frame_lang = ttk.Frame(self.root)
        frame_lang.pack(pady=10)
        ttk.Label(frame_lang, text="Язык:").pack(side='left')
        lang_cb = ttk.Combobox(frame_lang, textvariable=self.lang, values=['en', 'ru', 'tk'], state='readonly', width=5)
        lang_cb.pack(side='left', padx=5)

        # Кнопки
        frame_btns = ttk.Frame(self.root)
        frame_btns.pack(pady=10)
        ttk.Button(frame_btns, text="Шифровать", command=self.encrypt).pack(side='left', padx=5)
        ttk.Button(frame_btns, text="Дешифровать", command=self.decrypt).pack(side='left', padx=5)
        ttk.Button(frame_btns, text="Копировать", command=self.copy_result).pack(side='left', padx=5)
        ttk.Button(frame_btns, text="Вставить", command=self.paste_input).pack(side='left', padx=5)

        # Импорт/Экспорт
        frame_io = ttk.Frame(self.root)
        frame_io.pack(pady=10)
        ttk.Button(frame_io, text="Импорт .txt", command=self.import_txt).pack(side='left', padx=5)
        ttk.Button(frame_io, text="Экспорт .txt", command=self.export_txt).pack(side='left', padx=5)

        # Вывод
        ttk.Label(self.root, text="Результат:").pack(pady=5)
        self.output_text = tk.Text(self.root, height=6, wrap='word')
        self.output_text.pack(fill='x', padx=10)

    # --- Основные функции ---
    def encrypt(self):
        self.process_text(decrypt=False)

    def decrypt(self):
        self.process_text(decrypt=True)

    def process_text(self, decrypt):
        text = self.input_text.get("1.0", tk.END).strip()
        key = self.key_entry.get().strip()
        lang = self.lang.get()
        if not text or not key:
            messagebox.showwarning("Ошибка", "Введите и текст, и ключ")
            return
        try:
            result = vigenere_cipher(text, key, lang=lang, decrypt=decrypt)
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
            return
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, result)

    def copy_result(self):
        text = self.output_text.get("1.0", tk.END).strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()

    def paste_input(self):
        try:
            text = self.root.clipboard_get()
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert(tk.END, text)
        except tk.TclError:
            messagebox.showerror("Ошибка", "Буфер обмена пуст или недоступен")

    def import_txt(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if path:
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.input_text.delete("1.0", tk.END)
                self.input_text.insert(tk.END, content)

    def export_txt(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if path:
            with open(path, 'w', encoding='utf-8') as file:
                content = self.output_text.get("1.0", tk.END).strip()
                file.write(content)

# ------------------ Запуск ------------------
if __name__ == '__main__':
    root = tk.Tk()
    app = VigenereApp(root)
    root.mainloop()
