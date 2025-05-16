import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import csv
import os

DATA_FILE = r"C:\Users\111\Desktop\perekup\prices.csv"
prices = {}

# Цвета для тёмной темы
DARK_BG = "#2e2e2e"
DARK_FRAME_BG = "#3c3f41"
DARK_BUTTON_BG = "#5a5a5a"
DARK_BUTTON_ACTIVE_BG = "#707070"
DARK_TEXT = "#e0e0e0"
DARK_HIGHLIGHT = "#4a90e2"
DARK_ENTRY_BG = "#45494a"

def normalize_product_name(name):
    return name.strip().lower()

def load_data():
    global prices
    prices = {}
    if not os.path.exists(DATA_FILE):
        return
    try:
        with open(DATA_FILE, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 2:
                    continue
                product = row[0].strip().lower()
                price_list = []
                for price_str in row[1:]:
                    try:
                        price = float(price_str)
                        price_list.append(price)
                    except ValueError:
                        pass
                if price_list:
                    prices[product] = price_list
    except Exception as e:
        messagebox.showerror("Ошибка загрузки", str(e))

def save_data():
    folder = os.path.dirname(DATA_FILE)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)
    try:
        with open(DATA_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for product, price_list in prices.items():
                writer.writerow([product] + price_list)
    except Exception as e:
        messagebox.showerror("Ошибка сохранения", str(e))

def get_average_price(product):
    product = normalize_product_name(product)
    if product not in prices or not prices[product]:
        return None
    recent_prices = prices[product][-5:]
    return sum(recent_prices) / len(recent_prices)

def add_price(product, price):
    product = normalize_product_name(product)
    if price <= 0:
        messagebox.showerror("Ошибка", "Цена должна быть положительным числом!")
        return False
    if product not in prices:
        prices[product] = []
    prices[product].append(price)
    save_data()
    refresh_table()
    return True

def delete_product(product):
    product = normalize_product_name(product)
    if product in prices:
        del prices[product]
        save_data()
        refresh_table()
        messagebox.showinfo("Удаление", f"Товар '{product}' удалён.")
        return True
    else:
        messagebox.showerror("Ошибка", f"Товар '{product}' не найден.")
        return False

def compare_with_last_price(product, new_price):
    product = normalize_product_name(product)
    if product not in prices or not prices[product]:
        return None
    last_price = prices[product][-1]
    diff = new_price - last_price
    percent_diff = (diff / last_price) * 100 if last_price != 0 else 0
    return last_price, diff, percent_diff

def calculate_total_for_products_by_indices(indices, product_keys):
    total = 0.0
    missing_indices = []
    for idx in indices:
        if 0 <= idx < len(product_keys):
            prod = product_keys[idx]
            avg_price = get_average_price(prod)
            if avg_price is None:
                missing_indices.append(str(idx + 1))
            else:
                total += avg_price
        else:
            missing_indices.append(str(idx + 1))
    return total, missing_indices

def refresh_table(filtered_products=None):
    for row in tree.get_children():
        tree.delete(row)
    product_list = filtered_products if filtered_products is not None else sorted(prices.keys())
    for product in product_list:
        price_list = prices[product]
        avg = get_average_price(product)
        tree.insert('', 'end', values=(
            product[:50],
            len(price_list),
            f"{min(price_list):.2f}",
            f"{avg:.2f}" if avg is not None else "",
            f"{max(price_list):.2f}"
        ))

def add_product():
    product = simpledialog.askstring("Добавить товар", "Введите название товара:", parent=root)
    if not product:
        return
    try:
        price_str = simpledialog.askstring("Добавить цену", "Введите цену товара:", parent=root)
        price = float(price_str)
    except (TypeError, ValueError):
        messagebox.showerror("Ошибка", "Введите корректную цену!", parent=root)
        return
    if add_price(product, price):
        messagebox.showinfo("Успех", f"Товар '{product}' с ценой {price:.2f} добавлен.", parent=root)

def show_average_price():
    product = simpledialog.askstring("Средняя цена", "Введите название товара:", parent=root)
    if not product:
        return
    avg = get_average_price(product)
    if avg is None:
        messagebox.showerror("Ошибка", f"Нет данных по товару '{product}'.", parent=root)
    else:
        messagebox.showinfo("Средняя цена", f"Средняя цена товара '{product}': {avg:.2f}", parent=root)

def show_all_products():
    if not prices:
        messagebox.showinfo("Товары", "Список товаров пуст.", parent=root)
        return
    lines = []
    for product in sorted(prices.keys()):
        avg = get_average_price(product)
        lines.append(f"{product[:50]} : {avg:.2f}" if avg is not None else f"{product[:50]} : Нет данных")
    text = "\n".join(lines)
    show_text_window("Все товары и цены", text)

def compare_prices():
    product = simpledialog.askstring("Сравнить цены", "Введите название товара:", parent=root)
    if not product:
        return
    if product not in prices:
        messagebox.showerror("Ошибка", f"Нет данных по товару '{product}'.", parent=root)
        return
    price_list = prices[product]
    text = (f"Товар: {product}\n"
            f"Минимальная цена: {min(price_list):.2f}\n"
            f"Максимальная цена: {max(price_list):.2f}\n"
            f"Средняя цена: {sum(price_list)/len(price_list):.2f}")
    messagebox.showinfo("Сравнение цен", text, parent=root)

def compare_with_last():
    product = simpledialog.askstring("Сравнить с последней ценой", "Введите название товара:", parent=root)
    if not product:
        return
    try:
        price_str = simpledialog.askstring("Сравнить с последней ценой", "Введите цену для сравнения:", parent=root)
        new_price = float(price_str)
    except (TypeError, ValueError):
        messagebox.showerror("Ошибка", "Введите корректную цену!", parent=root)
        return
    result = compare_with_last_price(product, new_price)
    if result is None:
        messagebox.showerror("Ошибка", f"Нет данных по товару '{product}'.", parent=root)
        return
    last_price, diff, percent_diff = result
    if diff > 0:
        text = (f"Последняя цена: {last_price:.2f}\n"
                f"Введённая цена выше последней на {diff:.2f} ({percent_diff:.2f}%)!")
        messagebox.showinfo("Сравнение с последней ценой", text, parent=root)
    elif diff < 0:
        text = (f"Последняя цена: {last_price:.2f}\n"
                f"Введённая цена ниже последней на {-diff:.2f} ({-percent_diff:.2f}%)")
        if abs(percent_diff) >= 10:
            text += "\nОтличная цена! Значительно ниже последней."
        messagebox.showinfo("Сравнение с последней ценой", text, parent=root)
    else:
        messagebox.showinfo("Сравнение с последней ценой", "Введённая цена равна последней.", parent=root)

def delete_product_ui():
    product = simpledialog.askstring("Удалить товар", "Введите название товара для удаления:", parent=root)
    if not product:
        return
    delete_product(product)

def calculate_total():
    if not prices:
        messagebox.showinfo("Ошибка", "Список товаров пуст.", parent=root)
        return
    product_keys = sorted(prices.keys())
    prompt = "Введите номера товаров через запятую (например: 1,3,5):\n\n"
    prompt += "\n".join(f"{i+1}. {p[:50]}" for i, p in enumerate(product_keys))
    input_str = simpledialog.askstring("Общая сумма", prompt, parent=root)
    if not input_str:
        return
    try:
        indices = [int(x.strip()) - 1 for x in input_str.split(",") if x.strip()]
    except ValueError:
        messagebox.showerror("Ошибка", "Введите корректные номера товаров через запятую.", parent=root)
        return
    total_sum, missing = calculate_total_for_products_by_indices(indices, product_keys)
    text = f"Общая сумма выбранных товаров: {total_sum:.2f}"
    if missing:
        text += f"\nНекорректные номера или отсутствующие товары: {', '.join(missing)}"
    messagebox.showinfo("Общая сумма", text, parent=root)

def show_text_window(title, text):
    win = tk.Toplevel(root)
    win.title(title)
    win.geometry("600x400")
    win.configure(bg=DARK_BG)
    text_widget = tk.Text(win, wrap=tk.WORD, bg=DARK_ENTRY_BG, fg=DARK_TEXT, insertbackground=DARK_TEXT)
    text_widget.pack(expand=True, fill=tk.BOTH)
    text_widget.insert(tk.END, text)
    text_widget.config(state=tk.DISABLED)

def show_search_results_editable_with_add(filtered_products):
    if not filtered_products:
        messagebox.showinfo("Поиск", "Ничего не найдено.", parent=root)
        return

    win = tk.Toplevel(root)
    win.title("Редактирование цен покупки и продажи")
    win.geometry("900x500")
    win.configure(bg=DARK_BG)

    columns = ("Название (ср. цена)", "Цена покупки", "Цена продажи (средняя)")
    tree_search = ttk.Treeview(win, columns=columns, show="headings")
    for col in columns:
        tree_search.heading(col, text=col)
        tree_search.column(col, width=300 if col == columns[0] else 150, anchor='center')
    tree_search.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    style_search = ttk.Style(win)
    style_search.theme_use('clam')
    style_search.configure("Treeview",
                           background=DARK_FRAME_BG,
                           foreground=DARK_TEXT,
                           fieldbackground=DARK_FRAME_BG,
                           font=("Segoe UI", 10),
                           rowheight=25)
    style_search.map('Treeview', background=[('selected', DARK_HIGHLIGHT)], foreground=[('selected', '#ffffff')])
    style_search.configure("Treeview.Heading",
                           background=DARK_BUTTON_BG,
                           foreground=DARK_TEXT,
                           font=("Segoe UI", 11, "bold"))

    # Заполним таблицу данными
    for product in filtered_products:
        avg_price = get_average_price(product)
        if avg_price is None:
            continue
        price_buy = prices[product][0] if prices[product] else avg_price / 1.10  # первая цена из списка или прибл.
        price_sell = avg_price
        display_name = f"{product[:40]} (ср: {avg_price:.2f})"
        tree_search.insert('', 'end', values=(
            display_name,
            f"{price_buy:.2f}",
            f"{price_sell:.2f}"
        ))

    def save_edit(item_id, col_index, new_val):
        product_display = tree_search.set(item_id, columns[0])
        product_name = product_display.split(" (ср:")[0].lower()

        try:
            val_float = float(new_val)
            if val_float <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное положительное число", parent=win)
            return False

        if product_name not in prices:
            messagebox.showerror("Ошибка", f"Товар '{product_name}' не найден в базе", parent=win)
            return False

        if col_index == 1:
            # Цена покупки изменена - обновим первую цену в списке или добавим, если пусто
            if prices[product_name]:
                prices[product_name][0] = val_float
            else:
                prices[product_name].append(val_float)
        elif col_index == 2:
            # Цена продажи изменена - обновим последнюю цену в списке или добавим, если пусто
            if prices[product_name]:
                prices[product_name][-1] = val_float
            else:
                prices[product_name].append(val_float)

        save_data()
        refresh_table()
        # Обновим среднюю цену в названии
        avg_price = get_average_price(product_name)
        display_name_new = f"{product_name[:40]} (ср: {avg_price:.2f})"
        tree_search.set(item_id, columns[0], display_name_new)
        return True

    def on_double_click(event):
        item_id = tree_search.identify_row(event.y)
        column = tree_search.identify_column(event.x)
        if not item_id or column == '#0':
            return

        col_index = int(column.replace('#', '')) - 1
        if col_index == 0:
            # Название не редактируем
            return

        old_value = tree_search.set(item_id, column)

        entry = tk.Entry(win)
        entry.insert(0, old_value)
        entry.select_range(0, tk.END)
        entry.focus()

        x, y, width, height = tree_search.bbox(item_id, column)
        entry.place(x=x + tree_search.winfo_rootx() - win.winfo_rootx(),
                    y=y + tree_search.winfo_rooty() - win.winfo_rooty(),
                    width=width, height=height)

        def save_and_close(event=None):
            new_val = entry.get()
            if save_edit(item_id, col_index, new_val):
                entry.destroy()

        entry.bind('<Return>', save_and_close)
        entry.bind('<FocusOut>', lambda e: entry.destroy())

    tree_search.bind('<Double-1>', on_double_click)

    def add_price_for_selected():
        selected = tree_search.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите товар для добавления цены", parent=win)
            return
        item_id = selected[0]
        product_display = tree_search.set(item_id, columns[0])
        product_name = product_display.split(" (ср:")[0].lower()

        price_str = simpledialog.askstring("Добавить цену", f"Введите новую цену для товара '{product_name}':", parent=win)
        if price_str is None:
            return
        try:
            price = float(price_str)
            if price <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную положительную цену", parent=win)
            return

        if product_name not in prices:
            prices[product_name] = []
        prices[product_name].append(price)
        save_data()
        refresh_table()

        # Обновляем среднюю цену в названии
        avg_price = get_average_price(product_name)
        display_name_new = f"{product_name[:40]} (ср: {avg_price:.2f})"
        tree_search.set(item_id, columns[0], display_name_new)

        # Обновляем цену продажи в таблице (последняя цена)
        tree_search.set(item_id, columns[2], f"{avg_price:.2f}")

        messagebox.showinfo("Успех", f"Цена {price:.2f} добавлена для товара '{product_name}'", parent=win)

    btn_add_price = tk.Button(win, text="Добавить новую цену выбранному товару", command=add_price_for_selected,
                              bg=DARK_BUTTON_BG, fg=DARK_TEXT, activebackground=DARK_BUTTON_ACTIVE_BG,
                              relief=tk.FLAT, bd=0, font=("Segoe UI", 10))
    btn_add_price.pack(pady=5, padx=10, anchor='w')

    explanation = ("* Двойной клик по цене покупки или продажи позволяет изменить значение вручную.\n"
                   "* Добавляйте новую цену для выбранного товара кнопкой ниже.\n"
                   "* Средняя цена отображается рядом с названием товара.\n"
                   "* Изменения сохраняются и обновляют основное окно.")
    label_expl = tk.Label(win, text=explanation, bg=DARK_BG, fg=DARK_TEXT,
                          font=("Segoe UI", 9), justify=tk.LEFT)
    label_expl.pack(padx=10, pady=10, anchor='w')

def search_products():
    keyword = simpledialog.askstring("Поиск", "Введите ключевое слово для поиска:", parent=root)
    if keyword is None or keyword.strip() == "":
        refresh_table()
        return
    keyword = keyword.lower()
    filtered = [p for p in prices if keyword in p]
    if not filtered:
        messagebox.showinfo("Поиск", f"Товары по запросу '{keyword}' не найдены.", parent=root)
        return
    show_search_results_editable_with_add(filtered)

# --- Основное окно ---
root = tk.Tk()
root.title("Учёт цен товаров")
root.geometry("900x500")
root.configure(bg=DARK_BG)

frame = tk.Frame(root, bg=DARK_BG)
frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

btn_frame = tk.Frame(frame, bg=DARK_FRAME_BG)
btn_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0,10), pady=5)

buttons = [
    ("Добавить цену товара", add_product),
    ("Узнать среднюю цену товара", show_average_price),
    ("Показать все товары и цены", show_all_products),
    ("Сравнить цены товара", compare_prices),
    ("Сравнить введённую цену с последней", compare_with_last),
    ("Удалить товар", delete_product_ui),
    ("Посчитать общую\nсумму товаров", calculate_total),
    ("Поиск товара по ключевому слову", search_products),
    ("Выход", root.quit)
]

for (text, cmd) in buttons:
    btn = tk.Button(btn_frame, text=text, command=cmd, width=30, justify=tk.CENTER,
                    wraplength=200,
                    bg=DARK_BUTTON_BG, fg=DARK_TEXT, activebackground=DARK_BUTTON_ACTIVE_BG,
                    relief=tk.FLAT, bd=0, font=("Segoe UI", 10))
    btn.pack(fill=tk.X, pady=3)

table_frame = tk.Frame(frame, bg=DARK_BG)
table_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

style = ttk.Style()
style.theme_use('clam')

style.configure("Treeview",
                background=DARK_FRAME_BG,
                foreground=DARK_TEXT,
                fieldbackground=DARK_FRAME_BG,
                font=("Segoe UI", 10),
                rowheight=25)
style.map('Treeview', background=[('selected', DARK_HIGHLIGHT)], foreground=[('selected', '#ffffff')])

style.configure("Treeview.Heading",
                background=DARK_BUTTON_BG,
                foreground=DARK_TEXT,
                font=("Segoe UI", 11, "bold"))

tree = ttk.Treeview(table_frame, columns=("Название", "Кол-во цен", "Мин", "Сред", "Макс"), show="headings")
for col in ("Название", "Кол-во цен", "Мин", "Сред", "Макс"):
    tree.heading(col, text=col)
    tree.column(col, width=140 if col == "Название" else 80, anchor='center')
tree.pack(fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

load_data()
refresh_table()

root.mainloop()

