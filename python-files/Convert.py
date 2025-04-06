import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import re
import os
import threading
from time import sleep

class TextLineNumbers(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None

    def attach(self, text_widget):
        self.textwidget = text_widget

    def redraw(self, *args):
        self.delete("all")
        i = self.textwidget.index("@0,0")
        while True:
            dline = self.textwidget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(2, y, anchor="nw", text=linenum, fill="grey")
            i = self.textwidget.index("%s+1line" % i)

class LogViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Log Viewer")

        self.status_label = tk.Label(root, text="Status: Ready")
        self.status_label.grid(row=0, column=0, sticky="ew")

        # Label to display the name of the loaded log file
        self.log_file_label = tk.Label(root, text=" Loaded File: None", font=("Helvetica", 25), anchor='w')
        self.log_file_label.grid(row=1, column=0, sticky="ew")

        # Paned window for log text and search results
        self.paned_window = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.paned_window.grid(row=2, column=0, sticky="nsew")

        # Frame for the file explorer
        self.explorer_frame = tk.Frame(self.paned_window)
        self.paned_window.add(self.explorer_frame, weight=1)

        self.explorer_label = tk.Label(self.explorer_frame, text="Log Files:")
        self.explorer_label.grid(row=0, column=0, sticky="ew")

        # Filter entry widget
        self.filter_entry = tk.Entry(self.explorer_frame)
        self.filter_entry.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.filter_entry.bind("<KeyRelease>", self.filter_log_files)

        # Adding a vertical scrollbar to the Treeview
        self.explorer_tree_scrollbar = ttk.Scrollbar(self.explorer_frame, orient="vertical")
        self.explorer_tree_scrollbar.grid(row=2, column=1, sticky="ns")

        self.explorer_tree = ttk.Treeview(self.explorer_frame, yscrollcommand=self.explorer_tree_scrollbar.set)
        self.explorer_tree.grid(row=2, column=0, sticky="nsew")
        self.explorer_tree_scrollbar.config(command=self.explorer_tree.yview)

        self.explorer_tree.bind("<<TreeviewSelect>>", self.on_explorer_select)

        # Button to select log folder
        self.select_folder_button = tk.Button(self.explorer_frame, text="Select Log Folder", command=self.set_log_folder)
        self.select_folder_button.grid(row=3, column=0, sticky="ew")

        self.text_frame = tk.Frame(self.paned_window)
        self.paned_window.add(self.text_frame, weight=3)

        self.line_numbers = TextLineNumbers(self.text_frame, width=50)  # Increased width
        self.line_numbers.grid(row=0, column=0, sticky="ns")

        # Ensure the log_text widget is configured for normal selection
        self.log_text = tk.Text(self.text_frame, wrap='none', undo=True, exportselection=True)
        self.log_text.grid(row=0, column=1, sticky="nsew")
        self.log_text.bind("<KeyRelease>", self.update_line_numbers)
        self.log_text.bind("<MouseWheel>", self.update_line_numbers)

        self.add_context_menu(self.log_text)

        # Ensure the log_text widget allows normal text selection
        self.log_text.config(cursor="xterm", insertwidth=1, insertofftime=300, insertontime=600)

        # Ensure scrollbars are configured correctly
        self.scrollbar_v = ttk.Scrollbar(self.text_frame, orient="vertical", command=self.log_text.yview)
        self.scrollbar_v.grid(row=0, column=2, sticky="ns")
        self.log_text.config(yscrollcommand=self.scrollbar_v.set)

        self.scrollbar_h = ttk.Scrollbar(self.text_frame, orient="horizontal", command=self.log_text.xview)
        self.scrollbar_h.grid(row=1, column=0, columnspan=3, sticky="ew")
        self.log_text.config(xscrollcommand=self.scrollbar_h.set)

        # Apply style to scrollbars to make them semi-transparent
        style = ttk.Style()
        style.configure("Vertical.TScrollbar", background="#f0f0f0", troughcolor="#f0f0f0", relief="flat")
        style.map("Vertical.TScrollbar",
                  background=[('active', '#e0e0e0')],
                  troughcolor=[('active', '#e0e0e0')],
                  relief=[('active', 'groove')])
        style.configure("Horizontal.TScrollbar", background="#f0f0f0", troughcolor="#f0f0f0", relief="flat")
        style.map("Horizontal.TScrollbar",
                  background=[('active', '#e0e0e0')],
                  troughcolor=[('active', '#e0e0e0')],
                  relief=[('active', 'groove')])

        # Frame for search results with a scrollbar
        self.search_result_frame = tk.Frame(self.paned_window)
        self.paned_window.add(self.search_result_frame, weight=1)

        self.search_result_text = tk.Listbox(self.search_result_frame, width=40, height=10)
        self.search_result_text.grid(row=0, column=0, sticky="nsew")
        self.search_result_text.bind("<<ListboxSelect>>", self.on_search_result_click)
        self.add_context_menu(self.search_result_text)

        # Adding a vertical scrollbar to the search_result_text widget
        self.search_result_scrollbar_v = ttk.Scrollbar(self.search_result_frame, orient="vertical", command=self.search_result_text.yview)
        self.search_result_scrollbar_v.grid(row=0, column=1, sticky="ns")
        self.search_result_text.config(yscrollcommand=self.search_result_scrollbar_v.set)

        # Adding a horizontal scrollbar to the search_result_text widget
        self.search_result_scrollbar_h = ttk.Scrollbar(self.search_result_frame, orient="horizontal", command=self.search_result_text.xview)
        self.search_result_scrollbar_h.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.search_result_text.config(xscrollcommand=self.search_result_scrollbar_h.set)

        # Configure grid weights for proper resizing
        self.text_frame.grid_rowconfigure(0, weight=1)
        self.text_frame.grid_columnconfigure(1, weight=1)
        self.search_result_frame.grid_rowconfigure(0, weight=1)
        self.search_result_frame.grid_columnconfigure(0, weight=1)
        self.explorer_frame.grid_rowconfigure(2, weight=1)
        self.explorer_frame.grid_columnconfigure(0, weight=1)

        button_frame = tk.Frame(root)
        button_frame.grid(row=3, column=0, sticky="ew")

        self.load_log_button = tk.Button(button_frame, text="Load Log", command=self.load_log)
        self.load_log_button.grid(row=0, column=0, padx=10, pady=10)

        self.load_excel_button = tk.Button(button_frame, text="Load Excel", command=self.load_excel)
        self.load_excel_button.grid(row=0, column=1, padx=10, pady=10)

        self.search_label = tk.Label(button_frame, text="Search:")
        self.search_label.grid(row=0, column=2, padx=5)

        self.search_entry = tk.Entry(button_frame, width=50)
        self.search_entry.grid(row=0, column=3, padx=5)
        self.add_context_menu(self.search_entry)

        self.search_button = tk.Button(button_frame, text="Search", command=self.search_log)
        self.search_button.grid(row=0, column=4, padx=5)

        self.copy_button = tk.Button(button_frame, text="Copy", command=self.copy_selected_text)
        self.copy_button.grid(row=0, column=5, padx=5)

        self.search_selected_button = tk.Button(button_frame, text="Search Selected", command=self.search_selected_text)
        self.search_selected_button.grid(row=0, column=6, padx=5)

        # Toggle button for Excel data
        self.toggle_excel_button = tk.Button(button_frame, text="On/Off Excel Data", command=self.toggle_excel_data)
        self.toggle_excel_button.grid(row=0, column=7, padx=10, pady=10)

        self.goods_data = None
        self.raw_log_content = ""
        self.transformed_log_content = ""
        self.highlighted_line = None
        self.log_folder_path = ""
        self.use_excel_data = False  # State variable to track if Excel data is used
        self.existing_files = set()  # Set to track existing files

        self.line_numbers.attach(self.log_text)

        # Start polling for new log files
        self.polling_thread = threading.Thread(target=self.poll_log_files)
        self.polling_thread.daemon = True
        self.polling_thread.start()

        # Configure the root window to resize properly
        root.grid_rowconfigure(2, weight=1)
        root.grid_columnconfigure(0, weight=1)

    def auto_scroll(self, event=None):
        # Remove or modify this method if you want to disable auto-scrolling
        pass

    def update_line_numbers(self, event=None):
        self.line_numbers.redraw()

    def add_context_menu(self, widget):
        menu = tk.Menu(widget, tearoff=0)
        menu.add_command(label="Cut", command=lambda: widget.event_generate("<<Cut>>"))
        menu.add_command(label="Copy", command=lambda: widget.event_generate("<<Copy>>"))
        menu.add_command(label="Paste", command=lambda: widget.event_generate("<<Paste>>"))
        menu.add_command(label="Select All", command=lambda: widget.event_generate("<<SelectAll>>"))

        def show_menu(event):
            menu.tk_popup(event.x_root, event.y_root)

        widget.bind("<Button-3>", show_menu)

    def load_log(self):
        log_file_path = filedialog.askopenfilename(filetypes=[("Log files", "*.log"), ("All files", "*.*")])
        if log_file_path:
            self.status_label.config(text="Status: Loading Log...")
            self.root.update_idletasks()
            try:
                with open(log_file_path, 'r', encoding='utf-8') as log_file:
                    self.raw_log_content = log_file.read()
                    self.display_log_content()
                self.status_label.config(text="Status: Log Loaded Successfully")
                self.log_file_label.config(text=f"Loaded Log File: {os.path.basename(log_file_path)}")
            except Exception as e:
                self.status_label.config(text=f"Status: Failed to Load Log - {str(e)}")

    def display_log_content(self):
        # Store the current scroll position
        current_yview = self.log_text.yview()
        current_xview = self.log_text.xview()

        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        if self.use_excel_data and self.goods_data is not None:
            self.transformed_log_content = self.transform_log_content(self.raw_log_content)
            log_content = self.transformed_log_content
        else:
            log_content = self.raw_log_content
        self.log_text.insert(tk.END, log_content)
        self.update_line_numbers()
        self.log_text.config(state=tk.DISABLED)

        # Restore the scroll position
        self.log_text.yview_moveto(current_yview[0])
        self.log_text.xview_moveto(current_xview[0])

    def toggle_excel_data(self):
        self.use_excel_data = not self.use_excel_data
        self.display_log_content()
        self.status_label.config(text="Status: Toggled Excel Data View" if self.use_excel_data else "Status: Excel Data View Off")

    def load_excel(self):
        excel_file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
        if excel_file_path:
            self.status_label.config(text="Status: Loading Excel...")
            self.root.update_idletasks()
            try:
                self.goods_data = pd.read_excel(excel_file_path)
                messagebox.showinfo("Excel Loaded", "Excel data loaded successfully.")
                self.status_label.config(text="Status: Excel Loaded Successfully")
                if self.raw_log_content:
                    self.transformed_log_content = self.transform_log_content(self.raw_log_content)
                    self.display_log_content()
            except Exception as e:
                self.status_label.config(text=f"Status: Failed to Load Excel - {str(e)}")

    def transform_log_content(self, log_content):
        # Parse the log and transform it into a readable format
        lines = log_content.splitlines()
        transformed_log = []

        site_codes = {
            10: "Сайт 366.ru",
            4: "Сайт ГорЗдрав",
            13: "Мобильное приложение 36,6",
            14: "Мобильное приложение ГОРЗДРАВ",
            81: "Сайт ЛОТ",
            82: "МП ЛОТ",
            96: "ЛОТ Оптика",
            95: "Мир сити 366",
            94: "Мир сити Горздрав",
            93: "Яндекс самовывоз 366",
            92: "Яндекс самовывоз Горздрав",
            91: "ЯндексDBS (Пульс)",
            90: "Сбермегамаркет (Пульс)",
            89: "Озон RFBS (Пульс)",
            88: "АСНА",
            87: "АптекаЭконом (Пульс)",
            86: "АптекаФорте (Пульс)",
            85: "009.рф",
            84: "ЛОТ Мегаптека",
            83: "ЛОТ Ютека",
            78: "ЛекОптТорг 36,6",
            77: "ЛекОптТорг Горздрав",
            76: "Склад Здоровья 366",
            75: "Склад Здоровья Горздрав",
            74: "Меди 366",
            73: "Меди Горздрав",
            72: "ЦеныВаптеках Горздрав",
            71: "ЦеныВаптеках 366",
            70: "Ютека склад ГЗ",
            69: "Ютека склад 366",
            68: "Эксперо Горздрав",
            67: "Эксперо 366",
            66: "АптекаМос 366",
            65: "Яндекс еда Горздрав (самовывоз)",
            64: "Яндекс еда 366 (самовывоз)",
            63: "POLZAru",
            62: "БлижайшаяАптекаРФ 366",
            61: "БлижайшаяАптекаРФ Горздрав",
            60: "009 Фамрлинк 366",
            59: "Яндекс Еда 366",
            58: "Яндекс Еда Горздрав",
            57: "Яндекс ФБС Горздрав",
            56: "Яндекс ДБС 36,6",
            55: "366 МП: Деливери (Доставка)",
            54: "Горздрав МП: Деливери (Доставка)",
            53: "366: Деливери (Доставка)",
            52: "Горздрав: Деливери (Доставка)",
            51: "ZdravCity.ru",
            50: "Приложение 36.6 (Доставка)",
            49: "366: Яндекс.Доставка (Доставка)",
            48: "Горздрав: Яндекс.Доставка (Доставка)",
            47: "366: Геттакси (Доставка)",
            46: "Горздрав: Геттакси (Доставка)",
            45: "366: Чекбокс (Доставка)",
            44: "Горздрав: Чекбокс (Доставка)",
            43: "366: Даллиэкспресс (Доставка)",
            42: "Горздрав: Даллиэкспресс (Доставка)",
            41: "АптекаМос Горздрав",
            40: "СберМаркет ГОРЗДРАВ",
            39: "Деливери Клаб ГОРЗДРАВ",
            38: "ЯндексМаркет Экспресс ДБС ГОРЗДРАВ",
            37: "СберМаркет 36,6",
            36: "Деливери Клаб 36,6",
            35: "ЯндексМаркет Экспресс ФБС 36,6",
            34: "Apteka.ru",
            33: "newpharma Бронирование 36.6",
            32: "newpharma Бронирование Горздрав",
            31: "newpharma Интернет заказ",
            28: "goods_gorzdrav",
            27: "goods_apt366",
            26: "Достависта интернет-заказ",
            25: "Достависта бронирование в 36.6",
            24: "Достависта бронирования в Горздрав",
            23: "Мегаптека Бронирование Горздрав",
            22: "Мегаптека Бронирование 36.6",
            21: "009 Фамрлинк Горздрав",
            20: "Ютека (Бронирование Гордрав)",
            19: "Ютека (Бронирование 36.6)",
            18: "Ютека (Интернет-заказы)",
            17: "Росфарма (Бронирования)",
            16: "vseapteki.ru (на ГЗ)",
            15: "vseapteki.ru (на 36,6)",
            12: "docplus",
            11: "www.hybris.ru",
            9: "OZON",
            8: "Тест",
            7: "www.ozon.ru",
            6: "Семейный доктор",
            5: "ЛекОпт",
            3: "MED03 (Стар и млад)",
            2: "www.366.ru",
            1: "Личный кабинет АВЕ"
        }

        card_levels = {
            0: "0 - Уровень не указан",
            1: "1 - White/Серебро",
            2: "2 - Green/Золото",
            3: "3 - Blue/Платина",
            4: "4 - Black",
            101: "101 - White",
            102: "102 - Gold"
        }

        card_prefixes = {
            "300": "ГОРЗДРАВ",
            "366": "36.6",
            "315": "Калина Фарм",
            "801": "ЛОТ",
            "780": "ЛОТ",
            "350": "ЛОТ"
        }

        for i, line in enumerate(lines):
            if '<art>' in line:
                time = lines[i - 1].split()[0]
                art = line.split('<art>')[1].split('</art>')[0]
                label = self.get_label_by_art(art)
                transformed_log.append(f"{line} // {label}")
            else:
                # Adding comments based on specified tags
                if '<tag>' in line:
                    tags = line.split('<tag>')[1].split('</tag>')[0].split(',')
                    comments = []
                    for tag in tags:
                        if tag == 'vip':
                            comments.append("vip – владелец вип карты")
                        elif tag == 'pensioner':
                            comments.append("pensioner - пенсионер")
                        elif tag == 'staff':
                            comments.append("staff – сотрудник аптечной сети")
                    transformed_log.append(f"{line}  // {', '.join(comments)}")
                elif '<cardLevel>' in line:
                    cardlevel_str = line.split('<cardLevel>')[1].split('</cardLevel>')[0]

                    try:
                        cardlevel = int(cardlevel_str)
                        level_comment = card_levels.get(cardlevel, "Неизвестный уровень карты")
                        transformed_log.append(f"{line}  // {level_comment}")
                    except ValueError:
                        transformed_log.append(line)
                elif '<type>' in line:
                    types = line.split('<type>')[1].split('</type>')[0]
                    comments = []
                    if 'L' in types:
                        comments.append("L - товар из списка ЖНВЛП")
                    if 'I' in types:
                        comments.append("I - товар интернет-заказа")
                    if 'B' in types:
                        comments.append("B – товар интернет-бронирования")
                    if 'F' in types:
                        comments.append("F - любимый товар")
                    transformed_log.append(f"{line}  // {', '.join(comments)}")
                elif '<site>' in line:
                    site_str = line.split('<site>')[1].split('</site>')[0]
                    try:
                        site = int(site_str)
                        site_name = site_codes.get(site, "Неизвестный сайт")
                        transformed_log.append(f"{line}  // {site_name}")
                    except ValueError:
                        transformed_log.append(line)
                elif '<card>' in line:
                    card_str = line.split('<card>')[1].split('</card>')[0]
                    prefix = card_str[:3]
                    card_comment = card_prefixes.get(prefix, "Неизвестный префикс карты")
                    transformed_log.append(f"{line}  // Карта {card_comment}")
                elif '<qty>' in line:
                    qty_str = line.split('<qty>')[1].split('</qty>')[0]
                    try:
                        qty = int(qty_str)
                        price_line = next((l for l in lines[i:] if '<price>' in l), None)
                        base_price_line = next((l for l in lines[i:] if '<basePrice>' in l), None)

                        if price_line or base_price_line:
                            price_str = price_line.split('<price>')[1].split('</price>')[0]
                            base_price = base_price_line.split('<basePrice>')[1].split('</basePrice>')[0]
                            price = float(price_str)
                            total_price = price * qty
                            total_base_price = float(base_price) * qty
                            if float(base_price) != price:
                                transformed_log.append(f"{line}  // Количество: {qty}, Цена со скидкой: {total_price:.2f}, без скидки: {total_base_price:.2f}")
                            else:
                                transformed_log.append(f"{line}  // Количество: {qty}, Цена: {total_base_price:.2f}")
                        else:
                            transformed_log.append(line)
                    except (ValueError, IndexError):
                        transformed_log.append(line)
                else:
                    transformed_log.append(line)

        return "\n".join(transformed_log)

    def get_label_by_art(self, art):
        if self.goods_data is not None:
            try:
                row = self.goods_data[self.goods_data['good_id'] == int(art)]
                if not row.empty:
                    return row.iloc[0]['label']
            except ValueError:
                pass
        return "Unknown"

    def search_log(self):
        search_term = self.search_entry.get()
        if not search_term:
            messagebox.showwarning("No Search Term", "Please enter a search term.")
            return

        self.search_result_text.delete(0, tk.END)
        lines = self.transformed_log_content.splitlines() if self.use_excel_data else self.raw_log_content.splitlines()
        search_term = search_term.lower()
        pattern = re.compile(re.escape(search_term), re.IGNORECASE)

        for i, line in enumerate(lines):
            if pattern.search(line):
                self.search_result_text.insert(tk.END, f"{i + 1}: {line}")

        self.status_label.config(text=f"Status: Found {self.search_result_text.size()} occurrences")

    def on_search_result_click(self, event):
        selected = self.search_result_text.curselection()
        if selected:
            line_text = self.search_result_text.get(selected[0])
            line_number = int(line_text.split()[0].strip(':'))
            self.go_to_line(line_number)

    def go_to_line(self, line_number):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.mark_set(tk.INSERT, f"{line_number}.0")
        self.log_text.see(f"{line_number}.0")

        # Clear previous highlight
        if self.highlighted_line:
            self.log_text.tag_delete(self.highlighted_line)

        # Highlight the new line
        self.highlighted_line = f"highlight_{line_number}"
        self.log_text.tag_add(self.highlighted_line, f"{line_number}.0", f"{line_number}.end")
        self.log_text.tag_config(self.highlighted_line, background="yellow", foreground="black")
        self.log_text.config(state=tk.DISABLED)

    def copy_selected_text(self):
        try:
            selected_text = self.log_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
            self.status_label.config(text="Status: Text Copied to Clipboard")
        except tk.TclError:
            self.status_label.config(text="Status: No Text Selected")

    def search_selected_text(self):
        try:
            selected_text = self.log_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, selected_text)
            self.search_log()
        except tk.TclError:
            self.status_label.config(text="Status: No Text Selected")

    def set_log_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.log_folder_path = folder_path
            self.load_log_files()

    def load_log_files(self):
        if not self.log_folder_path:
            return

        # Clear existing items in the Treeview
        for item in self.explorer_tree.get_children():
            self.explorer_tree.delete(item)

        # Track existing files
        self.existing_files = set(os.listdir(self.log_folder_path))

        for file_name in self.existing_files:
            if file_name.endswith(".log"):
                self.explorer_tree.insert("", "end", text=file_name, values=(os.path.join(self.log_folder_path, file_name),))

    def filter_log_files(self, event=None):
        filter_text = self.filter_entry.get().lower()
        if not filter_text:
            # Reset filter and show all files
            self.explorer_tree.delete(*self.explorer_tree.get_children())
            for file_name in self.existing_files:
                if file_name.endswith(".log"):
                    self.explorer_tree.insert("", "end", text=file_name, values=(os.path.join(self.log_folder_path, file_name),))
        else:
            self.explorer_tree.delete(*self.explorer_tree.get_children())
            for file_name in self.existing_files:
                if file_name.endswith(".log") and filter_text in file_name.lower():
                    self.explorer_tree.insert("", "end", text=file_name, values=(os.path.join(self.log_folder_path, file_name),))

    def poll_log_files(self):
        while True:
            if self.log_folder_path:
                current_files = set(os.listdir(self.log_folder_path))
                new_files = current_files - self.existing_files
                if new_files:
                    for file_name in new_files:
                        if file_name.endswith(".log"):
                            self.explorer_tree.insert("", "end", text=file_name, values=(os.path.join(self.log_folder_path, file_name),))
                    self.existing_files = current_files
            sleep(1)

    def on_explorer_select(self, event):
        selected_items = self.explorer_tree.selection()
        if selected_items:
            selected_item = selected_items[0]
            file_path = self.explorer_tree.item(selected_item, "values")[0]
            self.load_log_from_path(file_path)
            self.search_result_text.delete(0, tk.END)  # Clear search results
        else:
            self.status_label.config(text="Status: No File Selected")

    def load_log_from_path(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as log_file:
                self.raw_log_content = log_file.read()
                self.display_log_content()
            self.status_label.config(text="Status: Log Loaded Successfully")
            self.log_file_label.config(text=f" Loaded File: {os.path.basename(file_path)}")
        except Exception as e:
            self.status_label.config(text=f"Status: Failed to Load Log - {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LogViewerApp(root)
    root.mainloop()
