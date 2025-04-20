import sys
import subprocess
import importlib.util
import re
import os
import configparser
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QAction, 
                             QFileDialog, QMessageBox, QVBoxLayout, QWidget, 
                             QHBoxLayout, QPushButton)
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont

# Функция для проверки и установки библиотек
def install_library(package_name):
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        print(f"{package_name} не найден, устанавливаем...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            print(f"{package_name} успешно установлен.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при установке {package_name}: {e}")
            return False
    return True

# Установка PyQt5
def install_pyqt5():
    return install_library('PyQt5')

install_pyqt5()

# Класс для подсветки синтаксиса Python
class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)

        self.highlightingRules = []

        # Форматы для подсветки
        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground(QColor("#ffffff"))
        keywordFormat.setFontWeight(QFont.Bold)

        stringFormat = QTextCharFormat()
        stringFormat.setForeground(QColor("#98fb98"))

        commentFormat = QTextCharFormat()
        commentFormat.setForeground(QColor("#808080"))

        numberFormat = QTextCharFormat()
        numberFormat.setForeground(QColor("#87ceeb"))

        operatorFormat = QTextCharFormat()
        operatorFormat.setForeground(QColor("#ffa500"))

        # Ключевые слова Python
        keywords = [
            'and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del', 'elif', 
            'else', 'except', 'False', 'finally', 'for', 'from', 'global', 'if', 
            'import', 'in', 'is', 'lambda', 'None', 'nonlocal', 'not', 'or', 'pass', 
            'raise', 'return', 'True', 'try', 'while', 'with', 'yield'
        ]
        for word in keywords:
            pattern = QRegExp(f"\\b{word}\\b")
            self.highlightingRules.append((pattern, keywordFormat))

        # Числа
        self.highlightingRules.append((QRegExp("\\b[0-9]+\\b"), numberFormat))

        # Строки
        self.highlightingRules.append((QRegExp("\".*\""), stringFormat))
        self.highlightingRules.append((QRegExp("'.*'"), stringFormat))

        # Комментарии
        self.highlightingRules.append((QRegExp("#[^\n]*"), commentFormat))

        # Операторы
        operators = ['\\+', '-', '\\*', '/', '//', '%', '\\*\\*', '=', '==', '!=', 
                     '<', '>', '<=', '>=', '&', '\\|', '^', '~', '<<', '>>']
        for op in operators:
            pattern = QRegExp(op)
            self.highlightingRules.append((pattern, operatorFormat))

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

class Notepad(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_dir = r"C:\notepad"
        self.config_file = os.path.join(self.config_dir, "config.ini")
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Linux-Style Notepad')
        self.setGeometry(100, 100, 800, 600)

        # Создание папки для конфигурации
        self.setupConfigDir()

        # Центральный виджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        # Текстовое поле и кнопка запуска
        self.textEdit = QTextEdit()
        self.highlighter = PythonHighlighter(self.textEdit.document())
        self.main_layout.addWidget(self.textEdit)

        self.run_button = QPushButton('Запустить код')
        self.run_button.setFixedWidth(150)
        self.run_button.clicked.connect(self.runCode)
        self.main_layout.addWidget(self.run_button, alignment=Qt.AlignRight)

        # Настройка меню
        self.setupMenu()

        # Применение стилей
        self.applyStyles()

        # Переменная для отслеживания текущего файла
        self.current_file = None

        # Загрузка последнего файла
        self.loadLastFile()

    def setupConfigDir(self):
        try:
            os.makedirs(self.config_dir, exist_ok=True)
        except Exception as e:
            print(f"Не удалось создать папку {self.config_dir}: {e}")

    def saveLastFile(self):
        if self.current_file:
            config = configparser.ConfigParser()
            config['Settings'] = {'last_file': self.current_file}
            try:
                with open(self.config_file, 'w', encoding='utf-8') as configfile:
                    config.write(configfile)
            except Exception as e:
                print(f"Не удалось сохранить конфигурацию: {e}")

    def loadLastFile(self):
        config = configparser.ConfigParser()
        try:
            if os.path.exists(self.config_file):
                config.read(self.config_file)
                last_file = config.get('Settings', 'last_file', fallback=None)
                if last_file and os.path.exists(last_file):
                    with open(last_file, 'r', encoding='utf-8') as file:
                        self.textEdit.setText(file.read())
                    self.current_file = last_file
        except Exception as e:
            print(f"Не удалось загрузить последний файл: {e}")

    def setupMenu(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('Файл')

        newAction = QAction('Новый', self)
        newAction.setShortcut('Ctrl+N')
        newAction.triggered.connect(self.newFile)
        fileMenu.addAction(newAction)

        openAction = QAction('Открыть', self)
        openAction.setShortcut('Ctrl+O')
        openAction.triggered.connect(self.openFile)
        fileMenu.addAction(openAction)

        saveAction = QAction('Сохранить', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.triggered.connect(self.saveFile)
        fileMenu.addAction(saveAction)

        saveAsAction = QAction('Сохранить как...', self)
        saveAsAction.triggered.connect(self.saveFileAs)
        fileMenu.addAction(saveAsAction)

        fileMenu.addSeparator()

        exitAction = QAction('Выход', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(exitAction)

    def applyStyles(self):
        style = """
        QMainWindow {
            background-color: #2e2e2e;
        }
        QMenuBar {
            background-color: #3c3f41;
            color: #ffffff;
            font-size: 13px;
        }
        QMenuBar::item {
            background-color: #3c3f41;
            padding: 4px 8px;
        }
        QMenuBar::item:selected {
            background-color: #5294e2;
        }
        QMenu {
            background-color: #3c3f41;
            color: #ffffff;
            border: 1px solid #555;
        }
        QMenu::item {
            padding: 4px 16px;
        }
        QMenu::item:selected {
            background-color: #5294e2;
        }
        QTextEdit {
            background-color: #272822;
            color: #f8f8f2;
            border: 1px solid #555;
            font-family: 'Monospace';
            font-size: 14px;
        }
        QScrollBar:vertical {
            border: none;
            background: #3c3f41;
            width: 12px;
            margin: 0px 0px 0px 0px;
        }
        QScrollBar::handle:vertical {
            background: #cccccc;
            min-height: 20px;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            background: none;
            height: 0px;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }
        QPushButton {
            background-color: #5294e2;
            color: #ffffff;
            border: none;
            padding: 4px;
            font-size: 12px;
        }
        QPushButton:hover {
            background-color: #62a4f2;
        }
        """
        self.setStyleSheet(style)

    def newFile(self):
        if self.textEdit.toPlainText():
            reply = QMessageBox.question(self, 'Новый файл',
                                        'Сохранить изменения перед созданием нового файла?',
                                        QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                self.saveFile()
            elif reply == QMessageBox.Cancel:
                return
        self.textEdit.clear()
        self.current_file = None
        self.saveLastFile()

    def openFile(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Открыть файл', '',
                                               'Python файлы (*.py);;Текстовые файлы (*.txt);;Все файлы (*.*)')
        if fname:
            try:
                with open(fname, 'r', encoding='utf-8') as file:
                    self.textEdit.setText(file.read())
                self.current_file = fname
                self.saveLastFile()
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Не удалось открыть файл: {e}')

    def saveFile(self):
        if self.current_file:
            try:
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(self.textEdit.toPlainText())
                self.saveLastFile()
                return True
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Не удалось сохранить файл: {e}')
                return False
        else:
            return self.saveFileAs()

    def saveFileAs(self):
        fname, _ = QFileDialog.getSaveFileName(self, 'Сохранить как', '',
                                               'Python файлы (*.py);;Текстовые файлы (*.txt);;Все файлы (*.*)')
        if fname:
            self.current_file = fname
            self.saveLastFile()
            return self.saveFile()
        return False

    def extract_imports(self, code):
        imports = set()
        pattern = r'^\s*(?:import|from)\s+([a-zA-Z0-9_]+)'
        for line in code.split('\n'):
            match = re.match(pattern, line)
            if match:
                imports.add(match.group(1))
        return imports

    def runCode(self):
        if not self.current_file:
            reply = QMessageBox.question(self, 'Сохранение', 
                                        'Сохранить файл перед выполнением?',
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                if not self.saveFileAs():
                    return
            else:
                return

        if not self.current_file.endswith('.py'):
            QMessageBox.warning(self, 'Ошибка', 'Файл должен быть .py для выполнения!')
            return

        code = self.textEdit.toPlainText()
        imports = self.extract_imports(code)
        for module in imports:
            if module.lower() not in ('sys', 'os', 'math', 'random', 'datetime', 'time', 'json', 're'):
                if not install_library(module):
                    QMessageBox.critical(self, 'Ошибка', f'Не удалось установить библиотеку {module}')
                    return

        try:
            result = subprocess.run([sys.executable, self.current_file], 
                                   capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"Код выполнен успешно! Вывод:\n{result.stdout}")
            else:
                QMessageBox.critical(self, 'Ошибка выполнения', f'Ошибка в коде:\n{result.stderr}')
        except subprocess.TimeoutExpired:
            QMessageBox.critical(self, 'Ошибка', 'Программа превысила время выполнения (10 секунд).')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось выполнить код: {e}')

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        ex = Notepad()
        ex.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        sys.exit(1)