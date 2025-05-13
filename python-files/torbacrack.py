import sys
import requests
import os
from datetime import datetime, timedelta
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QTextEdit, QSizePolicy, QMessageBox, QDialog, QVBoxLayout as DialogLayout, QLineEdit as DialogLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QIcon, QPalette
import appdirs
import tempfile
import logging
logging.basicConfig(filename='debug.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
ALLOWED_PASSWORDS = {'X8@kM5$dZrD', 'K5&nW2@zCvT', 'G8@qN2#LvR', 'G2$tP8@MfG', 'zX@3mC9!VrP', 'T7$pW2#FdC', 'bV$9sN4@KxB', 'bC@7mL2$WfZ', 'Y9#pW5&LrJ', 'wT$2cH7&MvW', 'vT$7cH5!FxG', 'X3@nF9!TqE', 'Y7&vP5@TdN', 'Z7#vT9@xQw', 'dM!7xN3$QvH', 'L6%qY3@wNsF', 'hJ$8mC5@VrD', 'jP@9rK2#VmH', 'xC!5mL7@QbJ', 'S9#pV4$GwK', 'gD#2nJ9&PeE', 'L6%qY3@wNsF', 'S9#pV4$GwK', 'bC@3mF7$TfK', 'tR#6yP8*JmA', 'nF#8wL2$KqO', 'vQ!9rK4@ZmB', 'S9#pV4$GwK', 'L6%qY3@wNsF', 'S9#pV4$GwK', 'kS!3mF9&PxS', 'dL$8vQ3!ZmU', 'S9#pV4$GwK', 'qM$6xN3!JhM', 'X3@nF9!TqE', 'dM!7xN3$QvH', 'L6%qY3@wNsF', 'Y8#pV9&DtY', 'K5&nW2@zCvT', 'S9#pV4$GwK', 'L6%qY3@wNsF', 'mF$8pX3!Lq', 'K5&nW2@zCvT', 'G2$tP8@MfG', 'L6%qY3@wNsF', 'W3$nF8&DtI', 'pQ!3wL7#TfY', 'hJ$5pW7&TfQ', 'dL$8vQ3!ZmU', 'Y8#pV9&DtY'}
TEMP_DIR = tempfile.gettempdir()
APP_NAME = 'TorbaSearch crack by kunteinyr'
ACTIVATION_FILE = os.path.join(TEMP_DIR, f'{APP_NAME}_activation.txt')

def check_activation():
    """Проверяет активацию программы и срок действия."""
    logging.debug(f'Checking activation file at: {ACTIVATION_FILE}')
    if not os.path.exists(ACTIVATION_FILE):
        logging.debug('Activation file does not exist.')
        return False  # Требуется активация
    try:
        with open(ACTIVATION_FILE, 'r') as file:
            lines = file.readlines()
            if len(lines) < 2:
                logging.debug('Activation file is incomplete.')
                return False
            activation_date_str = lines[0].strip()
            activation_date = datetime.strptime(activation_date_str, '%Y-%m-%d %H:%M:%S')
            password = lines[1].strip()
            if datetime.now() > activation_date + timedelta(days=30):
                logging.debug('Activation has expired.')
                return False
            logging.debug('Activation is valid.')
            return True
    except Exception as e:
        logging.error(f'Error reading activation file: {e}')
        return False

def activate_program(password):
    """Активирует программу с паролем."""
    if password in ALLOWED_PASSWORDS:
        try:
            with open(ACTIVATION_FILE, 'w') as file:
                file.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n')
                file.write(password + '\n')
                ALLOWED_PASSWORDS.remove(password)
                logging.debug(f'Program activated with password: {password}')
                return True
        except Exception as e:
            logging.error(f'Error writing to activation file: {e}')
            return False
    else:
        logging.debug(f'Incorrect password: {password}')
        return False
        

class ActivationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Активация программы')
        self.setGeometry(300, 300, 400, 150)
        layout = DialogLayout()
        label = QLabel('Введите пароль для активации:', self)
        label.setFont(QFont('Arial', 12))
        label.setStyleSheet('color: white;')
        layout.addWidget(label)
        self.password_input = DialogLineEdit(self)
        self.password_input.setPlaceholderText('Пароль')
        self.password_input.setStyleSheet('\n            QLineEdit {\n                border: 2px solid #b5332a;\n                padding: 10px;\n                background-color: #0a0808;\n                color: red;\n                border-radius: 10px;\n            }\n        ')
        layout.addWidget(self.password_input)
        self.submit_button = QPushButton('Активировать', self)
        self.submit_button.setStyleSheet('\n            QPushButton {\n                border: 2px solid red;\n                background-color: #808080;\n                color: red;\n                padding: 5px;\n                margin: 0px;\n                min-width: 100%;\n                height: 30px;\n                border-radius: 5px;\n            }\n            QPushButton:hover {\n                background-color: #A9A9A9; \n            }\n        ')
        self.submit_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.submit_button.clicked.connect(self.accept)
        layout.addWidget(self.submit_button)
        self.setLayout(layout)

    def get_password(self):
        return self.password_input.text().strip()

class SearchApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Zlo proverai')
        self.setGeometry(100, 100, 800, 600)
        if not check_activation():
            self.show_activation_dialog()
        else:  # inserted
            self.setStyleSheet('background-color: #2e2e2e; ')
            self.central_widget = QWidget()
            self.setCentralWidget(self.central_widget)
            main_layout = QVBoxLayout()
            title_label = QLabel('Torba Search', self)
            title_label.setFont(QFont('Arial', 24, QFont.Weight.Bold))
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setStyleSheet('color: red;')
            main_layout.addWidget(title_label)
            self.input_field = QLineEdit()
            self.input_field.setPlaceholderText('Введите запрос ( имя, возраст, город, email):')
            self.input_field.setStyleSheet('\n            QLineEdit {\n                border:  2px solid #b5332a;\n                padding: 10px;\n                background-color: #0a0808;\n                color: red;\n                border-radius: 10px;\n                width:  100%;\n            }\n        ')
            main_layout.addWidget(self.input_field)
            self.search_button = QPushButton('искать')
            self.search_button.setStyleSheet('\n            QPushButton {\n                border: 2px solid red;\n                background-color: #808080;\n                color: red;\n                padding: 5px;\n                margin: 0px;\n                min-width: 100%;\n                height: 30px;\n                border-radius: 5px;\n            }\n            QPushButton:hover  {\n                background-color: #A9A9A9;\n            } \n        ')
            self.search_button.clicked.connect(self.perform_search)
            main_layout.addWidget(self.search_button)
            self.result_output = QTextEdit()
            self.result_output.setReadOnly(True)
            self.result_output.setStyleSheet('\n            QTextEdit {\n                border: 2px solid red;\n                padding: 10px;\n                background-color: #0a0808;\n                color: red;\n                border-radius: 10px;\n                font-family: Arial;\n                font-size: 12px;\n            }\n        ')
            main_layout.addWidget(self.result_output)
            self.temp_email_button = QPushButton('Получить временную почту (временно не работает)')
            self.temp_email_button.setStyleSheet('\n            QPushButton {\n                border: 2px solid red;\n                background-color: #808080;\n                color: red;\n                padding: 5px;\n                margin: 0px;\n                min-width: 100%;\n                height: 30px;\n                border-radius: 5px;\n            }\n            QPushButton:hover {\n                background-color: #A9A9A9;\n            }\n        ')
            self.temp_email_button.clicked.connect(self.get_temp_email)
            main_layout.addWidget(self.temp_email_button)
            self.ip_info_button = QPushButton('Получить информацию по IP')
            self.ip_info_button.setStyleSheet('\n            QPushButton {\n                border: 2px solid red;\n                background-color: #808080;\n                color: red;\n                padding: 5px;\n                margin: 0px;\n                min-width: 100%;\n                height: 30px;\n                border-radius: 5px;\n            }\n            QPushButton:hover {\n                background-color: #A9A9A9;\n            }\n        ')
            self.ip_info_button.clicked.connect(self.get_ip_info)
            main_layout.addWidget(self.ip_info_button)
            self.central_widget.setLayout(main_layout)

    def perform_search(self):
        request_text = self.input_field.text().strip()
        if not request_text:
            QMessageBox.warning(self, 'Ошибка', 'Введите запрос перед отправкой.')
            return
        token = '7942240361:p3veULoP'
        data = {'token': token, 'request': request_text, 'lang': 'ru', 'limit': 100}
        url = 'https://leakosintapi.com/'
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                results = response.json()
                self.result_output.setPlainText(f'Результаты: {results}')
            else:  # inserted
                self.result_output.setPlainText(f'Ошибка запроса: {response.status_code} - {response.text}')
        except requests.exceptions.RequestException as e:
            self.result_output.setPlainText(f'Ошибка сети: {e}')
            return None

    def show_activation_dialog(self):
    dialog = ActivationDialog()
    if dialog.exec() == QDialog.DialogCode.Accepted:
        entered_password = dialog.get_password()
        if activate_program(entered_password):
            QMessageBox.information(self, 'Успех', 'Программа успешно активирована.')
            self.setup_ui()
            self.show()  # Добавьте эту строку
        else:
            QMessageBox.critical(self, 'Ошибка', 'Неверный пароль. Программа будет закрыта.')
            sys.exit()
    else:
        sys.exit()

    def deactivate_program(self):
        """Деактивирует программу после истечения времени."""  # inserted
        os.remove(ACTIVATION_FILE) if os.path.exists(ACTIVATION_FILE) else None
        QMessageBox.critical(self, 'Истечение времени', 'Время активации истекло. Введите новый пароль для продолжения.')
        sys.exit()

    def setup_ui(self):
        """Настройка пользовательского интерфейса после успешной активации."""  # inserted
        self.setStyleSheet('background-color: #2e2e2e;')
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout()
        title_label = QLabel('TorbaSearch CRACK', self)
        title_label.setFont(QFont('Arial', 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet('color: red;')
        main_layout.addWidget(title_label)
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText('Введите запрос (имя, возраст, город, email):')
        self.input_field.setStyleSheet('\n            QLineEdit {\n                border: 2px solid #b5332a;\n                padding: 10px;\n                background-color: #0a0808;\n                color: red;\n                border-radius: 10px;\n                width: 100%;\n            }\n        ')
        main_layout.addWidget(self.input_field)
        self.search_button = QPushButton('искать')
        self.search_button.setStyleSheet('\n            QPushButton {\n                border: 2px solid red;\n                background-color: #808080;\n                color: red;\n                padding: 5px;\n                margin: 0px;\n                min-width: 100%;\n                height: 30px;\n                border-radius: 5px;\n            }\n            QPushButton:hover {\n                background-color: #A9A9A9;\n            }\n        ')
        self.search_button.clicked.connect(self.perform_search)
        main_layout.addWidget(self.search_button)
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setStyleSheet('\n            QTextEdit {\n                border: 2px solid red;\n                padding: 10px;\n                background-color: #0a0808;\n                color: red;\n                border-radius: 10px;\n                font-family: Arial;\n                font-size: 12px;\n            }\n        ')
        main_layout.addWidget(self.result_output)
        self.temp_email_button = QPushButton('Получить временную почту')
        self.temp_email_button.setStyleSheet('\n            QPushButton {\n                border: 2px solid red;\n                background-color: #808080;\n                color: red;\n                padding: 5px;\n                margin: 0px;\n                min-width: 100%;\n                height: 30px;\n                border-radius: 5px;\n            }\n            QPushButton:hover {\n                background-color: #A9A9A9;\n            }\n        ')
        self.temp_email_button.clicked.connect(self.get_temp_email)
        main_layout.addWidget(self.temp_email_button)
        self.ip_info_button = QPushButton('Получить информацию по IP')
        self.ip_info_button.setStyleSheet('\n            QPushButton {\n                border: 2px solid red;\n                background-color: #808080;\n                color: red;\n                padding: 5px;\n                margin: 0px;\n                min-width: 100%;\n                height: 30px;\n                border-radius: 5px;\n            }\n            QPushButton:hover {\n                background-color: #A9A9A9;\n            }\n        ')
        self.ip_info_button.clicked.connect(self.get_ip_info)
        main_layout.addWidget(self.ip_info_button)
        self.central_widget.setLayout(main_layout)

    def get_temp_email(self):
        """Получает временную электронную почту."""  # inserted
        try:
            response = requests.get('https://www.1secmail.com/api/v1/?action=genRandomMailbox')
            if response.status_code == 200:
                email_list = response.json()
                if email_list:
                    email = email_list[0]
                    self.result_output.setPlainText(f'Временная почта: {email}')
                else:  # inserted
                    self.result_output.setPlainText('Не удалось получить временную почту.')
        except requests.exceptions.RequestException as e:
            self.result_output.setPlainText(f'Ошибка запроса: {response.status_code} - {response.text}')
            self.result_output.setPlainText(f'Ошибка сети: {e}')

    def get_ip_info(self):
        """Получает информацию по IP-адресу."""  # inserted
        try:
            ip = self.input_field.text().strip()
            if not ip:
                QMessageBox.warning(self, 'Ошибка', 'Введите IP-адрес перед отправкой.')
                return
            response = requests.get(f'https://ipinfo.io/{ip}/json')
            if response.status_code == 200:
                ip_info = response.json()
                info_text = f'IP-адрес: {ip}\n'
                for key, value in ip_info.items():
                    info_text += f'{key}: {value}\n'
                self.result_output.setPlainText(info_text)
        except requests.exceptions.RequestException as e:
            self.result_output.setPlainText(f'Ошибка запроса: {response.status_code} - {response.text}')
            self.result_output.setPlainText(f'Ошибка сети: {e}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SearchApp()
    if check_activation():
        window.show()
    else:
        window.show_activation_dialog()
        if check_activation():  # Проверяем, прошла ли активация
            window.show()
    sys.exit(app.exec())