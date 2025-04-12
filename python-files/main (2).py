import sys
import sqlite3
import csv
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHBoxLayout, QLineEdit, QLabel, QComboBox, QDialog, 
                             QFormLayout, QDialogButtonBox, QMessageBox, QSpinBox, QInputDialog, QFileDialog, QTabWidget)
from PyQt5.QtCore import Qt
import os
from datetime import datetime
import uuid
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtGui import QIcon
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from jinja2 import Environment, FileSystemLoader

DB_NAME = "forsunki.db"
print("[LOG] Импорт завершён")

class BatchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавить партию форсунок")
        self.layout = QFormLayout(self)

        self.model_input = QLineEdit()
        self.count_input = QSpinBox()
        self.count_input.setRange(1, 100)
        self.buy_price_input = QLineEdit()
        self.sell_price_input = QLineEdit()

        self.layout.addRow("Марка/модель:", self.model_input)
        self.layout.addRow("Количество:", self.count_input)
        self.layout.addRow("Цена закупки (за 1 шт):", self.buy_price_input)
        self.layout.addRow("Цена продажи (за 1 шт):", self.sell_price_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def get_data(self):
        return (
            self.model_input.text(),
            self.count_input.value(),
            float(self.buy_price_input.text()) if self.buy_price_input.text() else 0.0,
            float(self.sell_price_input.text()) if self.sell_price_input.text() else 0.0
        )

class AddDialog(QDialog):
    def __init__(self, data=None):
        super().__init__()
        print("[LOG] Открыт диалог добавления/редактирования")
        self.setWindowTitle("Добавить/Редактировать форсунку")
        self.layout = QFormLayout(self)

        self.model_input = QLineEdit()
        self.status_input = QComboBox()
        self.status_input.addItems(["грязная", "чистится", "готова", "продана"])
        self.date_input = QLineEdit(datetime.now().strftime("%Y-%m-%d"))
        self.buy_price_input = QLineEdit()
        self.sell_price_input = QLineEdit()

        self.layout.addRow("Марка/модель:", self.model_input)
        self.layout.addRow("Состояние:", self.status_input)
        self.layout.addRow("Дата поступления:", self.date_input)
        self.layout.addRow("Цена закупки:", self.buy_price_input)
        self.layout.addRow("Цена продажи:", self.sell_price_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

        if data:
            self.model_input.setText(data[1])
            self.status_input.setCurrentText(data[2])
            self.date_input.setText(data[3])
            self.buy_price_input.setText(str(data[4]))
            self.sell_price_input.setText(str(data[5]))
            self.id = data[0]
        else:
            self.id = None

    def get_data(self):
        return (
            self.id,
            self.model_input.text(),
            self.status_input.currentText(),
            self.date_input.text(),
            float(self.buy_price_input.text()) if self.buy_price_input.text() else 0.0,
            float(self.sell_price_input.text()) if self.sell_price_input.text() else 0.0
        )

class PlotWindow(QWidget):
    def __init__(self, data):
        super().__init__()
        self.setWindowTitle("Графики форсунок")
        self.layout = QVBoxLayout(self)
        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.layout.addWidget(self.canvas)
        self.plot(data)

    def plot(self, data):
        ax = self.canvas.figure.subplots()
        models = [d[1] for d in data]
        counts = [d[4] for d in data]
        ax.bar(models, counts)
        ax.set_title("Количество форсунок по моделям")
        ax.set_xlabel("Модель")
        ax.set_ylabel("Количество")

class WebsiteManager(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        
        self.generate_button = QPushButton("Сгенерировать HTML")
        self.upload_button = QPushButton("Загрузить на сервер")
        self.status_label = QLabel("Статус: Ожидание")

        self.layout.addWidget(self.generate_button)
        self.layout.addWidget(self.upload_button)
        self.layout.addWidget(self.status_label)

        self.generate_button.clicked.connect(self.generate_html)
        self.upload_button.clicked.connect(self.upload_to_server)

    def generate_html(self):
        # Генерация HTML
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('product_template.html')

        conn = sqlite3.connect('forsunki.db')
        cursor = conn.cursor()
        cursor.execute("SELECT kit_code, shelf_section, injector_ids FROM kits")
        kits = cursor.fetchall()

        for kit in kits:
            kit_code, shelf_section, injector_ids = kit
            data = {
                'kit_code': kit_code,
                'shelf_section': shelf_section,
                'injector_ids': injector_ids.split(',')
            }
            output = template.render(data=data)
            with open(f'site/products/{kit_code}.html', 'w', encoding='utf-8') as f:
                f.write(output)

        conn.close()
        self.status_label.setText("Статус: HTML сгенерирован")

    def upload_to_server(self):
        # Загрузка файлов на сервер
        # Здесь будет код для загрузки через FTP или SFTP
        self.status_label.setText("Статус: Файлы загружены")

class InjectorApp(QWidget):
    def __init__(self):
        super().__init__()
        print("[LOG] GUI запускается")
        self.setWindowTitle("Учёт форсунок")
        self.resize(900, 600)
        self.layout = QVBoxLayout(self)

        self.tabs = QTabWidget(self)
        self.website_manager = WebsiteManager()
        self.tabs.addTab(self.website_manager, "Управление сайтом")

        self.search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по модели, состоянию или дате...")
        self.search_btn = QPushButton("Поиск")
        self.search_btn.clicked.connect(self.search_records)
        self.status_filter = QComboBox()
        self.status_filter.addItem("Все")
        self.status_filter.addItems(["грязная", "чистится", "готова", "продана"])
        self.status_filter.currentTextChanged.connect(self.filter_by_status)

        self.search_layout.addWidget(self.search_input)
        self.search_layout.addWidget(self.search_btn)
        self.search_layout.addWidget(QLabel("Фильтр по статусу:"))
        self.search_layout.addWidget(self.status_filter)
        self.layout.addLayout(self.search_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Марка/модель", "Состояние", "Дата поступления", "Цена закупки", "Цена продажи", "Прибыль", "Код партии"])
        self.table.setSortingEnabled(True)
        self.table.cellDoubleClicked.connect(self.change_status_inline)
        self.layout.addWidget(self.table)

        self.button_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить форсунку")
        self.add_batch_btn = QPushButton("Добавить партию")
        self.edit_btn = QPushButton("Редактировать")
        self.delete_btn = QPushButton("Удалить")
        self.export_btn = QPushButton("Экспорт в CSV")
        self.stats_btn = QPushButton("Показать аналитику")
        self.plot_btn = QPushButton("Показать графики")
        self.financial_btn = QPushButton("Финансовая аналитика")
        self.create_kit_btn = QPushButton("Создать комплект")

        self.button_layout.addWidget(self.add_btn)
        self.button_layout.addWidget(self.add_batch_btn)
        self.button_layout.addWidget(self.edit_btn)
        self.button_layout.addWidget(self.delete_btn)
        self.button_layout.addWidget(self.export_btn)
        self.button_layout.addWidget(self.stats_btn)
        self.button_layout.addWidget(self.plot_btn)
        self.button_layout.addWidget(self.financial_btn)
        self.button_layout.addWidget(self.create_kit_btn)
        self.layout.addLayout(self.button_layout)

        self.add_btn.clicked.connect(self.open_add_dialog)
        self.add_batch_btn.clicked.connect(self.open_add_batch_dialog)
        self.edit_btn.clicked.connect(self.edit_record)
        self.delete_btn.clicked.connect(self.delete_record)
        self.export_btn.clicked.connect(self.export_to_csv)
        self.stats_btn.clicked.connect(self.show_stats)
        self.plot_btn.clicked.connect(self.show_plots)
        self.financial_btn.clicked.connect(self.show_financial_analytics)
        self.create_kit_btn.clicked.connect(self.open_create_kit_dialog)

        self.add_btn.setIcon(QIcon('icons/add.png'))
        self.add_batch_btn.setIcon(QIcon('icons/add_batch.png'))
        self.edit_btn.setIcon(QIcon('icons/edit.png'))
        self.delete_btn.setIcon(QIcon('icons/delete.png'))
        self.export_btn.setIcon(QIcon('icons/export.png'))
        self.stats_btn.setIcon(QIcon('icons/stats.png'))
        self.plot_btn.setIcon(QIcon('icons/plot.png'))
        self.financial_btn.setIcon(QIcon('icons/financial.png'))
        self.create_kit_btn.setIcon(QIcon('icons/create_kit.png'))

        self.setStyleSheet('''
            QPushButton {
                font-size: 14px;
                padding: 10px;
            }
            QTableWidget {
                font-size: 12px;
            }
        ''')

        self.stock_label = QLabel("Текущий запас: 0")
        self.layout.addWidget(self.stock_label)

        self.status_counts_layout = QHBoxLayout()
        self.dirty_count_label = QLabel("Грязные: 0")
        self.cleaning_count_label = QLabel("Чистятся: 0")
        self.ready_count_label = QLabel("Готовы: 0")
        self.sold_count_label = QLabel("Проданы: 0")

        self.status_counts_layout.addWidget(self.dirty_count_label)
        self.status_counts_layout.addWidget(self.cleaning_count_label)
        self.status_counts_layout.addWidget(self.ready_count_label)
        self.status_counts_layout.addWidget(self.sold_count_label)
        self.layout.addLayout(self.status_counts_layout)

        self.init_db()
        self.load_data()

        self.tabs.addTab(self, "Учёт форсунок")
        self.setLayout(self.layout)

    def init_db(self):
        print("[LOG] Инициализация базы данных")
        self.conn = sqlite3.connect(DB_NAME)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS forsunki (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model TEXT,
            status TEXT,
            date_in TEXT,
            buy_price REAL,
            sell_price REAL,
            batch_code TEXT
        )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            injector_id INTEGER,
            change_type TEXT,
            change_date TEXT,
            details TEXT,
            FOREIGN KEY(injector_id) REFERENCES forsunki(id)
        )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS kits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kit_code TEXT,
            shelf_section TEXT,
            injector_ids TEXT
        )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS kit_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kit_id INTEGER,
            file_path TEXT,
            FOREIGN KEY(kit_id) REFERENCES kits(id)
        )''')
        self.conn.commit()

    def load_data(self, filter_query=None, status_filter=None):
        print(f"[LOG] Загрузка данных, фильтр: {filter_query}, статус: {status_filter}")
        self.table.setRowCount(0)
        query = "SELECT * FROM forsunki"
        params = []

        if filter_query or (status_filter and status_filter != "Все"):
            conditions = []
            if filter_query:
                conditions.append("(model LIKE ? OR status LIKE ? OR date_in LIKE ? OR batch_code LIKE ?)")
                like_query = f"%{filter_query}%"
                params.extend([like_query, like_query, like_query, like_query])
            if status_filter and status_filter != "Все":
                conditions.append("status = ?")
                params.append(status_filter)
            query += " WHERE " + " AND ".join(conditions)

        self.cursor.execute(query, params)

        for row_data in self.cursor.fetchall():
            row_number = self.table.rowCount()
            self.table.insertRow(row_number)
            profit = row_data[5] - row_data[4]
            for column_number, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                if column_number == 2:
                    self.color_status_cell(item)
                self.table.setItem(row_number, column_number, item)
            profit_item = QTableWidgetItem(f"{profit:.2f}")
            self.table.setItem(row_number, 6, profit_item)

        self.cursor.execute("SELECT SUM(buy_price) FROM forsunki")
        total_stock = self.cursor.fetchone()[0] or 0
        self.stock_label.setText(f"Текущий запас: {total_stock}")

        self.cursor.execute("SELECT status, COUNT(*) FROM forsunki GROUP BY status")
        status_counts = {"грязная": 0, "чистится": 0, "готова": 0, "продана": 0}
        for status, count in self.cursor.fetchall():
            status_counts[status] = count

        self.dirty_count_label.setText(f"Грязные: {status_counts['грязная']}")
        self.cleaning_count_label.setText(f"Чистятся: {status_counts['чистится']}")
        self.ready_count_label.setText(f"Готовы: {status_counts['готова']}")
        self.sold_count_label.setText(f"Проданы: {status_counts['продана']}")

        if status_counts['грязная'] > 0:
            QMessageBox.warning(self, "Внимание", f"У вас есть {status_counts['грязная']} грязных форсунок, которые требуют обработки.")

    def color_status_cell(self, item):
        status = item.text()
        if status == "грязная":
            item.setBackground(Qt.red)
        elif status == "чистится":
            item.setBackground(Qt.yellow)
        elif status == "готова":
            item.setBackground(Qt.green)
        elif status == "продана":
            item.setBackground(Qt.gray)

    def change_status_inline(self, row, column):
        if column == 2:
            current_status = self.table.item(row, column).text()
            combo = QComboBox()
            combo.addItems(["грязная", "чистится", "готова", "продана"])
            combo.setCurrentText(current_status)
            self.table.setCellWidget(row, column, combo)
            combo.activated.connect(lambda: self.save_inline_status(row, combo))

    def save_inline_status(self, row, combo):
        new_status = combo.currentText()
        id_item = self.table.item(row, 0)
        if id_item:
            id = int(id_item.text())
            self.cursor.execute("UPDATE forsunki SET status=? WHERE id=?", (new_status, id))
            self.conn.commit()
            self.load_data()

    def search_records(self):
        print("[LOG] Поиск записей")
        text = self.search_input.text().strip()
        status = self.status_filter.currentText()
        self.load_data(text, status)

    def filter_by_status(self):
        print("[LOG] Фильтрация по статусу")
        self.search_records()

    def open_add_dialog(self):
        print("[LOG] Добавление новой записи")
        dialog = AddDialog()
        if dialog.exec_():
            _, model, status, date_in, buy_price, sell_price = dialog.get_data()
            batch_code = str(uuid.uuid4())[:8]
            self.cursor.execute("INSERT INTO forsunki (model, status, date_in, buy_price, sell_price, batch_code) VALUES (?, ?, ?, ?, ?, ?)",
                                (model, status, date_in, buy_price, sell_price, batch_code))
            self.conn.commit()
            self.load_data()

    def open_add_batch_dialog(self):
        print("[LOG] Добавление партии форсунок")
        dialog = BatchDialog()
        if dialog.exec_():
            model, count, buy_price, sell_price = dialog.get_data()
            batch_code = str(uuid.uuid4())[:8]
            date_in = datetime.now().strftime("%Y-%m-%d")
            for _ in range(count):
                self.cursor.execute("INSERT INTO forsunki (model, status, date_in, buy_price, sell_price, batch_code) VALUES (?, ?, ?, ?, ?, ?)",
                                    (model, "грязная", date_in, buy_price, sell_price, batch_code))
            self.conn.commit()
            self.load_data()

    def edit_record(self):
        print("[LOG] Редактирование записи")
        selected_row = self.table.currentRow()
        if selected_row < 0:
            return
        id = int(self.table.item(selected_row, 0).text())
        model = self.table.item(selected_row, 1).text()
        status = self.table.item(selected_row, 2).text()
        date_in = self.table.item(selected_row, 3).text()
        buy_price = float(self.table.item(selected_row, 4).text())
        sell_price = float(self.table.item(selected_row, 5).text())

        dialog = AddDialog((id, model, status, date_in, buy_price, sell_price))
        if dialog.exec_():
            id, model, status, date_in, buy_price, sell_price = dialog.get_data()
            self.cursor.execute("UPDATE forsunki SET model=?, status=?, date_in=?, buy_price=?, sell_price=? WHERE id=?",
                                (model, status, date_in, buy_price, sell_price, id))
            self.conn.commit()
            self.load_data()

    def delete_record(self):
        print("[LOG] Удаление записи")
        selected_row = self.table.currentRow()
        if selected_row < 0:
            return
        id = int(self.table.item(selected_row, 0).text())
        confirm = QMessageBox.question(self, "Удалить", "Удалить выбранную форсунку?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            self.cursor.execute("DELETE FROM forsunki WHERE id=?", (id,))
            self.conn.commit()
            self.load_data()

    def export_to_csv(self):
        print("[LOG] Экспорт в CSV")
        self.cursor.execute("SELECT * FROM forsunki")
        data = self.cursor.fetchall()
        filename = f"forsunki_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            headers = ["ID", "Марка/модель", "Состояние", "Дата поступления", "Цена закупки", "Цена продажи", "Код партии", "Прибыль"]
            writer.writerow(headers)
            for row in data:
                profit = row[5] - row[4]
                writer.writerow(list(row) + [profit])

        try:
            os.startfile(filename)
        except AttributeError:
            import subprocess
            subprocess.call(["open" if sys.platform == "darwin" else "xdg-open", filename])

    def show_stats(self):
        print("[LOG] Отображение аналитики")
        self.cursor.execute("SELECT SUM(buy_price), SUM(sell_price) FROM forsunki")
        result = self.cursor.fetchone()
        total_buy = result[0] if result[0] else 0.0
        total_sell = result[1] if result[1] else 0.0
        profit = total_sell - total_buy
        QMessageBox.information(self, "Аналитика", f"Закуплено на: {total_buy:.2f}₽\nПродано на: {total_sell:.2f}₽\nПрибыль: {profit:.2f}₽")

    def show_plots(self):
        print("[LOG] Отображение графиков")
        self.cursor.execute("SELECT * FROM forsunki")
        data = self.cursor.fetchall()
        self.plot_window = PlotWindow(data)
        self.plot_window.show()

    def show_financial_analytics(self):
        print("[LOG] Отображение финансовой аналитики")
        self.cursor.execute("SELECT SUM(buy_price), SUM(sell_price) FROM forsunki")
        result = self.cursor.fetchone()
        total_buy = result[0] if result[0] else 0.0
        total_sell = result[1] if result[1] else 0.0
        profit = total_sell - total_buy

        QMessageBox.information(self, "Финансовая аналитика",
                                f"Общая стоимость закупок: {total_buy:.2f}₽\n"
                                f"Общая стоимость продаж: {total_sell:.2f}₽\n"
                                f"Прибыль: {profit:.2f}₽")

    def update_stock(self, change):
        print(f"[LOG] Обновление запаса на {change}")
        self.cursor.execute("UPDATE forsunki SET count = count + ? WHERE id = ?", (change, self.selected_id))
        self.conn.commit()
        self.load_data()

    def log_change(self, injector_id, change_type, details):
        print(f"[LOG] Запись изменения: {change_type} - {details}")
        self.cursor.execute('''INSERT INTO history (injector_id, change_type, change_date, details)
                               VALUES (?, ?, ?, ?)''',
                            (injector_id, change_type, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), details))
        self.conn.commit()

    def show_history(self, injector_id):
        print(f"[LOG] Показ истории для форсунки ID {injector_id}")
        self.cursor.execute("SELECT change_type, change_date, details FROM history WHERE injector_id = ?", (injector_id,))
        history_data = self.cursor.fetchall()
        history_text = '\n'.join([f"{change_type} ({change_date}): {details}" for change_type, change_date, details in history_data])
        QMessageBox.information(self, "История изменений", history_text)

    def print_kit_label(self, kit_id):
        print("[LOG] Печать этикетки для комплекта")
        self.cursor.execute("SELECT kit_code, shelf_section, injector_ids FROM kits WHERE id = ?", (kit_id,))
        kit = self.cursor.fetchone()
        if not kit:
            QMessageBox.warning(self, "Ошибка", "Комплект не найден.")
            return

        filename = f"kit_label_{kit_id}.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        c.drawString(100, 750, f"Код комплекта: {kit[0]}")
        c.drawString(100, 730, f"Секция стеллажа: {kit[1]}")
        c.drawString(100, 710, f"Форсунки: {kit[2]}")
        c.save()

        try:
            os.startfile(filename)
        except AttributeError:
            import subprocess
            subprocess.call(["open" if sys.platform == "darwin" else "xdg-open", filename])

    def attach_file_to_kit(self, kit_id):
        print("[LOG] Прикрепление файла к комплекту")
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "", "All Files (*);;Image Files (*.png *.jpg *.bmp);;Video Files (*.mp4 *.avi)", options=options)
        if file_path:
            self.cursor.execute("INSERT INTO kit_files (kit_id, file_path) VALUES (?, ?)", (kit_id, file_path))
            self.conn.commit()
            QMessageBox.information(self, "Успех", "Файл успешно прикреплен к комплекту.")

    def open_create_kit_dialog(self):
        print("[LOG] Создание комплекта форсунок")
        selected_rows = self.table.selectionModel().selectedRows()
        if len(selected_rows) < 4:
            QMessageBox.warning(self, "Ошибка", "Выберите как минимум 4 форсунки для создания комплекта.")
            return

        kit_code = str(uuid.uuid4())[:8]  # Генерация уникального кода
        shelf_section, ok = QInputDialog.getText(self, "Секция стеллажа", "Введите секцию стеллажа:")
        if not ok or not shelf_section:
            return

        injector_ids = [self.table.item(row.row(), 0).text() for row in selected_rows]
        self.cursor.execute("INSERT INTO kits (kit_code, shelf_section, injector_ids) VALUES (?, ?, ?)",
                            (kit_code, shelf_section, ','.join(injector_ids)))
        self.conn.commit()
        QMessageBox.information(self, "Успех", f"Комплект успешно создан с кодом {kit_code}.")
        # self.print_kit_label(self.cursor.lastrowid)  # Отключение печати этикеток

if __name__ == '__main__':
    print("[LOG] Программа стартует")
    app = QApplication(sys.argv)
    window = InjectorApp()
    window.show()
    print("[LOG] Окно показано")
    sys.exit(app.exec_())
