import sys
import os
import sqlite3
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox,
                            QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
                            QDateEdit, QMessageBox, QHBoxLayout, QStatusBar)
from PyQt5.QtGui import QIntValidator
from datetime import datetime

DB_PATH = os.path.join(os.getcwd(), 'storage.db')

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS ProductTypes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS Products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            type_id INTEGER,
            FOREIGN KEY (type_id) REFERENCES ProductTypes(id)
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS OperationTypes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS WarehouseOperations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            type_id INTEGER,
            quantity INTEGER,
            product_id INTEGER,
            FOREIGN KEY (type_id) REFERENCES OperationTypes(id),
            FOREIGN KEY (product_id) REFERENCES Products(id)
        )''')
        cursor.execute("SELECT COUNT(*) FROM ProductTypes")
        if cursor.fetchone()[0] == 0:
            cursor.executemany("INSERT INTO ProductTypes (name) VALUES (?)",
                            [('Сырье',), ('Готовая продукция',), ('Инструменты',)])
            cursor.executemany("INSERT INTO OperationTypes (name) VALUES (?)",
                            [('Поступление',), ('Списание',)])
            cursor.executemany("INSERT INTO Products (name, description, type_id) VALUES (?, ?, ?)",
                            [('Доска 50x150', 'Сосна, 6м', 1),
                                ('Гвозди 100мм', 'Стальные', 3),
                                ('Стол обеденный', 'Деревянный', 2)])
            cursor.executemany(
                "INSERT INTO WarehouseOperations (date, type_id, quantity, product_id) VALUES (?, ?, ?, ?)",
                [('2025-04-01', 1, 100, 1),
                ('2025-04-02', 1, 1000, 2),
                ('2025-04-03', 1, 10, 3),
                ('2025-04-04', 2, 20, 1)])
        conn.commit()
        conn.close()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Складской учет')
        self.setGeometry(100, 100, 1200, 800)
        self.db = Database(DB_PATH)
        self.initUI()
        self.apply_styles()
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

    def apply_styles(self):
        style = """
            QMainWindow, QDialog {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QTableWidget {
                border: 1px solid #ddd;
                background-color: white;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QLineEdit, QComboBox, QDateEdit {
                padding: 6px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QLabel {
                color: #333;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #4CAF50;
            }
        """
        self.setStyleSheet(style)

    def initUI(self):
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.tab_widget = QtWidgets.QTabWidget()
        self.layout.addWidget(self.tab_widget)
        self.initProductsTab()
        self.initOperationsTab()
        self.initReportsTab()

    def initProductsTab(self):
        self.tab_products = QtWidgets.QWidget()
        self.tab_widget.addTab(self.tab_products, 'Товары')
        layout = QtWidgets.QVBoxLayout(self.tab_products)
        search_layout = QHBoxLayout()
        self.product_search = QLineEdit()
        self.product_search.setPlaceholderText("Поиск по названию...")
        self.product_search.textChanged.connect(self.filterProducts)
        self.product_type_filter = QComboBox()
        self.product_type_filter.addItem("Все типы", 0)
        self.updateProductTypeFilter()
        self.product_type_filter.currentIndexChanged.connect(self.filterProducts)
        search_layout.addWidget(self.product_search)
        search_layout.addWidget(self.product_type_filter)
        layout.addLayout(search_layout)
        buttons_layout = QHBoxLayout()
        self.button_add_product = QPushButton('Добавить товар')
        self.button_edit_product = QPushButton('Редактировать товар')
        self.button_delete_product = QPushButton('Удалить товар')
        self.button_add_product.setToolTip('Добавить новый товар')
        self.button_edit_product.setToolTip('Редактировать выбранный товар')
        self.button_delete_product.setToolTip('Удалить выбранный товар')
        self.button_add_product.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_FileDialogNewFolder))
        self.button_edit_product.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_FileDialogDetailedView))
        self.button_delete_product.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_TrashIcon))
        self.button_add_product.clicked.connect(self.showAddProductDialog)
        self.button_edit_product.clicked.connect(self.showEditProductDialog)
        self.button_delete_product.clicked.connect(self.deleteProduct)
        buttons_layout.addWidget(self.button_add_product)
        buttons_layout.addWidget(self.button_edit_product)
        buttons_layout.addWidget(self.button_delete_product)
        layout.addLayout(buttons_layout)
        self.products_table = QTableWidget()
        layout.addWidget(self.products_table)
        self.updateProductsTable()
        self.products_table.itemSelectionChanged.connect(self.updateProductButtons)

    def updateProductsTable(self):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.id, p.name, p.description, pt.name AS type_name, 
                       COALESCE((SELECT SUM(wo.quantity) 
                                 FROM WarehouseOperations wo 
                                 WHERE wo.product_id = p.id AND wo.type_id = 1), 0) -
                       COALESCE((SELECT SUM(wo.quantity) 
                                 FROM WarehouseOperations wo 
                                 WHERE wo.product_id = p.id AND wo.type_id = 2), 0) AS total_quantity
                FROM Products p
                JOIN ProductTypes pt ON p.type_id = pt.id
            """)
            records = cursor.fetchall()
            self.products_table.setRowCount(len(records))
            self.products_table.setColumnCount(5)
            self.products_table.setHorizontalHeaderLabels(['ID', 'Название', 'Описание', 'Тип', 'Количество на складе'])
            self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            for i, row in enumerate(records):
                for j, col in enumerate(row):
                    self.products_table.setItem(i, j, QTableWidgetItem(str(col)))
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка обновления таблицы товаров: {str(e)}')

    def updateProductTypeFilter(self):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM ProductTypes")
            types = cursor.fetchall()
            for t in types:
                self.product_type_filter.addItem(t[1], t[0])
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка обновления фильтра типов: {str(e)}')

    def filterProducts(self):
        try:
            search_text = self.product_search.text().lower()
            type_filter = self.product_type_filter.currentData()
            conn = self.db.get_connection()
            cursor = conn.cursor()
            query = """
                SELECT p.id, p.name, p.description, pt.name AS type_name, 
                       COALESCE((SELECT SUM(wo.quantity) 
                                 FROM WarehouseOperations wo 
                                 WHERE wo.product_id = p.id AND wo.type_id = 1), 0) -
                       COALESCE((SELECT SUM(wo.quantity) 
                                 FROM WarehouseOperations wo 
                                 WHERE wo.product_id = p.id AND wo.type_id = 2), 0) AS total_quantity
                FROM Products p
                JOIN ProductTypes pt ON p.type_id = pt.id
                WHERE (? = 0 OR p.type_id = ?)
                AND p.name LIKE ?
            """
            cursor.execute(query, (type_filter, type_filter, f'%{search_text}%'))
            records = cursor.fetchall()
            conn.close()
            self.products_table.setRowCount(len(records))
            self.products_table.setColumnCount(5)
            for i, row in enumerate(records):
                for j, col in enumerate(row):
                    item = QTableWidgetItem(str(col))
                    self.products_table.setItem(i, j, item)
                    if j == 4 and int(col) < 10:
                        item.setBackground(QtGui.QColor(255, 204, 204))
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка фильтрации товаров: {str(e)}')

    def showAddProductDialog(self):
        dialog = AddProductDialog(self.db)
        dialog.setStyleSheet(self.styleSheet())
        if dialog.exec_() == QDialog.Accepted:
            self.updateProductsTable()

    def showEditProductDialog(self):
        selected_items = self.products_table.selectedItems()
        if selected_items and len(selected_items) >= 1:
            product_id = selected_items[0].text()
            dialog = EditProductDialog(self.db, product_id)
            dialog.setStyleSheet(self.styleSheet())
            if dialog.exec_() == QDialog.Accepted:
                self.updateProductsTable()

    def deleteProduct(self):
        selected_items = self.products_table.selectedItems()
        if selected_items and len(selected_items) >= 1 and QMessageBox.question(self, 'Подтверждение',
            'Вы уверены, что хотите удалить товар?') == QMessageBox.Yes:
            product_id = selected_items[0].text()
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Products WHERE id = ?", (product_id,))
                conn.commit()
                conn.close()
                self.updateProductsTable()
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Ошибка удаления товара: {str(e)}')

    def updateProductButtons(self):
        selected_items = self.products_table.selectedItems()
        enabled = bool(selected_items) and len(selected_items) >= 2
        self.button_edit_product.setEnabled(enabled)
        self.button_delete_product.setEnabled(enabled)
        if enabled:
            self.statusBar.showMessage(f"Выбран товар: {selected_items[1].text()}")
        else:
            self.statusBar.clearMessage()

    def initOperationsTab(self):
        self.tab_operations = QtWidgets.QWidget()
        self.tab_widget.addTab(self.tab_operations, 'Операции')
        layout = QtWidgets.QVBoxLayout(self.tab_operations)
        search_layout = QHBoxLayout()
        self.operation_search = QLineEdit()
        self.operation_search.setPlaceholderText("Поиск по товару...")
        self.operation_search.textChanged.connect(self.filterOperations)
        self.operation_type_filter = QComboBox()
        self.operation_type_filter.addItem("Все типы", 0)
        self.updateOperationTypeFilter()
        self.operation_type_filter.currentIndexChanged.connect(self.filterOperations)
        search_layout.addWidget(self.operation_search)
        search_layout.addWidget(self.operation_type_filter)
        layout.addLayout(search_layout)
        buttons_layout = QHBoxLayout()
        self.button_add_operation = QPushButton('Добавить операцию')
        self.button_edit_operation = QPushButton('Редактировать операцию')
        self.button_delete_operation = QPushButton('Удалить операцию')
        self.button_add_operation.setToolTip('Добавить новую операцию')
        self.button_edit_operation.setToolTip('Редактировать выбранную операцию')
        self.button_delete_operation.setToolTip('Удалить выбранную операцию')
        self.button_add_operation.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_FileDialogNewFolder))
        self.button_edit_operation.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_FileDialogDetailedView))
        self.button_delete_operation.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_TrashIcon))
        self.button_add_operation.clicked.connect(self.showAddOperationDialog)
        self.button_edit_operation.clicked.connect(self.showEditOperationDialog)
        self.button_delete_operation.clicked.connect(self.deleteOperation)
        buttons_layout.addWidget(self.button_add_operation)
        buttons_layout.addWidget(self.button_edit_operation)
        buttons_layout.addWidget(self.button_delete_operation)
        layout.addLayout(buttons_layout)
        self.operations_table = QTableWidget()
        layout.addWidget(self.operations_table)
        self.updateOperationsTable()
        self.operations_table.itemSelectionChanged.connect(self.updateOperationButtons)

    def updateOperationsTable(self):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT wo.id, wo.date, ot.name AS operation_type, wo.quantity, p.name AS product_name
                FROM WarehouseOperations wo
                JOIN OperationTypes ot ON wo.type_id = ot.id
                JOIN Products p ON wo.product_id = p.id
            """)
            records = cursor.fetchall()
            conn.close()
            self.operations_table.setRowCount(len(records))
            self.operations_table.setColumnCount(5)
            self.operations_table.setHorizontalHeaderLabels(['ID', 'Дата', 'Тип операции', 'Количество', 'Товар'])
            self.operations_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            for i, row in enumerate(records):
                for j, col in enumerate(row):
                    self.operations_table.setItem(i, j, QTableWidgetItem(str(col)))
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка обновления таблицы операций: {str(e)}')

    def updateOperationTypeFilter(self):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM OperationTypes")
            types = cursor.fetchall()
            for t in types:
                self.operation_type_filter.addItem(t[1], t[0])
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка обновления фильтра операций: {str(e)}')

    def filterOperations(self):
        try:
            search_text = self.operation_search.text().lower()
            type_filter = self.operation_type_filter.currentData()
            conn = self.db.get_connection()
            cursor = conn.cursor()
            query = """
                SELECT wo.id, wo.date, ot.name AS operation_type, wo.quantity, p.name AS product_name
                FROM WarehouseOperations wo
                JOIN OperationTypes ot ON wo.type_id = ot.id
                JOIN Products p ON wo.product_id = p.id
                WHERE (? = 0 OR wo.type_id = ?)
                AND p.name LIKE ?
            """
            cursor.execute(query, (type_filter, type_filter, f'%{search_text}%'))
            records = cursor.fetchall()
            conn.close()
            self.operations_table.setRowCount(len(records))
            self.operations_table.setColumnCount(5)
            for i, row in enumerate(records):
                for j, col in enumerate(row):
                    self.operations_table.setItem(i, j, QTableWidgetItem(str(col)))
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка фильтрации операций: {str(e)}')

    def showAddOperationDialog(self):
        dialog = AddOperationDialog(self.db)
        dialog.setStyleSheet(self.styleSheet())
        if dialog.exec_() == QDialog.Accepted:
            self.updateOperationsTable()
            self.updateProductsTable()

    def showEditOperationDialog(self):
        selected_items = self.operations_table.selectedItems()
        if selected_items and len(selected_items) >= 1:
            operation_id = selected_items[0].text()
            dialog = EditOperationDialog(self.db, operation_id)
            dialog.setStyleSheet(self.styleSheet())
            if dialog.exec_() == QDialog.Accepted:
                self.updateOperationsTable()
                self.updateProductsTable()

    def deleteOperation(self):
        selected_items = self.operations_table.selectedItems()
        if selected_items and len(selected_items) >= 1 and QMessageBox.question(self, 'Подтверждение',
            'Вы уверены, что хотите удалить операцию?') == QMessageBox.Yes:
            operation_id = selected_items[0].text()
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM WarehouseOperations WHERE id = ?", (operation_id,))
                conn.commit()
                conn.close()
                self.updateOperationsTable()
                self.updateProductsTable()
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Ошибка удаления операции: {str(e)}')

    def updateOperationButtons(self):
        selected_items = self.operations_table.selectedItems()
        enabled = bool(selected_items) and len(selected_items) >= 3
        self.button_edit_operation.setEnabled(enabled)
        self.button_delete_operation.setEnabled(enabled)
        if enabled:
            self.statusBar.showMessage(f"Выбрана операция: {selected_items[2].text()} от {selected_items[1].text()}")
        else:
            self.statusBar.clearMessage()

    def initReportsTab(self):
        self.tab_reports = QtWidgets.QWidget()
        self.tab_widget.addTab(self.tab_reports, 'Отчеты')
        layout = QtWidgets.QVBoxLayout(self.tab_reports)
        self.start_date_label = QLabel('Начальная дата')
        self.start_date_edit = QDateEdit(calendarPopup=True)
        self.start_date_edit.setDate(QtCore.QDate.currentDate())
        self.end_date_label = QLabel('Конечная дата')
        self.end_date_edit = QDateEdit(calendarPopup=True)
        self.end_date_edit.setDate(QtCore.QDate.currentDate())
        self.button_generate_report = QPushButton('Сгенерировать отчет')
        self.button_generate_report.clicked.connect(self.generateReport)
        layout.addWidget(self.start_date_label)
        layout.addWidget(self.start_date_edit)
        layout.addWidget(self.end_date_label)
        layout.addWidget(self.end_date_edit)
        layout.addWidget(self.button_generate_report)

    def generateReport(self):
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        format_dialog = QtWidgets.QInputDialog()
        format_type, ok = format_dialog.getItem(self, "Формат отчета",
            "Выберите формат:", ["txt", "csv"], 0, False)
        format_dialog.setStyleSheet(self.styleSheet())
        if not ok:
            return
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.name, ot.name, SUM(wo.quantity), wo.date
                FROM WarehouseOperations wo
                JOIN Products p ON wo.product_id = p.id
                JOIN OperationTypes ot ON wo.type_id = ot.id
                WHERE wo.date BETWEEN ? AND ?
                GROUP BY p.name, ot.name, wo.date
            """, (start_date, end_date))
            operations = cursor.fetchall()
            if not operations:
                QMessageBox.warning(self, 'Предупреждение', 'Нет данных для создания отчета в указанном периоде')
                conn.close()
                return
            if format_type == "txt":
                report_text = f"Отчет по складу\nПериод: {start_date} - {end_date}\n\n"
                total = 0
                for op in operations:
                    report_text += f"Товар: {op[0]}, Тип: {op[1]}, Кол-во: {op[2]}, Дата: {op[3]}\n"
                    total += op[2]
                report_text += f"\nИтого: {total}"
                with open('report.txt', 'w', encoding='utf-8') as f:
                    f.write(report_text)
            else:
                with open('report.csv', 'w', encoding='utf-8') as f:
                    f.write("Товар,Тип операции,Количество,Дата\n")
                    total = 0
                    for op in operations:
                        f.write(f"{op[0]},{op[1]},{op[2]},{op[3]}\n")
                        total += op[2]
                    f.write(f"Итого,,{total},")
            conn.close()
            QMessageBox.information(self, 'Отчет создан', f'Отчет сохранен в report.{format_type}')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка генерации отчета: {str(e)}')

class AddProductDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.setWindowTitle('Добавить товар')
        self.setGeometry(100, 100, 400, 300)
        self.db = db
        layout = QVBoxLayout()
        self.label_name = QLabel('Название')
        self.input_name = QLineEdit()
        self.label_description = QLabel('Описание')
        self.input_description = QLineEdit()
        self.label_type = QLabel('Тип')
        self.combo_type = QComboBox()
        self.updateTypes()
        self.button_add = QPushButton('Добавить')
        self.button_add.clicked.connect(self.addProduct)
        self.input_name.setMaxLength(100)
        self.input_description.setMaxLength(255)
        self.input_name.setToolTip("Введите название товара (макс. 100 символов)")
        self.input_description.setToolTip("Введите описание (макс. 255 символов)")
        self.combo_type.setToolTip("Выберите тип товара")
        layout.addWidget(self.label_name)
        layout.addWidget(self.input_name)
        layout.addWidget(self.label_description)
        layout.addWidget(self.input_description)
        layout.addWidget(self.label_type)
        layout.addWidget(self.combo_type)
        layout.addWidget(self.button_add)
        self.setLayout(layout)

    def updateTypes(self):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM ProductTypes")
            types = cursor.fetchall()
            self.combo_type.clear()
            for t in types:
                self.combo_type.addItem(t[1], t[0])
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка загрузки типов: {str(e)}')

    def addProduct(self):
        name = self.input_name.text().strip()
        description = self.input_description.text().strip()
        type_id = self.combo_type.currentData()
        if not name:
            QMessageBox.warning(self, 'Ошибка', 'Название не может быть пустым')
            return
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Products (name, description, type_id) VALUES (?, ?, ?)",
                        (name, description, type_id))
            conn.commit()
            conn.close()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка добавления товара: {str(e)}')

class EditProductDialog(QDialog):
    def __init__(self, db, product_id):
        super().__init__()
        self.setWindowTitle('Редактировать товар')
        self.setGeometry(100, 100, 400, 300)
        self.db = db
        self.product_id = product_id
        layout = QVBoxLayout()
        self.label_name = QLabel('Название')
        self.input_name = QLineEdit()
        self.label_description = QLabel('Описание')
        self.input_description = QLineEdit()
        self.label_type = QLabel('Тип')
        self.combo_type = QComboBox()
        self.updateTypes()
        self.loadProductData()
        self.button_edit = QPushButton('Сохранить')
        self.button_edit.clicked.connect(self.editProduct)
        self.input_name.setMaxLength(100)
        self.input_description.setMaxLength(255)
        self.input_name.setToolTip("Введите название товара (макс. 100 символов)")
        self.input_description.setToolTip("Введите описание (макс. 255 символов)")
        self.combo_type.setToolTip("Выберите тип товара")
        layout.addWidget(self.label_name)
        layout.addWidget(self.input_name)
        layout.addWidget(self.label_description)
        layout.addWidget(self.input_description)
        layout.addWidget(self.label_type)
        layout.addWidget(self.combo_type)
        layout.addWidget(self.button_edit)
        self.setLayout(layout)

    def updateTypes(self):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM ProductTypes")
            types = cursor.fetchall()
            self.combo_type.clear()
            for t in types:
                self.combo_type.addItem(t[1], t[0])
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка загрузки типов: {str(e)}')

    def loadProductData(self):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name, description, type_id FROM Products WHERE id = ?",
                        (self.product_id,))
            product = cursor.fetchone()
            if product:
                self.input_name.setText(product[0])
                self.input_description.setText(product[1] if product[1] else '')
                self.combo_type.setCurrentIndex(self.combo_type.findData(product[2]))
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка загрузки данных товара: {str(e)}')

    def editProduct(self):
        name = self.input_name.text().strip()
        description = self.input_description.text().strip()
        type_id = self.combo_type.currentData()
        if not name:
            QMessageBox.warning(self, 'Ошибка', 'Название не может быть пустым')
            return
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE Products SET name = ?, description = ?, type_id = ? WHERE id = ?",
                        (name, description, type_id, self.product_id))
            conn.commit()
            conn.close()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка редактирования товара: {str(e)}')

class AddOperationDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.setWindowTitle('Добавить операцию')
        self.setGeometry(100, 100, 400, 300)
        self.db = db
        layout = QVBoxLayout()
        self.label_date = QLabel('Дата')
        self.date_edit = QDateEdit(calendarPopup=True)
        self.date_edit.setDate(QtCore.QDate.currentDate())
        self.label_type = QLabel('Тип операции')
        self.combo_type = QComboBox()
        self.updateOperationTypes()
        self.label_quantity = QLabel('Количество')
        self.input_quantity = QLineEdit()
        self.label_product = QLabel('Товар')
        self.combo_product = QComboBox()
        self.updateProducts()
        self.button_add = QPushButton('Добавить')
        self.button_add.clicked.connect(self.addOperation)
        self.input_quantity.setValidator(QIntValidator(1, 999999))
        self.input_quantity.setToolTip("Введите количество (только положительные числа)")
        self.date_edit.setToolTip("Выберите дату операции")
        self.combo_type.setToolTip("Выберите тип операции")
        self.combo_product.setToolTip("Выберите товар")
        layout.addWidget(self.label_date)
        layout.addWidget(self.date_edit)
        layout.addWidget(self.label_type)
        layout.addWidget(self.combo_type)
        layout.addWidget(self.label_quantity)
        layout.addWidget(self.input_quantity)
        layout.addWidget(self.label_product)
        layout.addWidget(self.combo_product)
        layout.addWidget(self.button_add)
        self.setLayout(layout)

    def updateOperationTypes(self):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM OperationTypes")
            types = cursor.fetchall()
            self.combo_type.clear()
            for t in types:
                self.combo_type.addItem(t[1], t[0])
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка загрузки типов операций: {str(e)}')

    def updateProducts(self):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM Products")
            products = cursor.fetchall()
            self.combo_product.clear()
            for p in products:
                self.combo_product.addItem(p[1], p[0])
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка загрузки товаров: {str(e)}')

    def addOperation(self):
        if not self.input_quantity.text():
            QMessageBox.warning(self, 'Ошибка', 'Количество не может быть пустым')
            return
        date = self.date_edit.date().toString("yyyy-MM-dd")
        type_id = self.combo_type.currentData()
        quantity = int(self.input_quantity.text())
        product_id = self.combo_product.currentData()
        if type_id == 2 and not self.checkIfEnoughStock(product_id, quantity):
            QMessageBox.warning(self, 'Ошибка', 'Недостаточно товара на складе для списания')
            return
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO WarehouseOperations (date, type_id, quantity, product_id) VALUES (?, ?, ?, ?)",
                        (date, type_id, quantity, product_id))
            conn.commit()
            conn.close()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка добавления операции: {str(e)}')

    def checkIfEnoughStock(self, product_id, quantity):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COALESCE((SELECT SUM(wo.quantity) 
                                 FROM WarehouseOperations wo 
                                 WHERE wo.product_id = ? AND wo.type_id = 1), 0) -
                       COALESCE((SELECT SUM(wo.quantity) 
                                 FROM WarehouseOperations wo 
                                 WHERE wo.product_id = ? AND wo.type_id = 2), 0) AS total_quantity
            """, (product_id, product_id))
            stock = cursor.fetchone()[0]
            conn.close()
            return stock >= quantity
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка проверки остатка: {str(e)}')
            return False

class EditOperationDialog(QDialog):
    def __init__(self, db, operation_id):
        super().__init__()
        self.setWindowTitle('Редактировать операцию')
        self.setGeometry(100, 100, 400, 300)
        self.db = db
        self.operation_id = operation_id
        layout = QVBoxLayout()
        self.label_date = QLabel('Дата')
        self.date_edit = QDateEdit(calendarPopup=True)
        self.label_type = QLabel('Тип операции')
        self.combo_type = QComboBox()
        self.updateOperationTypes()
        self.label_quantity = QLabel('Количество')
        self.input_quantity = QLineEdit()
        self.label_product = QLabel('Товар')
        self.combo_product = QComboBox()
        self.updateProducts()
        self.loadOperationData()
        self.button_edit = QPushButton('Сохранить')
        self.button_edit.clicked.connect(self.editOperation)
        self.input_quantity.setValidator(QIntValidator(1, 999999))
        self.input_quantity.setToolTip("Введите количество (только положительные числа)")
        self.date_edit.setToolTip("Выберите дату операции")
        self.combo_type.setToolTip("Выберите тип операции")
        self.combo_product.setToolTip("Выберите товар")
        layout.addWidget(self.label_date)
        layout.addWidget(self.date_edit)
        layout.addWidget(self.label_type)
        layout.addWidget(self.combo_type)
        layout.addWidget(self.label_quantity)
        layout.addWidget(self.input_quantity)
        layout.addWidget(self.label_product)
        layout.addWidget(self.combo_product)
        layout.addWidget(self.button_edit)
        self.setLayout(layout)

    def updateOperationTypes(self):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM OperationTypes")
            types = cursor.fetchall()
            self.combo_type.clear()
            for t in types:
                self.combo_type.addItem(t[1], t[0])
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка загрузки типов операций: {str(e)}')

    def updateProducts(self):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM Products")
            products = cursor.fetchall()
            self.combo_product.clear()
            for p in products:
                self.combo_product.addItem(p[1], p[0])
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка загрузки товаров: {str(e)}')

    def loadOperationData(self):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT date, type_id, quantity, product_id FROM WarehouseOperations WHERE id = ?",
                        (self.operation_id,))
            operation = cursor.fetchone()
            if operation:
                self.date_edit.setDate(QtCore.QDate.fromString(operation[0], "yyyy-MM-dd"))
                self.combo_type.setCurrentIndex(self.combo_type.findData(operation[1]))
                self.input_quantity.setText(str(operation[2]))
                self.combo_product.setCurrentIndex(self.combo_product.findData(operation[3]))
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка загрузки данных операции: {str(e)}')

    def editOperation(self):
        if not self.input_quantity.text():
            QMessageBox.warning(self, 'Ошибка', 'Количество не может быть пустым')
            return
        date = self.date_edit.date().toString("yyyy-MM-dd")
        type_id = self.combo_type.currentData()
        quantity = int(self.input_quantity.text())
        product_id = self.combo_product.currentData()
        if type_id == 2 and not self.checkIfEnoughStock(product_id, quantity):
            QMessageBox.warning(self, 'Ошибка', 'Недостаточно товара на складе для списания')
            return
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE WarehouseOperations SET date = ?, type_id = ?, quantity = ?, product_id = ? WHERE id = ?",
                (date, type_id, quantity, product_id, self.operation_id))
            conn.commit()
            conn.close()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка редактирования операции: {str(e)}')

    def checkIfEnoughStock(self, product_id, quantity):
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COALESCE((SELECT SUM(wo.quantity) 
                                 FROM WarehouseOperations wo 
                                 WHERE wo.product_id = ? AND wo.type_id = 1), 0) -
                       COALESCE((SELECT SUM(wo.quantity) 
                                 FROM WarehouseOperations wo 
                                 WHERE wo.product_id = ? AND wo.type_id = 2), 0) AS total_quantity
            """, (product_id, product_id))
            stock = cursor.fetchone()[0]
            conn.close()
            return stock >= quantity
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка проверки остатка: {str(e)}')
            return False

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())