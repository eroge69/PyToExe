import tkinter as tk
from tkinter import filedialog, messagebox

class TextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Текстовый редактор - Bogy")
        self.root.geometry("600x400")

        self.text_area = tk.Text(self.root, wrap='word')
        self.text_area.pack(expand=1, fill='both')

        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        self.file_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="Файл", menu=self.file_menu)
        
        self.file_menu.add_command(label="Открыть", command=self.open_file)
        self.file_menu.add_command(label="Сохранить как...", command=self.save_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Выход", command=self.root.quit)

        # Добавление надписи внизу окна
        self.footer_label = tk.Label(self.root, text="ShadowBlade © 2025 все права защищены", bd=1, relief=tk.SUNKEN, anchor='center')
        self.footer_label.pack(side=tk.BOTTOM, fill=tk.X)

    def open_file(self):
        file_path = filedialog.askopenfilename(defaultextension=".ptf",
                                                filetypes=[("PTF files", "*.ptf"), ("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.text_area.delete(1.0, tk.END)  # Очистить текстовое поле
                    self.text_area.insert(tk.END, content)  # Вставить содержимое файла
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл: {e}")

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".ptf",
                                                   filetypes=[("PTF files", "*.ptf"), ("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    content = self.text_area.get(1.0, tk.END)  # Получить содержимое текстового поля
                    file.write(content.strip())  # Записать в файл
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    editor = TextEditor(root)
    root.mainloop()