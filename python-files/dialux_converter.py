import sys
import os
import shutil
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QFileDialog, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt


class DialuxConverterApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DIALux EVO Converter")
        self.setFixedSize(450, 250)
        self.setStyleSheet("background-color: #f0f0f0;")

        self.file_path = ""

        # Fonts
        title_font = QFont("Segoe UI", 11, QFont.Bold)
        normal_font = QFont("Segoe UI", 10)

        # Title label
        self.label = QLabel("🔍 Выберите .evo файл для конвертации:")
        self.label.setFont(title_font)
        self.label.setAlignment(Qt.AlignCenter)

        # File path label
        self.label_path = QLabel("")
        self.label_path.setFont(normal_font)
        self.label_path.setStyleSheet("color: #333333;")
        self.label_path.setWordWrap(True)
        self.label_path.setAlignment(Qt.AlignCenter)

        # Select button
        self.button_select = QPushButton("📂 Выбрать файл")
        self.button_select.setFont(normal_font)
        self.button_select.setCursor(Qt.PointingHandCursor)
        self.button_select.setStyleSheet("background-color: #3498db; color: white; padding: 8px; border-radius: 6px;")
        self.button_select.setToolTip("Открыть диалог выбора .evo файла")
        self.button_select.clicked.connect(self.select_file)

        # Convert button
        self.button_convert = QPushButton("⚙️ Конвертировать")
        self.button_convert.setFont(normal_font)
        self.button_convert.setCursor(Qt.PointingHandCursor)
        self.button_convert.setStyleSheet("background-color: #2ecc71; color: white; padding: 8px; border-radius: 6px;")
        self.button_convert.setToolTip("Сконвертировать файл и сохранить на рабочий стол")
        self.button_convert.clicked.connect(self.convert_file)

        # Status label
        self.label_status = QLabel("")
        self.label_status.setFont(normal_font)
        self.label_status.setAlignment(Qt.AlignCenter)
        self.label_status.setWordWrap(True)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.label_path)
        layout.addSpacerItem(QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))
        layout.addWidget(self.button_select)
        layout.addWidget(self.button_convert)
        layout.addWidget(self.label_status)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 20, 30, 20)

        self.setLayout(layout)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл .evo", "", "DIALux EVO файлы (*.evo)")
        if file_path:
            self.file_path = file_path
            filename = os.path.basename(file_path)
            self.label_path.setText(f"✅ Файл выбран: {filename}")
            self.label_status.setText("")

    def convert_file(self):
        if not self.file_path:
            self.label_status.setText("⚠️ Сначала выберите файл!")
            return

        try:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            filename = os.path.basename(self.file_path).replace(".evo", "_converted.evo")
            new_file = os.path.join(desktop, filename)

            shutil.copy(self.file_path, new_file)
            self.label_status.setStyleSheet("color: green;")
            self.label_status.setText(f"🎉 Успешно!\nФайл сохранён на рабочем столе:\n{filename}")
        except Exception as e:
            self.label_status.setStyleSheet("color: red;")
            self.label_status.setText(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon())  # можно добавить иконку здесь
    window = DialuxConverterApp()
    window.show()
    sys.exit(app.exec_())
