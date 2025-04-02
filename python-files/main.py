import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import pandas as pd
import csv
from PIL import Image, ImageTk
import os
import shutil


def init_files():
    required_animal_columns = ["ID", "Name", "Type", "Breed", "Gender", "Age", "Appearance", "Health", "Status",
                               "Origin", "Arrival_Date", "Previous_Conditions", "Owner_Info", "Death_Date"]
    required_processing_columns = ["Animal_ID", "Date", "Treatment"]

    if not os.path.exists("animals.csv"):
        with open("animals.csv", "w", newline="", encoding="windows-1251") as f:
            writer = csv.writer(f)
            writer.writerow(required_animal_columns)
            writer.writerow(
                [1, "Барон", "Собака", "Немецкая овчарка", "М", 4, "Черный с рыжим", "Здоров, привит", "Доступен",
                 "Улица", "2024-11-15", "Бездомный, жил в промзоне", "", ""])
            writer.writerow(
                [2, "Мурка", "Кошка", "Сиамская", "Ж", 2, "Кремовая с темными ушами", "Здорова, стерилизована",
                 "Доступен",
                 "Приют", "2025-01-10", "Клетка в приюте", "", ""])
    else:
        df = pd.read_csv("animals.csv", encoding="windows-1251")
        missing_columns = [col for col in required_animal_columns if col not in df.columns]
        if missing_columns:
            for col in missing_columns:
                if col in ["Origin", "Arrival_Date", "Previous_Conditions", "Owner_Info", "Death_Date"]:
                    df[col] = "Не указано"
                else:
                    df[col] = ""
            df.to_csv("animals.csv", index=False, encoding="windows-1251")

    if not os.path.exists("processing.csv"):
        with open("processing.csv", "w", newline="", encoding="windows-1251") as f:
            writer = csv.writer(f)
            writer.writerow(required_processing_columns)


class NurseryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🐾 Питомник животных")
        self.root.geometry("900x700")

        # Цветовая палитра
        self.bg_color = "#F9E4E8"
        self.text_color = "#5C4B7D"
        self.button_bg = "#FFDAB9"
        self.button_hover = "#FFE8D6"
        self.accent_color = "#B5EAD7"
        self.root.configure(bg=self.bg_color)

        # Настройка стилей
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=self.accent_color, padding=[15, 8], font=("Helvetica", 12),
                             borderwidth=0, relief="flat")
        self.style.map("TNotebook.Tab", background=[("selected", self.bg_color)],
                       foreground=[("selected", self.text_color)])
        self.style.configure("Treeview", font=("Helvetica", 10), rowheight=25, background="#FFFFFF",
                             fieldbackground="#FFFFFF", foreground=self.text_color)
        self.style.configure("Treeview.Heading", font=("Helvetica", 11, "bold"), background=self.accent_color)

        init_files()

        # Главное меню с кнопками "Добавить животное" и "Общий отчет"
        menu_frame = tk.Frame(self.root, bg=self.bg_color)
        menu_frame.pack(fill="x", padx=15, pady=5)

        add_btn_canvas = tk.Canvas(menu_frame, width=150, height=35, bg=self.bg_color, highlightthickness=0)
        add_btn_canvas.create_rectangle(5, 5, 200, 60, fill=self.button_bg, outline=self.button_bg)
        add_btn_canvas.create_text(75, 17, text="Добавить животное", fill=self.text_color, font=("Helvetica", 11))
        add_btn_canvas.bind("<Button-1>", lambda e: self.add_animal_window())
        add_btn_canvas.bind("<Enter>", lambda e: add_btn_canvas.itemconfig(1, fill=self.button_hover))
        add_btn_canvas.bind("<Leave>", lambda e: add_btn_canvas.itemconfig(1, fill=self.button_bg))
        add_btn_canvas.pack(side="left", padx=5)

        report_btn_canvas = tk.Canvas(menu_frame, width=150, height=35, bg=self.bg_color, highlightthickness=0)
        report_btn_canvas.create_rectangle(5, 5, 200, 60, fill=self.button_bg, outline=self.button_bg)
        report_btn_canvas.create_text(75, 17, text="Общий отчет", fill=self.text_color, font=("Helvetica", 11))
        report_btn_canvas.bind("<Button-1>", lambda e: self.show_general_report())
        report_btn_canvas.bind("<Enter>", lambda e: report_btn_canvas.itemconfig(1, fill=self.button_hover))
        report_btn_canvas.bind("<Leave>", lambda e: report_btn_canvas.itemconfig(1, fill=self.button_bg))
        report_btn_canvas.pack(side="left", padx=5)

        # Вкладки
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=10)

        self.main_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.main_frame, text="Доступные животные")

        self.adopted_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.adopted_frame, text="Пристроенные")

        self.dead_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.dead_frame, text="Умершие")

        self.load_main_content()
        self.load_adopted_content()
        self.load_dead_content()

    def load_main_content(self):
        frame = tk.Frame(self.main_frame, bg=self.bg_color)
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Список животных
        listbox_frame = tk.Frame(frame, bg=self.bg_color)
        listbox_frame.pack(side="left", fill="y", padx=10)

        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side="right", fill="y")

        self.animals_listbox = tk.Listbox(
            listbox_frame,
            width=25,
            height=30,
            font=("Helvetica", 12),
            bg="#FFFFFF",
            fg=self.text_color,
            selectbackground=self.accent_color,
            yscrollcommand=scrollbar.set
        )
        self.animals_listbox.pack(side="left", fill="y")
        scrollbar.config(command=self.animals_listbox.yview)

        # Информация о выбранном животном
        self.info_frame = tk.Frame(frame, bg="#FFFFFF", padx=20, pady=20)
        self.info_frame.pack(side="right", fill="both", expand=True)
        self.info_frame.config(highlightbackground=self.accent_color, highlightthickness=2)

        # Заполняем список животных
        animals = pd.read_csv("animals.csv", encoding="windows-1251")
        available_animals = animals[animals["Status"] == "Доступен"]

        for _, animal in available_animals.iterrows():
            self.animals_listbox.insert("end", animal["Name"])

        # Привязываем событие выбора
        self.animals_listbox.bind("<<ListboxSelect>>", self.show_selected_animal_info)

    def show_selected_animal_info(self, event):
        # Очищаем предыдущую информацию
        for widget in self.info_frame.winfo_children():
            widget.destroy()

        # Получаем выбранное животное
        selection = self.animals_listbox.curselection()
        if not selection:
            return

        selected_name = self.animals_listbox.get(selection)
        animals = pd.read_csv("animals.csv", encoding="windows-1251")
        animal = animals[animals["Name"] == selected_name].iloc[0]

        # Отображаем фото
        try:
            img = ImageTk.PhotoImage(Image.open(f"animal_{animal['ID']}.png").resize((200, 200)))
            photo_label = tk.Label(self.info_frame, image=img, bg="#FFFFFF")
            photo_label.image = img
            photo_label.pack(pady=10)
        except:
            no_photo_label = tk.Label(
                self.info_frame,
                text="Фото отсутствует",
                bg="#FFFFFF",
                fg="gray",
                font=("Helvetica", 10)
            )
            no_photo_label.pack(pady=10)

        # Кнопка для добавления фото
        photo_btn = tk.Button(
            self.info_frame,
            text="Добавить/изменить фото",
            command=lambda: self.add_photo(animal["ID"], photo_label if 'photo_label' in locals() else None, None),
            bg=self.button_bg,
            fg=self.text_color,
            font=("Helvetica", 10),
            relief="flat"
        )
        photo_btn.pack(pady=5)

        # Отображаем информацию о животном
        info_text = (
            f"Имя: {animal['Name']}\n"
            f"Тип: {animal['Type']}\n"
            f"Порода: {animal['Breed']}\n"
            f"Пол: {animal['Gender']}\n"
            f"Возраст: {animal['Age']} лет\n"
            f"Внешность: {animal['Appearance']}\n"
            f"Здоровье: {animal['Health']}\n"
            f"Откуда: {animal.get('Origin', 'Не указано')}\n"
            f"Дата поступления: {animal.get('Arrival_Date', 'Не указано')}\n"
            f"Предыдущие условия: {animal.get('Previous_Conditions', 'Не указано')}"
        )

        info_label = tk.Label(
            self.info_frame,
            text=info_text,
            bg="#FFFFFF",
            fg=self.text_color,
            font=("Helvetica", 11),
            justify="left"
        )
        info_label.pack(pady=10)

        # Кнопки действий
        btn_frame = tk.Frame(self.info_frame, bg="#FFFFFF")
        btn_frame.pack(pady=10)

        for text, cmd in [
            ("Обработка", lambda: self.show_processing(animal)),
            ("Пристроили", lambda: self.move_to_adopted(animal)),
            ("Умерло", lambda: self.move_to_dead(animal))
        ]:
            btn = tk.Button(
                btn_frame,
                text=text,
                command=cmd,
                bg=self.button_bg,
                fg=self.text_color,
                font=("Helvetica", 10),
                relief="flat",
                padx=10,
                pady=5
            )
            btn.pack(side="left", padx=5)

    def add_animal_window(self):
        add_win = tk.Toplevel(self.root)
        add_win.title("Добавить животное")
        add_win.geometry("400x500")
        add_win.configure(bg=self.bg_color)

        frame = tk.Frame(add_win, bg="#FFFFFF", padx=20, pady=20)
        frame.pack(fill="both", expand=True, padx=15, pady=15)
        frame.config(highlightbackground=self.accent_color, highlightthickness=2)

        fields = ["Имя", "Тип", "Порода", "Пол", "Возраст", "Внешность", "Здоровье", "Откуда", "Дата поступления",
                  "Предыдущие условия"]
        entries = {}

        for i, field in enumerate(fields):
            tk.Label(frame, text=f"{field}:", bg="#FFFFFF", fg=self.text_color, font=("Helvetica", 11)).grid(row=i,
                                                                                                             column=0,
                                                                                                             pady=5,
                                                                                                             sticky="w")
            entry = tk.Entry(frame, font=("Helvetica", 11), bg="#FFFFFF", fg=self.text_color, relief="flat")
            entry.grid(row=i, column=1, pady=5, sticky="ew")
            entry.config(highlightbackground=self.accent_color, highlightthickness=1)
            entries[field] = entry

        btn_canvas = tk.Canvas(frame, width=110, height=35, bg="#FFFFFF", highlightthickness=0)
        btn_canvas.create_oval(5, 5, 105, 30, fill=self.button_bg, outline=self.button_bg)
        btn_canvas.create_text(55, 17, text="Сохранить", fill=self.text_color, font=("Helvetica", 11))
        btn_canvas.bind("<Button-1>", lambda e: self.save_new_animal(entries, add_win))
        btn_canvas.bind("<Enter>", lambda e: btn_canvas.itemconfig(1, fill=self.button_hover))
        btn_canvas.bind("<Leave>", lambda e: btn_canvas.itemconfig(1, fill=self.button_bg))
        btn_canvas.grid(row=len(fields), column=0, columnspan=2, pady=10)

    def save_new_animal(self, entries, window):
        animals = pd.read_csv("animals.csv", encoding="windows-1251")
        new_id = animals["ID"].max() + 1 if not animals.empty else 1
        new_animal = [new_id,
                      entries["Имя"].get(),
                      entries["Тип"].get(),
                      entries["Порода"].get(),
                      entries["Пол"].get(),
                      entries["Возраст"].get(),
                      entries["Внешность"].get(),
                      entries["Здоровье"].get(),
                      "Доступен",
                      entries["Откуда"].get(),
                      entries["Дата поступления"].get(),
                      entries["Предыдущие условия"].get(),
                      "",  # Owner_Info
                      ""]  # Death_Date

        if not entries["Имя"].get():
            messagebox.showerror("Ошибка", "Имя животного обязательно!")
            return

        with open("animals.csv", "a", newline="", encoding="windows-1251") as f:
            writer = csv.writer(f)
            writer.writerow(new_animal)

        window.destroy()
        self.reload_all()
        messagebox.showinfo("Успех", "Животное добавлено!")

    def show_general_report(self):
        animals = pd.read_csv("animals.csv", encoding="windows-1251")
        total_animals = len(animals)
        adopted_count = len(animals[animals["Status"] == "Пристроен"])
        dead_count = len(animals[animals["Status"] == "Умер"])

        report_text = f"Общий отчет по питомнику:\n\n" \
                      f"Всего животных: {total_animals}\n" \
                      f"Пристроено: {adopted_count}\n" \
                      f"Умерло: {dead_count}"

        report_win = tk.Toplevel(self.root)
        report_win.title("Общий отчет")
        report_win.geometry("300x250")
        report_win.configure(bg=self.bg_color)

        frame = tk.Frame(report_win, bg="#FFFFFF", padx=20, pady=20)
        frame.pack(fill="both", expand=True, padx=15, pady=15)
        frame.config(highlightbackground=self.accent_color, highlightthickness=2)

        tk.Label(frame, text=report_text, bg="#FFFFFF", fg=self.text_color, font=("Helvetica", 11),
                 justify="left").pack(pady=10)

        # Фрейм для кнопок
        btn_frame = tk.Frame(frame, bg="#FFFFFF")
        btn_frame.pack(pady=10)

        # Кнопка закрытия
        close_btn_canvas = tk.Canvas(btn_frame, width=110, height=35, bg="#FFFFFF", highlightthickness=0)
        close_btn_canvas.create_oval(5, 5, 105, 30, fill=self.button_bg, outline=self.button_bg)
        close_btn_canvas.create_text(55, 17, text="Закрыть", fill=self.text_color, font=("Helvetica", 11))
        close_btn_canvas.bind("<Button-1>", lambda e: report_win.destroy())
        close_btn_canvas.bind("<Enter>", lambda e: close_btn_canvas.itemconfig(1, fill=self.button_hover))
        close_btn_canvas.bind("<Leave>", lambda e: close_btn_canvas.itemconfig(1, fill=self.button_bg))
        close_btn_canvas.pack(side="left", padx=10)

        # Кнопка сохранения отчета
        save_btn_canvas = tk.Canvas(btn_frame, width=110, height=35, bg="#FFFFFF", highlightthickness=0)
        save_btn_canvas.create_oval(5, 5, 105, 30, fill=self.button_bg, outline=self.button_bg)
        save_btn_canvas.create_text(55, 17, text="Сохранить", fill=self.text_color, font=("Helvetica", 11))
        save_btn_canvas.bind("<Button-1>", lambda e: self.save_report_to_file(report_text, report_win))
        save_btn_canvas.bind("<Enter>", lambda e: save_btn_canvas.itemconfig(1, fill=self.button_hover))
        save_btn_canvas.bind("<Leave>", lambda e: save_btn_canvas.itemconfig(1, fill=self.button_bg))
        save_btn_canvas.pack(side="left", padx=10)

    def save_report_to_file(self, report_text, window):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")],
            title="Сохранить отчет"
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(report_text)
                messagebox.showinfo("Успех", f"Отчет успешно сохранен в файл:\n{file_path}")
                window.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")

    def show_processing(self, animal):
        proc_win = tk.Toplevel(self.root)
        proc_win.title(f"🐾 Обработка: {animal['Name']}")
        proc_win.geometry("550x500")
        proc_win.configure(bg=self.bg_color)

        tree_frame = tk.Frame(proc_win, bg="#FFFFFF")
        tree_frame.pack(fill="both", expand=True, padx=15, pady=15)
        tree_frame.config(highlightbackground=self.accent_color, highlightthickness=2)

        tree = ttk.Treeview(tree_frame, columns=("Date", "Treatment"), show="headings")
        tree.heading("Date", text="Дата")
        tree.heading("Treatment", text="Обработка")
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        processing = pd.read_csv("processing.csv", encoding="windows-1251")
        animal_proc = processing[processing["Animal_ID"] == animal["ID"]]
        for _, row in animal_proc.iterrows():
            tree.insert("", "end", values=(row["Date"], row["Treatment"]))

        form_frame = tk.Frame(proc_win, bg=self.bg_color)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Дата:", bg=self.bg_color, fg=self.text_color, font=("Helvetica", 11)).grid(row=0,
                                                                                                              column=0,
                                                                                                              padx=10,
                                                                                                              pady=5)
        date_entry = tk.Entry(form_frame, font=("Helvetica", 11), bg="#FFFFFF", fg=self.text_color, relief="flat")
        date_entry.grid(row=0, column=1, padx=10, pady=5)
        date_entry.config(highlightbackground=self.accent_color, highlightthickness=1)

        tk.Label(form_frame, text="Обработка:", bg=self.bg_color, fg=self.text_color, font=("Helvetica", 11)).grid(
            row=1, column=0, padx=10, pady=5)
        treat_entry = tk.Entry(form_frame, font=("Helvetica", 11), bg="#FFFFFF", fg=self.text_color, relief="flat")
        treat_entry.grid(row=1, column=1, padx=10, pady=5)
        treat_entry.config(highlightbackground=self.accent_color, highlightthickness=1)

        btn_frame = tk.Frame(form_frame, bg=self.bg_color)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        for text, cmd in [
            ("Добавить", lambda: self.add_processing(animal["ID"], date_entry.get(), treat_entry.get(), tree)),
            ("Редактировать", lambda: self.edit_processing(tree, animal["ID"])),
            ("Удалить", lambda: self.delete_processing(tree, animal["ID"]))]:
            btn_canvas = tk.Canvas(btn_frame, width=110, height=35, bg=self.bg_color, highlightthickness=0)
            btn_canvas.create_oval(5, 5, 105, 30, fill=self.button_bg, outline=self.button_bg)
            btn_canvas.create_text(55, 17, text=text, fill=self.text_color, font=("Helvetica", 11))
            btn_canvas.bind("<Button-1>", lambda e, c=cmd: c())
            btn_canvas.bind("<Enter>", lambda e, c=btn_canvas: c.itemconfig(1, fill=self.button_hover))
            btn_canvas.bind("<Leave>", lambda e, c=btn_canvas: c.itemconfig(1, fill=self.button_bg))
            btn_canvas.pack(side="left", padx=5)

    def add_processing(self, animal_id, date, treatment, tree):
        if not date or not treatment:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return
        with open("processing.csv", "a", newline="", encoding="windows-1251") as f:
            writer = csv.writer(f)
            writer.writerow([animal_id, date, treatment])
        tree.insert("", "end", values=(date, treatment))
        messagebox.showinfo("Успех", "Обработка добавлена!")

    def edit_processing(self, tree, animal_id):
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите запись!")
            return
        item = tree.item(selected[0])["values"]
        date, treatment = item

        edit_win = tk.Toplevel(self.root)
        edit_win.title("Редактировать обработку")
        edit_win.geometry("350x250")
        edit_win.configure(bg=self.bg_color)

        frame = tk.Frame(edit_win, bg="#FFFFFF", padx=20, pady=20)
        frame.pack(fill="both", expand=True, padx=15, pady=15)
        frame.config(highlightbackground=self.accent_color, highlightthickness=2)

        tk.Label(frame, text="Дата:", bg="#FFFFFF", fg=self.text_color, font=("Helvetica", 11)).pack(pady=5)
        date_entry = tk.Entry(frame, font=("Helvetica", 11), bg="#FFFFFF", fg=self.text_color, relief="flat")
        date_entry.insert(0, date)
        date_entry.pack(pady=5)
        date_entry.config(highlightbackground=self.accent_color, highlightthickness=1)

        tk.Label(frame, text="Обработка:", bg="#FFFFFF", fg=self.text_color, font=("Helvetica", 11)).pack(pady=5)
        treat_entry = tk.Entry(frame, font=("Helvetica", 11), bg="#FFFFFF", fg=self.text_color, relief="flat")
        treat_entry.insert(0, treatment)
        treat_entry.pack(pady=5)
        treat_entry.config(highlightbackground=self.accent_color, highlightthickness=1)

        btn_canvas = tk.Canvas(frame, width=110, height=35, bg="#FFFFFF", highlightthickness=0)
        btn_canvas.create_oval(5, 5, 105, 30, fill=self.button_bg, outline=self.button_bg)
        btn_canvas.create_text(55, 17, text="Сохранить", fill=self.text_color, font=("Helvetica", 11))
        btn_canvas.bind("<Button-1>",
                        lambda e: self.save_edit_processing(animal_id, date, date_entry.get(), treat_entry.get(), tree,
                                                            selected[0], edit_win))
        btn_canvas.bind("<Enter>", lambda e: btn_canvas.itemconfig(1, fill=self.button_hover))
        btn_canvas.bind("<Leave>", lambda e: btn_canvas.itemconfig(1, fill=self.button_bg))
        btn_canvas.pack(pady=10)

    def save_edit_processing(self, animal_id, old_date, new_date, new_treatment, tree, item_id, window):
        processing = pd.read_csv("processing.csv", encoding="windows-1251")
        processing.loc[
            (processing["Animal_ID"] == animal_id) & (processing["Date"] == old_date), ["Date", "Treatment"]] = [
            new_date, new_treatment]
        processing.to_csv("processing.csv", index=False, encoding="windows-1251")
        tree.item(item_id, values=(new_date, new_treatment))
        window.destroy()
        messagebox.showinfo("Успех", "Обработка обновлена!")

    def delete_processing(self, tree, animal_id):
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите запись!")
            return
        date = tree.item(selected[0])["values"][0]
        processing = pd.read_csv("processing.csv", encoding="windows-1251")
        processing = processing[~((processing["Animal_ID"] == animal_id) & (processing["Date"] == date))]
        processing.to_csv("processing.csv", index=False, encoding="windows-1251")
        tree.delete(selected[0])
        messagebox.showinfo("Успех", "Обработка удалена!")

    def move_to_adopted(self, animal):
        # Создаем окно для ввода информации о хозяине
        owner_win = tk.Toplevel(self.root)
        owner_win.title(f"Пристроение: {animal['Name']}")
        owner_win.geometry("400x300")
        owner_win.configure(bg=self.bg_color)

        frame = tk.Frame(owner_win, bg="#FFFFFF", padx=20, pady=20)
        frame.pack(fill="both", expand=True, padx=15, pady=15)
        frame.config(highlightbackground=self.accent_color, highlightthickness=2)

        tk.Label(frame, text="Информация о хозяине:", bg="#FFFFFF", fg=self.text_color,
                 font=("Helvetica", 12, "bold")).pack(pady=5)

        tk.Label(frame, text="ФИО:", bg="#FFFFFF", fg=self.text_color, font=("Helvetica", 11)).pack(pady=5)
        name_entry = tk.Entry(frame, font=("Helvetica", 11), bg="#FFFFFF", fg=self.text_color, relief="flat")
        name_entry.pack(pady=5)
        name_entry.config(highlightbackground=self.accent_color, highlightthickness=1)

        tk.Label(frame, text="Адрес:", bg="#FFFFFF", fg=self.text_color, font=("Helvetica", 11)).pack(pady=5)
        address_entry = tk.Entry(frame, font=("Helvetica", 11), bg="#FFFFFF", fg=self.text_color, relief="flat")
        address_entry.pack(pady=5)
        address_entry.config(highlightbackground=self.accent_color, highlightthickness=1)

        def save_owner_info():
            owner_info = f"ФИО: {name_entry.get()}, Адрес: {address_entry.get()}"
            animals = pd.read_csv("animals.csv", encoding="windows-1251")
            animals.loc[animals["ID"] == animal["ID"], ["Status", "Owner_Info"]] = ["Пристроен", owner_info]
            animals.to_csv("animals.csv", index=False, encoding="windows-1251")
            owner_win.destroy()
            self.reload_all()
            messagebox.showinfo("Успех", "Животное пристроено!")

        btn_canvas = tk.Canvas(frame, width=110, height=35, bg="#FFFFFF", highlightthickness=0)
        btn_canvas.create_oval(5, 5, 105, 30, fill=self.button_bg, outline=self.button_bg)
        btn_canvas.create_text(55, 17, text="Сохранить", fill=self.text_color, font=("Helvetica", 11))
        btn_canvas.bind("<Button-1>", lambda e: save_owner_info())
        btn_canvas.bind("<Enter>", lambda e: btn_canvas.itemconfig(1, fill=self.button_hover))
        btn_canvas.bind("<Leave>", lambda e: btn_canvas.itemconfig(1, fill=self.button_bg))
        btn_canvas.pack(pady=10)

    def move_to_dead(self, animal):
        # Создаем окно для ввода даты смерти
        death_win = tk.Toplevel(self.root)
        death_win.title(f"Смерть: {animal['Name']}")
        death_win.geometry("300x200")
        death_win.configure(bg=self.bg_color)

        frame = tk.Frame(death_win, bg="#FFFFFF", padx=20, pady=20)
        frame.pack(fill="both", expand=True, padx=15, pady=15)
        frame.config(highlightbackground=self.accent_color, highlightthickness=2)

        tk.Label(frame, text="Дата смерти:", bg="#FFFFFF", fg=self.text_color, font=("Helvetica", 12)).pack(pady=10)
        date_entry = tk.Entry(frame, font=("Helvetica", 11), bg="#FFFFFF", fg=self.text_color, relief="flat")
        date_entry.pack(pady=10)
        date_entry.config(highlightbackground=self.accent_color, highlightthickness=1)

        def save_death_date():
            death_date = date_entry.get()
            animals = pd.read_csv("animals.csv", encoding="windows-1251")
            animals.loc[animals["ID"] == animal["ID"], ["Status", "Death_Date"]] = ["Умер", death_date]
            animals.to_csv("animals.csv", index=False, encoding="windows-1251")
            death_win.destroy()
            self.reload_all()
            messagebox.showinfo("Успех", "Запись обновлена!")

        btn_canvas = tk.Canvas(frame, width=110, height=35, bg="#FFFFFF", highlightthickness=0)
        btn_canvas.create_oval(5, 5, 105, 30, fill=self.button_bg, outline=self.button_bg)
        btn_canvas.create_text(55, 17, text="Сохранить", fill=self.text_color, font=("Helvetica", 11))
        btn_canvas.bind("<Button-1>", lambda e: save_death_date())
        btn_canvas.bind("<Enter>", lambda e: btn_canvas.itemconfig(1, fill=self.button_hover))
        btn_canvas.bind("<Leave>", lambda e: btn_canvas.itemconfig(1, fill=self.button_bg))
        btn_canvas.pack(pady=10)

    def load_adopted_content(self):
        frame = tk.Frame(self.adopted_frame, bg="#FFFFFF")
        frame.pack(fill="both", expand=True, padx=15, pady=15)
        frame.config(highlightbackground=self.accent_color, highlightthickness=2)

        # Создаем Treeview с колонками
        self.adopted_tree = ttk.Treeview(frame, columns=("ID", "Name", "Type", "Breed", "Owner"), show="headings")
        self.adopted_tree.heading("ID", text="ID")
        self.adopted_tree.heading("Name", text="Имя")
        self.adopted_tree.heading("Type", text="Тип")
        self.adopted_tree.heading("Breed", text="Порода")
        self.adopted_tree.heading("Owner", text="Хозяин")
        self.adopted_tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Добавляем вертикальную прокрутку
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.adopted_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.adopted_tree.configure(yscrollcommand=scrollbar.set)

        # Заполняем таблицу данными
        animals = pd.read_csv("animals.csv", encoding="windows-1251")
        adopted = animals[animals["Status"] == "Пристроен"]
        for _, row in adopted.iterrows():
            owner_info = row["Owner_Info"][:30] + "..." if len(row["Owner_Info"]) > 30 else row["Owner_Info"]
            self.adopted_tree.insert("", "end", values=(row["ID"], row["Name"], row["Type"], row["Breed"], owner_info))

        # Кнопка для редактирования
        edit_btn = tk.Button(
            frame,
            text="Редактировать данные",
            command=self.edit_adopted_data,
            bg=self.button_bg,
            fg=self.text_color,
            font=("Helvetica", 10),
            relief="flat"
        )
        edit_btn.pack(pady=5)

    def edit_adopted_data(self):
        selected = self.adopted_tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите животное для редактирования!")
            return

        item = self.adopted_tree.item(selected[0])
        animal_id = item["values"][0]

        animals = pd.read_csv("animals.csv", encoding="windows-1251")
        animal = animals[animals["ID"] == animal_id].iloc[0]

        # Создаем окно редактирования
        edit_win = tk.Toplevel(self.root)
        edit_win.title(f"Редактирование: {animal['Name']}")
        edit_win.geometry("400x300")
        edit_win.configure(bg=self.bg_color)

        frame = tk.Frame(edit_win, bg="#FFFFFF", padx=20, pady=20)
        frame.pack(fill="both", expand=True, padx=15, pady=15)
        frame.config(highlightbackground=self.accent_color, highlightthickness=2)

        # Парсим информацию о хозяине
        owner_info = animal["Owner_Info"]
        name = owner_info.split("ФИО: ")[1].split(", Адрес:")[0] if "ФИО: " in owner_info else ""
        address = owner_info.split("Адрес: ")[1] if "Адрес: " in owner_info else ""

        tk.Label(frame, text="ФИО хозяина:", bg="#FFFFFF", fg=self.text_color, font=("Helvetica", 11)).pack(pady=5)
        name_entry = tk.Entry(frame, font=("Helvetica", 11), bg="#FFFFFF", fg=self.text_color, relief="flat")
        name_entry.insert(0, name)
        name_entry.pack(pady=5)
        name_entry.config(highlightbackground=self.accent_color, highlightthickness=1)

        tk.Label(frame, text="Адрес:", bg="#FFFFFF", fg=self.text_color, font=("Helvetica", 11)).pack(pady=5)
        address_entry = tk.Entry(frame, font=("Helvetica", 11), bg="#FFFFFF", fg=self.text_color, relief="flat")
        address_entry.insert(0, address)
        address_entry.pack(pady=5)
        address_entry.config(highlightbackground=self.accent_color, highlightthickness=1)

        def save_changes():
            new_owner_info = f"ФИО: {name_entry.get()}, Адрес: {address_entry.get()}"
            animals.loc[animals["ID"] == animal_id, "Owner_Info"] = new_owner_info
            animals.to_csv("animals.csv", index=False, encoding="windows-1251")
            edit_win.destroy()
            self.reload_all()
            messagebox.showinfo("Успех", "Данные обновлены!")

        btn_canvas = tk.Canvas(frame, width=110, height=35, bg="#FFFFFF", highlightthickness=0)
        btn_canvas.create_oval(5, 5, 105, 30, fill=self.button_bg, outline=self.button_bg)
        btn_canvas.create_text(55, 17, text="Сохранить", fill=self.text_color, font=("Helvetica", 11))
        btn_canvas.bind("<Button-1>", lambda e: save_changes())
        btn_canvas.bind("<Enter>", lambda e: btn_canvas.itemconfig(1, fill=self.button_hover))
        btn_canvas.bind("<Leave>", lambda e: btn_canvas.itemconfig(1, fill=self.button_bg))
        btn_canvas.pack(pady=10)

    def load_dead_content(self):
        frame = tk.Frame(self.dead_frame, bg="#FFFFFF")
        frame.pack(fill="both", expand=True, padx=15, pady=15)
        frame.config(highlightbackground=self.accent_color, highlightthickness=2)

        # Создаем Treeview с колонками
        self.dead_tree = ttk.Treeview(frame, columns=("ID", "Name", "Type", "Breed", "Death_Date"), show="headings")
        self.dead_tree.heading("ID", text="ID")
        self.dead_tree.heading("Name", text="Имя")
        self.dead_tree.heading("Type", text="Тип")
        self.dead_tree.heading("Breed", text="Порода")
        self.dead_tree.heading("Death_Date", text="Дата смерти")
        self.dead_tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Добавляем вертикальную прокрутку
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.dead_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.dead_tree.configure(yscrollcommand=scrollbar.set)

        # Заполняем таблицу данными
        animals = pd.read_csv("animals.csv", encoding="windows-1251")
        dead = animals[animals["Status"] == "Умер"]
        for _, row in dead.iterrows():
            self.dead_tree.insert("", "end",
                                  values=(row["ID"], row["Name"], row["Type"], row["Breed"], row["Death_Date"]))

        # Кнопка для редактирования
        edit_btn = tk.Button(
            frame,
            text="Редактировать дату смерти",
            command=self.edit_death_date,
            bg=self.button_bg,
            fg=self.text_color,
            font=("Helvetica", 10),
            relief="flat"
        )
        edit_btn.pack(pady=5)

    def edit_death_date(self):
        selected = self.dead_tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите животное для редактирования!")
            return

        item = self.dead_tree.item(selected[0])
        animal_id = item["values"][0]
        current_date = item["values"][4]

        animals = pd.read_csv("animals.csv", encoding="windows-1251")
        animal = animals[animals["ID"] == animal_id].iloc[0]

        # Создаем окно редактирования
        edit_win = tk.Toplevel(self.root)
        edit_win.title(f"Редактирование: {animal['Name']}")
        edit_win.geometry("300x200")
        edit_win.configure(bg=self.bg_color)

        frame = tk.Frame(edit_win, bg="#FFFFFF", padx=20, pady=20)
        frame.pack(fill="both", expand=True, padx=15, pady=15)
        frame.config(highlightbackground=self.accent_color, highlightthickness=2)

        tk.Label(frame, text="Дата смерти:", bg="#FFFFFF", fg=self.text_color, font=("Helvetica", 11)).pack(pady=5)
        date_entry = tk.Entry(frame, font=("Helvetica", 11), bg="#FFFFFF", fg=self.text_color, relief="flat")
        date_entry.insert(0, current_date)
        date_entry.pack(pady=5)
        date_entry.config(highlightbackground=self.accent_color, highlightthickness=1)

        def save_changes():
            new_date = date_entry.get()
            animals.loc[animals["ID"] == animal_id, "Death_Date"] = new_date
            animals.to_csv("animals.csv", index=False, encoding="windows-1251")
            edit_win.destroy()
            self.reload_all()
            messagebox.showinfo("Успех", "Дата смерти обновлена!")

        btn_canvas = tk.Canvas(frame, width=110, height=35, bg="#FFFFFF", highlightthickness=0)
        btn_canvas.create_oval(5, 5, 105, 30, fill=self.button_bg, outline=self.button_bg)
        btn_canvas.create_text(55, 17, text="Сохранить", fill=self.text_color, font=("Helvetica", 11))
        btn_canvas.bind("<Button-1>", lambda e: save_changes())
        btn_canvas.bind("<Enter>", lambda e: btn_canvas.itemconfig(1, fill=self.button_hover))
        btn_canvas.bind("<Leave>", lambda e: btn_canvas.itemconfig(1, fill=self.button_bg))
        btn_canvas.pack(pady=10)

    def add_photo(self, animal_id, photo_label, window):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        if file_path:
            img = Image.open(file_path).resize((200, 200))
            photo = ImageTk.PhotoImage(img)

            if photo_label:
                photo_label.configure(image=photo)
                photo_label.image = photo

            shutil.copy(file_path, f"animal_{animal_id}.png")
            self.reload_all()
            messagebox.showinfo("Успех", "Фото добавлено!")

    def reload_all(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        for widget in self.adopted_frame.winfo_children():
            widget.destroy()
        for widget in self.dead_frame.winfo_children():
            widget.destroy()
        self.load_main_content()
        self.load_adopted_content()
        self.load_dead_content()


if __name__ == "__main__":
    root = tk.Tk()
    app = NurseryApp(root)
    root.mainloop()