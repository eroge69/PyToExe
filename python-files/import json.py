import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
from datetime import datetime
import os

SAVE_FILE = "payers_data.json"

class UtilityPaymentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Учет оплаты коммунальных услуг")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)

        # Данные о плательщиках
        self.payers = []
        self.load_on_start()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Создание вкладок
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Вкладки
        self.tab_add = ttk.Frame(self.notebook)
        self.tab_search = ttk.Frame(self.notebook)
        self.tab_list = ttk.Frame(self.notebook)
        self.tab_info = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_add, text="Добавить плательщика")
        self.notebook.add(self.tab_search, text="Поиск плательщика")
        self.notebook.add(self.tab_list, text="Список плательщиков")
        self.notebook.add(self.tab_info, text="Информация")

        # Инициализация вкладок
        self.init_add_tab()
        self.init_search_tab()
        self.init_list_tab()
        self.init_info_tab()

    def on_closing(self):
        self.save_on_exit()
        self.root.destroy()

    def save_on_exit(self):
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.payers, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")

    def load_on_start(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r", encoding="utf-8") as f:
                    self.payers = json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")

    def init_add_tab(self):
        frame = ttk.Frame(self.tab_add)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Label(frame, text="Добавить нового плательщика", font=("Arial", 16, "bold")).pack(pady=10)

        self.entry_name = self.create_entry(frame, "ФИО:")
        self.entry_address = self.create_entry(frame, "Адрес:")
        self.entry_amount = self.create_entry(frame, "Сумма оплаты:")
        self.entry_date = self.create_entry(frame, "Дата (ДД.ММ.ГГГГ):")

        ttk.Button(frame, text="Добавить", command=self.add_payer).pack(pady=10)
        ttk.Button(frame, text="Загрузить из файла", command=self.load_from_file).pack(pady=5)

    def init_info_tab(self):
        frame = ttk.Frame(self.tab_info)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Label(frame, text="Информация о плательщиках", font=("Arial", 16, "bold")).pack(pady=10)

        self.info_entry = self.create_entry(frame, "Введите ФИО:")
        ttk.Button(frame, text="Показать сумму", command=self.show_total_by_name).pack(pady=5)

        self.info_text = tk.Text(frame, height=15, font=("Arial", 12))
        scrollbar = ttk.Scrollbar(frame, command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.info_text.pack(fill="both", expand=True)

    def show_total_by_name(self):
        name_query = self.info_entry.get().strip().lower()
        total = sum(p["Сумма"] for p in self.payers if name_query in p["ФИО"].lower())
        filtered = [p for p in self.payers if name_query in p["ФИО"].lower()]

        if not filtered:
            self.info_text.delete("1.0", tk.END)
            self.info_text.insert("1.0", "Плательщик не найден!")
            return

        self.info_text.delete("1.0", tk.END)
        for p in filtered:
            self.info_text.insert(tk.END, f"ФИО: {p['ФИО']}, Сумма: {p['Сумма']} руб.\n")
        self.info_text.insert(tk.END, f"\nИтого: {total:.2f} руб.")

    def create_entry(self, parent, label_text):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=5)

        ttk.Label(frame, text=label_text, width=20).pack(side="left", padx=5)
        entry = ttk.Entry(frame)
        entry.pack(side="left", fill="x", expand=True)
        return entry

    def init_search_tab(self):
        frame = ttk.Frame(self.tab_search)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Label(frame, text="Поиск плательщика", font=("Arial", 16, "bold")).pack(pady=10)

        search_frame = ttk.Frame(frame)
        search_frame.pack(fill="x", pady=10)

        ttk.Label(search_frame, text="ФИО плательщика:", width=20).pack(side="left", padx=5)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(search_frame, text="Найти", command=self.search_payer, width=10).pack(side="left", padx=5)

        self.search_result = tk.Text(frame, height=10, font=("Arial", 12))
        scrollbar = ttk.Scrollbar(frame, command=self.search_result.yview)
        self.search_result.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.search_result.pack(fill="both", expand=True, pady=10)

    def init_list_tab(self):
        frame = ttk.Frame(self.tab_list)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Label(frame, text="Список плательщиков", font=("Arial", 16, "bold")).pack(pady=10)

        self.tree = ttk.Treeview(
            frame,
            columns=("ФИО", "Адрес", "Сумма", "Дата"),
            show="headings"
        )

        self.tree.heading("ФИО", text="ФИО", command=lambda: self.sort_tree("ФИО"))
        self.tree.heading("Адрес", text="Адрес", command=lambda: self.sort_tree("Адрес"))
        self.tree.heading("Сумма", text="Сумма", command=lambda: self.sort_tree("Сумма"))
        self.tree.heading("Дата", text="Дата", command=lambda: self.sort_tree("Дата"))

        self.tree.column("ФИО", width=200)
        self.tree.column("Адрес", width=200)
        self.tree.column("Сумма", width=100, anchor="center")
        self.tree.column("Дата", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        ttk.Button(frame, text="Обновить список", command=self.update_list).pack(pady=10)

    def add_payer(self):
        name = self.entry_name.get().strip()
        address = self.entry_address.get().strip()
        amount = self.entry_amount.get().strip()
        date = self.entry_date.get().strip()

        if not all([name, address, amount, date]):
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return

        try:
            amount = float(amount)
            datetime.strptime(date, "%d.%m.%Y")
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректные данные (сумма или дата)!")
            return

        self.payers.append({
            "ФИО": name,
            "Адрес": address,
            "Сумма": amount,
            "Дата": date
        })

        messagebox.showinfo("Успех", "Плательщик добавлен!")
        self.clear_entries()
        self.update_list()

    def clear_entries(self):
        self.entry_name.delete(0, tk.END)
        self.entry_address.delete(0, tk.END)
        self.entry_amount.delete(0, tk.END)
        self.entry_date.delete(0, tk.END)

    def load_from_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, list):
                    self.payers.extend(data)
                    messagebox.showinfo("Успех", f"Добавлено {len(data)} записей!")
                    self.update_list()
                else:
                    messagebox.showerror("Ошибка", "Файл должен содержать список плательщиков!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")

    def search_payer(self):
        query = self.search_entry.get().strip().lower()
        if not query:
            messagebox.showerror("Ошибка", "Введите ФИО для поиска!")
            return

        found = [p for p in self.payers if query in p["ФИО"].lower()]
        if not found:
            self.search_result.delete("1.0", tk.END)
            self.search_result.insert("1.0", "Плательщик не найден!")
            return

        result_text = "\n\n".join([
            f"ФИО: {p['ФИО']}\nАдрес: {p['Адрес']}\nСумма: {p['Сумма']} руб.\nДата: {p['Дата']}"
            for p in found
        ])
        self.search_result.delete("1.0", tk.END)
        self.search_result.insert("1.0", result_text)

    def update_list(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for payer in self.payers:
            self.tree.insert("", "end", values=(
                payer["ФИО"],
                payer["Адрес"],
                payer["Сумма"],
                payer["Дата"]
            ))

    def sort_tree(self, column):
        reverse = False
        if column == "Сумма":
            key = lambda x: float(x["Сумма"])
        elif column == "Дата":
            key = lambda x: datetime.strptime(x["Дата"], "%d.%m.%Y")
        else:
            key = lambda x: x[column]

        self.payers.sort(key=key, reverse=reverse)
        self.update_list()

if __name__ == "__main__":
    root = tk.Tk()
    app = UtilityPaymentApp(root)
    root.mainloop()