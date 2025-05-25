import database
import tkinter as tk
from tkinter import messagebox, ttk, filedialog

# Добавить акционера
def add_shareholder():
    def save_new():
        database.add_shareholder(
            entry_name.get(),
            entry_passport.get(),
            int(entry_shares.get()),
            entry_date.get(),
            entry_type.get(),
            entry_phone.get()
        )
        top.destroy()
        refresh_table()

    top = tk.Toplevel(root)
    top.title("Добавить акционера")

    labels = ["ФИО", "Паспорт", "Кол-во акций", "Дата покупки", "Тип акций", "Телефон"]
    entries = []

    for i, label in enumerate(labels):
        tk.Label(top, text=label).grid(row=i, column=0, padx=5, pady=5)
    entry_name = tk.Entry(top); entry_name.grid(row=0, column=1)
    entry_passport = tk.Entry(top); entry_passport.grid(row=1, column=1)
    entry_shares = tk.Entry(top); entry_shares.grid(row=2, column=1)
    entry_date = tk.Entry(top); entry_date.grid(row=3, column=1)
    entry_type = tk.Entry(top); entry_type.grid(row=4, column=1)
    entry_phone = tk.Entry(top); entry_phone.grid(row=5, column=1)

    tk.Button(top, text="Сохранить", command=save_new).grid(row=6, columnspan=2, pady=10)

# Удалить акционера
def delete_shareholder():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Внимание", "Выберите акционера для удаления.")
        return
    item = tree.item(selected_item)
    shareholder_id = item['values'][0]
    confirm = messagebox.askyesno("Удалить", f"Удалить акционера ID {shareholder_id}?")
    if confirm:
        database.delete_shareholder(shareholder_id)
        refresh_table()

# Обновить таблицу
def refresh_table():
    for row in tree.get_children():
        tree.delete(row)
    rows = database.get_all_shareholders()
    for row in rows:
        tree.insert('', 'end', values=row)

# Экспорт в CSV
def export_to_csv():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV файлы", "*.csv")])
    if not file_path:
        return
    rows = database.get_all_shareholders()
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'ФИО', 'Паспорт', 'Акции', 'Дата', 'Тип', 'Телефон'])
        writer.writerows(rows)
    messagebox.showinfo("Успех", f"Данные экспортированы в {file_path}")

# Основное окно
root = tk.Tk()
root.title("Реестр акционеров")
root.geometry("950x500")
root.resizable(False, False)
root.configure(bg="#f7f7f7")

# Верхнее меню
frame_buttons = tk.Frame(root, bg="#f7f7f7")
frame_buttons.pack(pady=10)

btn_add = tk.Button(frame_buttons, text="Добавить", command=add_shareholder, width=20, bg="#4caf50", fg="white")
btn_add.pack(side=tk.LEFT, padx=10)

btn_delete = tk.Button(frame_buttons, text="Удалить", command=delete_shareholder, width=20, bg="#f44336", fg="white")
btn_delete.pack(side=tk.LEFT, padx=10)

btn_export = tk.Button(frame_buttons, text="Экспорт в CSV", command=export_to_csv, width=20, bg="#2196f3", fg="white")
btn_export.pack(side=tk.LEFT, padx=10)

# Таблица акционеров
columns = ("ID", "ФИО", "Паспорт", "Акции", "Дата", "Тип", "Телефон")
tree = ttk.Treeview(root, columns=columns, show="headings", height=20)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=130, anchor=tk.CENTER)

tree.pack(pady=10)

# Стиль таблицы
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview.Heading", font=('Arial', 11, 'bold'))
style.configure("Treeview", font=('Arial', 10), rowheight=26)

# Запуск приложения
database.init_db()
refresh_table()
root.mainloop()
