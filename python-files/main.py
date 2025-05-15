import sys
import sqlite3
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget,
    QLabel, QTableWidget, QTableWidgetItem, QMessageBox, QToolBar, QAction,
    QDialog, QLineEdit, QFormLayout, QComboBox, QFileDialog, QGraphicsDropShadowEffect,
    QCheckBox, QHBoxLayout, QInputDialog, QTabWidget, QMenu, QHeaderView
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette
from PyQt5.QtWidgets import QScrollArea, QTextEdit
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox
from PyQt5.QtCore import QTimer

# Инициализация базы данных и создание таблиц, если их еще нет
def init_db():
    conn = sqlite3.connect('components.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS components (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        model TEXT NOT NULL,
                        quantity INTEGER NOT NULL CHECK (quantity >= 0))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS requests (
                        id INTEGER PRIMARY KEY,
                        type TEXT NOT NULL,
                        component_id INTEGER NOT NULL,
                        employee_id INTEGER NOT NULL,
                        status TEXT DEFAULT "Не выполнено",
                        FOREIGN KEY(component_id) REFERENCES components(id),
                        FOREIGN KEY(employee_id) REFERENCES employees(id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS request_logs (
                        id INTEGER PRIMARY KEY,
                        request_id INTEGER,
                        action TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(request_id) REFERENCES requests(id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS archived_requests (
                        id INTEGER PRIMARY KEY,
                        type TEXT NOT NULL,
                        component_id INTEGER NOT NULL,
                        employee_id INTEGER NOT NULL,
                        status TEXT DEFAULT "Выполнено",
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(component_id) REFERENCES components(id),
                        FOREIGN KEY(employee_id) REFERENCES employees(id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS employees (
                        id INTEGER PRIMARY KEY,
                        full_name TEXT NOT NULL,
                        department TEXT NOT NULL)''')
    cursor.execute("""CREATE TABLE IF NOT EXISTS request_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event TEXT NOT NULL,
                        user_login TEXT NOT NULL,
                        action TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")
    conn.commit()
    conn.close()

def check_db_existence():
    try:
        conn = sqlite3.connect('components.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        conn.close()
        if not tables:
            print("Ошибка: База данных пуста или не существует.")
            sys.exit(1)  # Точка выхода
    except sqlite3.Error as e:
        print(f"Ошибка при подключении к БД: {e}")
        sys.exit(1)  # Точка выхода

# Функция для обновления ID динамически после удаления
def update_ids(table_name):
    conn = sqlite3.connect('components.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT id FROM {table_name} ORDER BY id")
    rows = cursor.fetchall()
    
    # Переустановка ID начиная с 1
    for new_id, (old_id,) in enumerate(rows, start=1):
        cursor.execute(f"UPDATE {table_name} SET id = ? WHERE id = ?", (new_id, old_id))
    
    conn.commit()
    conn.close()
    
class BaseDialog(QDialog):
    def __init__(self, title="Диалог"):
        super().__init__()
        self.setWindowTitle(title)
        self.setFixedSize(350, 300)
        self.setFont(QFont("Arial", 10))
        self.setStyleSheet("""
            background-color: #2c2f33; 
            color: #ffffff;
            border-radius: 10px;
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.attempts = 0  # Счетчик попыток входа
        self.max_attempts = 3  # Максимальное количество попыток
        self.blocked = False  # Флаг блокировки

    def init_ui(self):
        self.setWindowTitle("Авторизация")
        self.setFixedSize(300, 200)
        self.setFont(QFont("Arial", 10))
        self.setStyleSheet("background-color: #2c2f33; color: #ffffff;")

        layout = QVBoxLayout()

        self.login_input = QLineEdit(self)
        self.login_input.setPlaceholderText("Логин")
        self.login_input.setStyleSheet("background-color: #23272a; color: #ffffff; border-radius: 5px; padding: 5px;")
        layout.addWidget(self.login_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("background-color: #23272a; color: #ffffff; border-radius: 5px; padding: 5px;")
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("Войти", self)
        self.login_button.setStyleSheet("background-color: #7289da; color: #ffffff; border-radius: 5px;")
        self.login_button.clicked.connect(self.check_credentials)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def check_credentials(self):
        login = self.login_input.text()
        password = self.password_input.text()
        conn = sqlite3.connect('components.db')
        cursor = conn.cursor()
        if self.blocked:
            QMessageBox.warning(self, "Блокировка", "Система заблокирована из-за превышения попыток входа. Попробуйте позже.")
            return

        login = self.login_input.text()
        password = self.password_input.text()

        # Пример проверки учетных данных
        if (login == "admin" and password == "password") or \
           (login == "user" and password == "password"):
            QMessageBox.information(self, "Успех", "Вы успешно вошли в систему!")
            self.accept()  # Закрыть диалог с успешным результатом
        else:
            self.attempts += 1
            if self.attempts >= self.max_attempts:
                self.blocked = True
                QMessageBox.critical(self, "Блокировка", "Превышено максимальное количество попыток входа. Система заблокирована на 1 минуту.")
                QTimer.singleShot(60000, self.reset_attempts)  # Разблокировать через 1 минуту
            else:
                QMessageBox.warning(self, "Ошибка", f"Неверный логин или пароль. Осталось попыток: {self.max_attempts - self.attempts}")

    def reset_attempts(self):
        self.blocked = False
        self.attempts = 0
        QMessageBox.information(self, "Разблокировка", "Система разблокирована. Вы можете снова попробовать войти.")
class InstructionDialog(BaseDialog):
    def __init__(self):
        super().__init__(title="Инструкция")

        # Создаём виджет прокрутки
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        # Используем QTextEdit для отображения текста и включаем прокрутку
        instruction_text = QTextEdit(self)
        instruction_text.setReadOnly(True)
        instruction_text.setStyleSheet("background-color: #2c2f33; color: #ffffff; padding: 10px; border-radius: 5px;")

        instruction_text.setText("""
            ### Инструкция по использованию программы "Управление комплектующими и заявками для МФУ"

            #### Вход в систему
            1. При запуске программы откроется окно авторизации. Введите логин и пароль.
               - **admin** / **password** для входа администратора.
               - **user** / **password** для входа пользователя.
            2. Пользователи с ролью "admin" имеют расширенные права, включая управление комплектующими и сотрудниками.

            #### Основное меню
            Программа состоит из нескольких вкладок:
            - **Комплектующие** (только для администратора) — управление списком комплектующих (добавление, редактирование, удаление).
            - **Сотрудники** (только для администратора) — управление списком сотрудников (добавление, редактирование, удаление).
            - **Заявки** — просмотр, создание и редактирование заявок на комплектующие.
            - **Архив заявок** (только для администратора) — просмотр выполненных заявок.
              
            #### Управление комплектующими
            1. Выберите вкладку "Комплектующие" и воспользуйтесь меню "Комплектующие" для добавления, редактирования или удаления записей.
            2. Используйте кнопку "Поиск комплектующей" для быстрого поиска по наименованию или модели.

            #### Управление сотрудниками
            1. Откройте вкладку "Сотрудники". В меню "Сотрудники" доступны функции для добавления, редактирования и удаления сотрудников.
            2. Поле "Отдел" для каждого сотрудника помогает назначить его к определённой категории.

            #### Управление заявками
            1. На вкладке "Заявки" можно добавлять, редактировать и удалять заявки на комплектующие.
            2. При создании или редактировании заявки:
               - Укажите тип заявки (например, "Получение", "Списание").
               - Выберите комплектующую и сотрудника.
               - Администраторы могут изменять статус заявки на "Выполнено" после завершения.

            #### Просмотр логов и отчётов (только для администратора)
            - **Логи** — доступен просмотр истории действий, связанных с заявками.
            - **Отчёт** — для генерации Excel-отчёта, содержащего данные о заявках, комплектующих, сотрудниках, логах и архивных заявках.

            #### Выход из системы
            - В любой момент вы можете выйти из системы через кнопку "Выход" в правом нижнем углу приложения и вернуться на страницу авторизации.
        """)

        # Добавляем виджет с текстом в область прокрутки
        scroll_area.setWidget(instruction_text)

        # Устанавливаем layout
        layout = QVBoxLayout()
        layout.addWidget(scroll_area)
        self.setLayout(layout)

        # Устанавливаем размер окна
        self.setFixedSize(400, 500)
        
class ComponentDialog(BaseDialog):
    def __init__(self, name="", model="", quantity=0):
        super().__init__(title="Комплектующая")
        
        layout = QFormLayout()
        self.name_input = QLineEdit(name, self)
        self.model_input = QLineEdit(model, self)
        self.quantity_input = QLineEdit(str(quantity), self)

        layout.addRow("Наименование:", self.name_input)
        layout.addRow("Модель:", self.model_input)
        layout.addRow("Количество:", self.quantity_input)

        btn_submit = QPushButton("Сохранить", self)
        btn_submit.setStyleSheet("background-color: #7289da; color: #ffffff; border-radius: 5px; padding: 5px;")
        btn_submit.clicked.connect(self.accept)
        layout.addWidget(btn_submit)
        self.setLayout(layout)

    def get_data(self):
        return self.name_input.text(), self.model_input.text(), int(self.quantity_input.text())

class EmployeeDialog(BaseDialog):
    def __init__(self, full_name="", department=""):
        super().__init__(title="Сотрудник")
        
        layout = QFormLayout()
        self.full_name_input = QLineEdit(full_name, self)
        self.department_input = QLineEdit(department, self)

        layout.addRow("ФИО:", self.full_name_input)
        layout.addRow("Отдел:", self.department_input)

        btn_submit = QPushButton("Сохранить", self)
        btn_submit.setStyleSheet("background-color: #7289da; color: #ffffff; border-radius: 5px; padding: 5px;")
        btn_submit.clicked.connect(self.accept)
        layout.addWidget(btn_submit)
        self.setLayout(layout)

    def get_data(self):
        return self.full_name_input.text(), self.department_input.text()

class RequestDialog(BaseDialog):
    def __init__(self, type_="", component_id=0, employee_id=0, status="Не выполнено", is_admin=False):
        super().__init__(title="Заявка")
        
        layout = QFormLayout()

        # Поле для выбора типа заявки
        self.type_input = QComboBox(self)
        self.type_input.addItems(["Получение", "Списание", "Ремонт", "Замена"])
        if type_:
            index = self.type_input.findText(type_)
            if index >= 0:
                self.type_input.setCurrentIndex(index)

        # Поле для выбора комплектующей
        self.component_input = QComboBox(self)
        self.populate_components()
        if component_id:
            self.set_selected_component(component_id)

        # Поле для выбора сотрудника
        self.employee_input = QComboBox(self)
        self.populate_employees()
        if employee_id:
            self.set_selected_employee(employee_id)

        # Поле для статуса (только для администратора)
        self.is_admin = is_admin
        if self.is_admin:
            self.status_checkbox = QCheckBox("Выполнено", self)
            self.status_checkbox.setChecked(status == "Выполнено")
            layout.addRow("Статус:", self.status_checkbox)

        # Добавление полей в форму
        layout.addRow("Тип заявки:", self.type_input)
        layout.addRow("Комплектующая:", self.component_input)
        layout.addRow("Сотрудник:", self.employee_input)

        # Кнопка для сохранения
        btn_submit = QPushButton("Сохранить", self)
        btn_submit.setStyleSheet("background-color: #7289da; color: #ffffff; border-radius: 5px; padding: 5px;")
        btn_submit.clicked.connect(self.accept)
        layout.addWidget(btn_submit)
        self.setLayout(layout)

    # Заполнение поля выбора комплектующих
    def populate_components(self):
        conn = sqlite3.connect('components.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM components")
        components = cursor.fetchall()
        conn.close()

        for component_id, name in components:
            self.component_input.addItem(f"{name} (ID: {component_id})", component_id)

    # Установка выбранной комплектующей
    def set_selected_component(self, component_id):
        index = self.component_input.findData(component_id)
        if index >= 0:
            self.component_input.setCurrentIndex(index)

    # Заполнение поля выбора сотрудников
    def populate_employees(self):
        conn = sqlite3.connect('components.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, full_name FROM employees")
        employees = cursor.fetchall()
        conn.close()

        for employee_id, full_name in employees:
            self.employee_input.addItem(f"{full_name} (ID: {employee_id})", employee_id)

    # Установка выбранного сотрудника
    def set_selected_employee(self, employee_id):
        index = self.employee_input.findData(employee_id)
        if index >= 0:
            self.employee_input.setCurrentIndex(index)

    # Получение данных из формы заявки
    def get_data(self):
        selected_type = self.type_input.currentText()
        selected_component_id = self.component_input.currentData()
        selected_employee_id = self.employee_input.currentData()
        selected_status = "Выполнено" if self.is_admin and self.status_checkbox.isChecked() else "Не выполнено"
        return selected_type, selected_component_id, selected_employee_id, selected_status


class SearchDialog(BaseDialog):
    def __init__(self, title="Поиск"):
        super().__init__(title=title)
        layout = QVBoxLayout()
        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("Введите ключевое слово")
        self.input_field.setStyleSheet("background-color: #23272a; color: #ffffff; border-radius: 5px; padding: 5px;")

        btn_submit = QPushButton("Найти", self)
        btn_submit.setStyleSheet("background-color: #7289da; color: #ffffff; border-radius: 5px; padding: 5px;")
        btn_submit.clicked.connect(self.accept)

        layout.addWidget(self.input_field)
        layout.addWidget(btn_submit)
        self.setLayout(layout)

    def get_input(self):
        return self.input_field.text()

class MainWindow(QMainWindow):
    def __init__(self, is_user=False):
        super().__init__()
        self.is_user = is_user
        self.setWindowTitle("Управление комплектующими и заявками для МФУ")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon('icon.png'))

        font = QFont("Arial", 14)
        self.setFont(font)
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#2c2f33"))
        palette.setColor(QPalette.WindowText, QColor("#ffffff"))
        self.setPalette(palette)
        self.init_ui()

    def init_ui(self):
        self.create_toolbar()
        self.create_content_area()
        self.create_exit_button()

    def create_toolbar(self):
        toolbar = QToolBar("Основные действия")
        toolbar.setStyleSheet("background-color: #23272a; color: #ffffff; padding: 10px;")
        self.addToolBar(toolbar)

        menu_style = """
            QMenu {
                background-color: #2c2f33;
                border: 1px solid #40444b;
                color: #ffffff;
                padding: 5px;
            }
            QMenu::item {
                padding: 5px 20px;
                background-color: transparent;
            }
            QMenu::item:selected {
                background-color: #7289da;
                color: #ffffff;
            }
        """

        if not self.is_user:
            menu_button = QMenu("Комплектующие", self)
            menu_button.setStyleSheet(menu_style)
            menu_button.addAction("Добавить комплектующую", self.add_component)
            menu_button.addAction("Удалить комплектующую", self.delete_component)
            menu_button.addAction("Поиск комплектующей", self.search_component)
            menu_button.addAction("Сбросить поиск комплектующей", self.load_components_to_table)
            toolbar.addAction(menu_button.menuAction())

            employees_menu = QMenu("Сотрудники", self)
            employees_menu.setStyleSheet(menu_style)
            employees_menu.addAction("Добавить сотрудника", self.add_employee)
            employees_menu.addAction("Удалить сотрудника", self.delete_employee)
            employees_menu.addAction("Поиск сотрудника", self.search_employee)
            employees_menu.addAction("Сбросить поиск сотрудников", self.load_employees_to_table)
            toolbar.addAction(employees_menu.menuAction())

        requests_menu = QMenu("Заявки", self)
        requests_menu.setStyleSheet(menu_style)
        requests_menu.addAction("Добавить заявку", self.add_request)
        requests_menu.addAction("Удалить заявку", self.delete_request)
        requests_menu.addAction("Поиск заявки", self.search_request)
        requests_menu.addAction("Сбросить поиск заявки", self.load_requests_to_table)
        toolbar.addAction(requests_menu.menuAction())

        if not self.is_user:
            logs_action = QAction("Просмотр логов", self)
            logs_action.triggered.connect(self.view_logs)
            toolbar.addAction(logs_action)

            report_action = QAction("Сгенерировать отчет", self)
            report_action.triggered.connect(self.generate_report)
            toolbar.addAction(report_action)

        toolbar.setIconSize(QSize(24, 24))

    def create_content_area(self):
        self.central_widget = QWidget(self)
        layout = QVBoxLayout(self.central_widget)

        self.tabs = QTabWidget(self)
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #40444b; }
            QTabBar::tab {
                background: #2c2f33;
                color: #ffffff;
                padding: 10px;
                border: 1px solid #40444b;
                border-radius: 5px;
                font-size: 14px;
                min-width: 150px;
            }
            QTabBar::tab:selected {
                background: #7289da;
                color: #ffffff;
            }
            QTabBar::tab:hover {
                background: #3c3f41;
            }
        """)

        if not self.is_user:
            self.components_tab = QWidget()
            self.components_layout = QVBoxLayout(self.components_tab)
            self.components_table = QTableWidget(self)
            self.components_table.setColumnCount(4)
            self.components_table.setHorizontalHeaderLabels(["ID", "Наименование", "Модель", "Количество"])

            # Additional styling for the components table
            self.components_table.setStyleSheet("background-color: #23272a; color: #ffffff; font-size: 14px; padding: 5px;")
            self.components_table.horizontalHeader().setStyleSheet("""
                QHeaderView::section {
                    background-color: #40444b;
                    color: #ffffff;
                    padding: 4px;
                    border: 1px solid #2c2f33;
                    font-size: 14px;
                    font-weight: bold;
                }
            """)
            self.components_table.verticalHeader().setStyleSheet("""
                QHeaderView::section {
                    background-color: #2c2f33;
                    color: #ffffff;
                }
            """)
            self.components_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.components_table.cellDoubleClicked.connect(self.edit_component)
            self.components_layout.addWidget(self.components_table)
            self.tabs.addTab(self.components_tab, "Комплектующие")
            self.load_components_to_table()

        # Add the Employees tab only for administrators
        if not self.is_user:
            self.employees_tab = QWidget()
            self.employees_layout = QVBoxLayout(self.employees_tab)
            self.employees_table = QTableWidget(self)
            self.employees_table.setColumnCount(3)
            self.employees_table.setHorizontalHeaderLabels(["ID", "ФИО", "Отдел"])

            # Styling for the employees table
            self.employees_table.setStyleSheet("background-color: #23272a; color: #ffffff; font-size: 14px; padding: 5px;")
            self.employees_table.horizontalHeader().setStyleSheet("""
                QHeaderView::section {
                    background-color: #40444b;
                    color: #ffffff;
                    padding: 4px;
                    border: 1px solid #2c2f33;
                    font-size: 14px;
                    font-weight: bold;
                }
            """)
            self.employees_table.verticalHeader().setStyleSheet("""
                QHeaderView::section {
                    background-color: #2c2f33;
                    color: #ffffff;
                }
            """)
            self.employees_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.employees_table.cellDoubleClicked.connect(self.edit_employee)
            self.employees_layout.addWidget(self.employees_table)
            self.tabs.addTab(self.employees_tab, "Сотрудники")
            self.load_employees_to_table()

        self.requests_tab = QWidget()
        self.requests_layout = QVBoxLayout(self.requests_tab)
        self.requests_table = QTableWidget(self)
        self.requests_table.setColumnCount(5)
        self.requests_table.setHorizontalHeaderLabels(["ID", "Тип", "Комплектующая", "Сотрудник", "Статус"])
        self.requests_table.setStyleSheet("background-color: #23272a; color: #ffffff; font-size: 14px; padding: 5px;")
        self.requests_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #40444b;
                color: #ffffff;
                padding: 4px;
                border: 1px solid #2c2f33;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        self.requests_table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #2c2f33;
                color: #ffffff;
            }
        """)
        self.requests_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.requests_table.cellDoubleClicked.connect(self.edit_request)
        self.requests_layout.addWidget(self.requests_table)
        self.tabs.addTab(self.requests_tab, "Заявки")
        self.load_requests_to_table()

        # Add the Archived Requests tab only for administrators
        if not self.is_user:
            self.archived_requests_tab = QWidget()
            self.archived_requests_layout = QVBoxLayout(self.archived_requests_tab)
            self.archived_requests_table = QTableWidget(self)
            self.archived_requests_table.setColumnCount(5)
            self.archived_requests_table.setHorizontalHeaderLabels(["ID", "Тип", "Комплектующая", "Сотрудник", "Статус"])
            self.archived_requests_table.setStyleSheet("background-color: #23272a; color: #ffffff; font-size: 14px; padding: 5px;")
            self.archived_requests_table.horizontalHeader().setStyleSheet("""
                QHeaderView::section {
                    background-color: #40444b;
                    color: #ffffff;
                    padding: 4px;
                    border: 1px solid #2c2f33;
                    font-size: 14px;
                    font-weight: bold;
                }
            """)
            self.archived_requests_table.verticalHeader().setStyleSheet("""
                QHeaderView::section {
                    background-color: #2c2f33;
                    color: #ffffff;
                }
            """)
            self.archived_requests_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.archived_requests_layout.addWidget(self.archived_requests_table)
            self.tabs.addTab(self.archived_requests_tab, "Архив заявок")
            self.load_archived_requests_to_table()

        layout.addWidget(self.tabs)
        self.setCentralWidget(self.central_widget)


    def show_instruction(self):
        instruction_dialog = InstructionDialog()
        instruction_dialog.exec_()

        
    def create_exit_button(self):
        # Create the 'Exit' button
        btn_exit = QPushButton("Выход", self)
        btn_exit.setStyleSheet("background-color: #c41e3a; color: white; border-radius: 5px; padding: 10px;")
        btn_exit.clicked.connect(self.handle_exit)

        # Create the 'Refresh Tables' button
        btn_refresh = QPushButton("Обновить таблицы", self)
        btn_refresh.setStyleSheet("background-color: #7289da; color: white; border-radius: 5px; padding: 10px;")
        btn_refresh.clicked.connect(self.refresh_tables)

        # Кнопка "Инструкция"
        btn_instruction = QPushButton("Инструкция", self)
        btn_instruction.setStyleSheet("background-color: #4caf50; color: white; border-radius: 5px; padding: 10px;")
        btn_instruction.clicked.connect(self.show_instruction)

        # Добавление кнопок в статус-бар
        self.statusBar().addPermanentWidget(btn_refresh)
        self.statusBar().addPermanentWidget(btn_instruction)
        self.statusBar().addPermanentWidget(btn_exit)
    
    def refresh_tables(self):
        # Reload data in all tables
        if not self.is_user:
            self.load_components_to_table()
            self.load_employees_to_table()
        self.load_requests_to_table()
        self.load_archived_requests_to_table()

    def handle_exit(self):
        self.close()
        login_dialog = LoginDialog()
        if login_dialog.exec_() == QDialog.Accepted:
            is_user = login_dialog.login_input.text() != "admin"
            self.__init__(is_user)
            self.show()

    def load_components_to_table(self):
        conn = sqlite3.connect('components.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM components")
        rows = cursor.fetchall()
        self.components_table.setRowCount(0)
        for row in rows:
            row_position = self.components_table.rowCount()
            self.components_table.insertRow(row_position)
            for column, item in enumerate(row):
                self.components_table.setItem(row_position, column, QTableWidgetItem(str(item)))
        conn.close()

    def load_employees_to_table(self):
        conn = sqlite3.connect('components.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees")
        rows = cursor.fetchall()
        self.employees_table.setRowCount(0)
        for row in rows:
            row_position = self.employees_table.rowCount()
            self.employees_table.insertRow(row_position)
            for column, item in enumerate(row):
                self.employees_table.setItem(row_position, column, QTableWidgetItem(str(item)))
        conn.close()

    def load_requests_to_table(self):
        conn = sqlite3.connect('components.db')
        cursor = conn.cursor()
        cursor.execute("SELECT requests.id, requests.type, components.name, employees.full_name, requests.status "
                       "FROM requests JOIN components ON requests.component_id = components.id "
                       "JOIN employees ON requests.employee_id = employees.id")
        rows = cursor.fetchall()
        self.requests_table.setRowCount(0)
        for row in rows:
            row_position = self.requests_table.rowCount()
            self.requests_table.insertRow(row_position)
            for column, item in enumerate(row):
                self.requests_table.setItem(row_position, column, QTableWidgetItem(str(item)))
        conn.close()

    def load_archived_requests_to_table(self):
        conn = sqlite3.connect('components.db')
        cursor = conn.cursor()
        cursor.execute("SELECT archived_requests.id, archived_requests.type, components.name, employees.full_name, archived_requests.status "
                       "FROM archived_requests JOIN components ON archived_requests.component_id = components.id "
                       "JOIN employees ON archived_requests.employee_id = employees.id")
        rows = cursor.fetchall()
        self.archived_requests_table.setRowCount(0)
        for row in rows:
            row_position = self.archived_requests_table.rowCount()
            self.archived_requests_table.insertRow(row_position)
            for column, item in enumerate(row):
                self.archived_requests_table.setItem(row_position, column, QTableWidgetItem(str(item)))
        conn.close()

    def add_component(self):
        dialog = ComponentDialog()
        if dialog.exec_() == QDialog.Accepted:
            name, model, quantity = dialog.get_data()
            conn = sqlite3.connect('components.db')
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(id) FROM components")
            max_id = cursor.fetchone()[0]
            next_id = (max_id or 0) + 1
            cursor.execute("INSERT INTO components (id, name, model, quantity) VALUES (?, ?, ?, ?)",
                           (next_id, name, model, quantity))
            conn.commit()
            conn.close()
            self.load_components_to_table()

    def edit_component(self, row):
        component_id = int(self.components_table.item(row, 0).text())
        name = self.components_table.item(row, 1).text()
        model = self.components_table.item(row, 2).text()
        quantity = int(self.components_table.item(row, 3).text())

        dialog = ComponentDialog(name, model, quantity)
        if dialog.exec_() == QDialog.Accepted:
            new_name, new_model, new_quantity = dialog.get_data()
            conn = sqlite3.connect('components.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE components SET name=?, model=?, quantity=? WHERE id=?", 
                           (new_name, new_model, new_quantity, component_id))
            conn.commit()
            conn.close()
            self.load_components_to_table()

    def delete_component(self):
        row = self.components_table.currentRow()
        if row != -1:
            component_id = int(self.components_table.item(row, 0).text())
            conn = sqlite3.connect('components.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM components WHERE id=?", (component_id,))
            conn.commit()
            conn.close()
            update_ids('components')
            self.load_components_to_table()

    def search_component(self):
        dialog = SearchDialog("Поиск комплектующей")
        if dialog.exec_() == QDialog.Accepted:
            keyword = dialog.get_input()
            if keyword:
                conn = sqlite3.connect('components.db')
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM components WHERE name LIKE ? OR model LIKE ?", 
                               (f'%{keyword}%', f'%{keyword}%'))
                rows = cursor.fetchall()
                self.components_table.setRowCount(0)
                for row in rows:
                    row_position = self.components_table.rowCount()
                    self.components_table.insertRow(row_position)
                    for column, item in enumerate(row):
                        self.components_table.setItem(row_position, column, QTableWidgetItem(str(item)))
                conn.close()

    def add_employee(self):
        dialog = EmployeeDialog()
        if dialog.exec_() == QDialog.Accepted:
            full_name, department = dialog.get_data()
            conn = sqlite3.connect('components.db')
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(id) FROM employees")
            max_id = cursor.fetchone()[0]
            next_id = (max_id or 0) + 1
            cursor.execute("INSERT INTO employees (id, full_name, department) VALUES (?, ?, ?)",
                           (next_id, full_name, department))
            conn.commit()
            conn.close()
            self.load_employees_to_table()

    def edit_employee(self, row):
        employee_id = int(self.employees_table.item(row, 0).text())
        full_name = self.employees_table.item(row, 1).text()
        department = self.employees_table.item(row, 2).text()

        dialog = EmployeeDialog(full_name, department)
        if dialog.exec_() == QDialog.Accepted:
            new_full_name, new_department = dialog.get_data()
            conn = sqlite3.connect('components.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE employees SET full_name=?, department=? WHERE id=?", 
                           (new_full_name, new_department, employee_id))
            conn.commit()
            conn.close()
            self.load_employees_to_table()

    def delete_employee(self):
        row = self.employees_table.currentRow()
        if row != -1:
            employee_id = int(self.employees_table.item(row, 0).text())
            conn = sqlite3.connect('components.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM employees WHERE id=?", (employee_id,))
            conn.commit()
            conn.close()
            update_ids('employees')
            self.load_employees_to_table()


    def search_employee(self):
        dialog = SearchDialog("Поиск сотрудника")
        if dialog.exec_() == QDialog.Accepted:
            keyword = dialog.get_input()
            if keyword:
                conn = sqlite3.connect('components.db')
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM employees WHERE full_name LIKE ? OR department LIKE ?", 
                               (f'%{keyword}%', f'%{keyword}%'))
                rows = cursor.fetchall()
                self.employees_table.setRowCount(0)
                for row in rows:
                    row_position = self.employees_table.rowCount()
                    self.employees_table.insertRow(row_position)
                    for column, item in enumerate(row):
                        self.employees_table.setItem(row_position, column, QTableWidgetItem(str(item)))
                conn.close()

    # Метод для добавления новой заявки
    def add_request(self):
        dialog = RequestDialog(is_admin=not self.is_user)
        if dialog.exec_() == QDialog.Accepted:
            type_, component_id, employee_id, status = dialog.get_data()
            conn = sqlite3.connect('components.db')
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(id) FROM requests")
            max_id = cursor.fetchone()[0]
            next_id = (max_id or 0) + 1
            cursor.execute("INSERT INTO requests (id, type, component_id, employee_id, status) VALUES (?, ?, ?, ?, ?)",
                           (next_id, type_, component_id, employee_id, status))
            conn.commit()
            conn.close()
            self.load_requests_to_table()

    # Метод для редактирования существующей заявки
    def edit_request(self, row):
        request_id = int(self.requests_table.item(row, 0).text())
        type_ = self.requests_table.item(row, 1).text()
        component_name = self.requests_table.item(row, 2).text()
        employee_name = self.requests_table.item(row, 3).text()
        status = self.requests_table.item(row, 4).text()

        conn = sqlite3.connect('components.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM components WHERE name=?", (component_name,))
        component_id = cursor.fetchone()[0]
        cursor.execute("SELECT id FROM employees WHERE full_name=?", (employee_name,))
        employee_id = cursor.fetchone()[0]
        conn.close()

        dialog = RequestDialog(type_, component_id, employee_id, status, is_admin=not self.is_user)
        if dialog.exec_() == QDialog.Accepted:
            new_type, new_component_id, new_employee_id, new_status = dialog.get_data()
            conn = sqlite3.connect('components.db')
            cursor = conn.cursor()
            cursor.execute("SELECT quantity FROM components WHERE id=?", (new_component_id,))
            current_quantity = cursor.fetchone()[0]

            # Проверка и обновление статуса заявки
            if status != "Выполнено" and new_status == "Выполнено":
                if new_type in ["Списание", "Замена"]:
                    if current_quantity > 0:
                        cursor.execute("UPDATE components SET quantity = quantity - 1 WHERE id=?", (new_component_id,))
                    else:
                        QMessageBox.warning(self, "Ошибка", "Недостаточно комплектующих для выполнения списания или замены")
                        return
                elif new_type == "Получение":
                    cursor.execute("UPDATE components SET quantity = quantity - 1 WHERE id=?", (new_component_id,))

                cursor.execute("INSERT INTO archived_requests (type, component_id, employee_id, status) VALUES (?, ?, ?, ?)",
                               (new_type, new_component_id, new_employee_id, "Выполнено"))
                cursor.execute("DELETE FROM requests WHERE id=?", (request_id,))
            else:
                cursor.execute("UPDATE requests SET type=?, component_id=?, employee_id=?, status=? WHERE id=?",
                               (new_type, new_component_id, new_employee_id, new_status, request_id))

            cursor.execute("INSERT INTO request_logs (request_id, action) VALUES (?, ?)", 
                           (request_id, f"Статус изменен на {new_status}"))
            conn.commit()
            conn.close()
            self.load_requests_to_table()
            self.load_archived_requests_to_table()


    def delete_request(self):
        row = self.requests_table.currentRow()
        if row != -1:
            request_id = int(self.requests_table.item(row, 0).text())
            conn = sqlite3.connect('components.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM requests WHERE id=?", (request_id,))
            conn.commit()
            conn.close()
            update_ids('requests')
            self.load_requests_to_table()

    def load_components_to_table(self):
        conn = sqlite3.connect('components.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM components")
        rows = cursor.fetchall()
        self.components_table.setRowCount(0)
        for row in rows:
            row_position = self.components_table.rowCount()
            self.components_table.insertRow(row_position)
            for column, item in enumerate(row):
                self.components_table.setItem(row_position, column, QTableWidgetItem(str(item)))
        conn.close()

    def load_employees_to_table(self):
        conn = sqlite3.connect('components.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees")
        rows = cursor.fetchall()
        self.employees_table.setRowCount(0)
        for row in rows:
            row_position = self.employees_table.rowCount()
            self.employees_table.insertRow(row_position)
            for column, item in enumerate(row):
                self.employees_table.setItem(row_position, column, QTableWidgetItem(str(item)))
        conn.close()

    def load_requests_to_table(self):
        conn = sqlite3.connect('components.db')
        cursor = conn.cursor()
        cursor.execute("SELECT requests.id, requests.type, components.name, employees.full_name, requests.status "
                       "FROM requests JOIN components ON requests.component_id = components.id "
                       "JOIN employees ON requests.employee_id = employees.id")
        rows = cursor.fetchall()
        self.requests_table.setRowCount(0)
        for row in rows:
            row_position = self.requests_table.rowCount()
            self.requests_table.insertRow(row_position)
            for column, item in enumerate(row):
                self.requests_table.setItem(row_position, column, QTableWidgetItem(str(item)))
        conn.close()

    def search_request(self):
        dialog = SearchDialog("Поиск заявки")
        if dialog.exec_() == QDialog.Accepted:
            keyword = dialog.get_input()
            if keyword:
                conn = sqlite3.connect('components.db')
                cursor = conn.cursor()
                cursor.execute("SELECT requests.id, requests.type, components.name, employees.full_name, requests.status "
                               "FROM requests JOIN components ON requests.component_id = components.id "
                               "JOIN employees ON requests.employee_id = employees.id "
                               "WHERE requests.type LIKE ? OR employees.full_name LIKE ?", 
                               (f'%{keyword}%', f'%{keyword}%'))
                rows = cursor.fetchall()
                self.requests_table.setRowCount(0)
                for row in rows:
                    row_position = self.requests_table.rowCount()
                    self.requests_table.insertRow(row_position)
                    for column, item in enumerate(row):
                        self.requests_table.setItem(row_position, column, QTableWidgetItem(str(item)))
                conn.close()

    def view_logs(self):
        try:
            # Подключение к базе данных
            conn = sqlite3.connect('components.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM request_logs ORDER BY timestamp DESC")  # Сортировка по дате
            logs = cursor.fetchall()
            conn.close()

            # Создание диалогового окна
            log_dialog = QDialog(self)
            log_dialog.setWindowTitle("Просмотр логов")
            log_dialog.setFixedSize(1000, 600)
            log_dialog.setStyleSheet("background-color: #2c2f33; color: #ffffff;")

            layout = QVBoxLayout(log_dialog)

            # Таблица для отображения логов
            log_table = QTableWidget()
            log_table.setColumnCount(5)  # Добавляем столбцы для нового формата
            log_table.setHorizontalHeaderLabels(["ID", "Событие", "Логин", "Действие", "Дата"])
            log_table.setStyleSheet("""
                QTableWidget {
                    background-color: #23272a;
                    border-radius: 5px;
                    gridline-color: #40444b;
                }
                QHeaderView::section {
                    background-color: #2c2f33;
                    color: #ffffff;
                    padding: 5px;
                    border: 1px solid #40444b;
                }
            """)
            log_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            log_table.horizontalHeader().setStretchLastSection(True)

            # Заполнение таблицы данными
            log_table.setRowCount(len(logs))
            for row_index, log in enumerate(logs):
                for col_index, item in enumerate(log):
                    table_item = QTableWidgetItem(str(item))
                    table_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    table_item.setToolTip(str(item))  # Всплывающая подсказка при наведении
                    log_table.setItem(row_index, col_index, table_item)

            layout.addWidget(log_table)
            log_dialog.setLayout(layout)
            log_dialog.exec_()
        except Exception as e:
            print(f"Ошибка при загрузке логов: {e}")

    def generate_report(self):
        try:
            conn = sqlite3.connect('components.db')
            df_requests = pd.read_sql_query("SELECT * FROM requests", conn)
            df_components = pd.read_sql_query("SELECT * FROM components", conn)
            df_logs = pd.read_sql_query("SELECT * FROM request_logs", conn)
            df_archived_requests = pd.read_sql_query("SELECT * FROM archived_requests", conn)
            df_employees = pd.read_sql_query("SELECT * FROM employees", conn)
            conn.close()

            # Проверка на пустые таблицы
            if df_requests.empty and df_components.empty and df_logs.empty and df_archived_requests.empty and df_employees.empty:
                QMessageBox.warning(self, "Предупреждение", "База данных пуста. Нет данных для экспорта.")
                return

            # Открываем диалог для выбора файла
            file_dialog = QFileDialog.getSaveFileName(self, "Сохранить отчет", "", "Excel Files (*.xlsx)")

            # Проверяем, был ли выбран файл
            if not file_dialog[0]:
                QMessageBox.warning(self, "Ошибка", "Не выбран путь для сохранения отчета.")
                return

            # Записываем данные в Excel
            with pd.ExcelWriter(file_dialog[0], engine='openpyxl') as writer:
                df_requests.to_excel(writer, sheet_name='Заявки', index=False)
                df_components.to_excel(writer, sheet_name='Комплектующие', index=False)
                df_employees.to_excel(writer, sheet_name='Сотрудники', index=False)
                df_logs.to_excel(writer, sheet_name='Логи изменений', index=False)
                df_archived_requests.to_excel(writer, sheet_name='Архив заявок', index=False)

            QMessageBox.information(self, "Отчет", "Отчет успешно сгенерирован!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при генерации отчета: {str(e)}")

if __name__ == "__main__":
    check_db_existence()
    init_db()
    app = QApplication(sys.argv)

    login_dialog = LoginDialog()
    if login_dialog.exec_() == QDialog.Accepted:
        is_user = login_dialog.login_input.text() != "admin"
        main_window = MainWindow(is_user=is_user)
        main_window.show()
        sys.exit(app.exec_())
